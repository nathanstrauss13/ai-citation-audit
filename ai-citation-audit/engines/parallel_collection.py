"""
Parallel Data Collection Engine - Runs platforms concurrently.

This is an optimized version of CollectionEngine that runs all 5 platforms
in parallel for each query, providing ~5x speedup.

Usage:
    from engines.parallel_collection import ParallelCollectionEngine

    engine = ParallelCollectionEngine(db)
    stats = engine.run_collection(study_id)
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Load .env
try:
    from dotenv import load_dotenv
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform
from platforms.meta import MetaPlatform

from schema.database import Database
from engines.collection_engine import ResponseParser, CollectionTask, CollectionResult

logger = logging.getLogger(__name__)


class ParallelCollectionEngine:
    """
    Parallel collection engine - runs all platforms concurrently for each query.

    Strategy:
    - For each query, spawn 5 threads (one per platform)
    - Wait for all to complete before next query
    - This respects rate limits while maximizing throughput

    Speedup: ~5x compared to sequential (from ~15 min to ~3 min for 30 queries)
    """

    PLATFORMS = ["chatgpt", "claude", "perplexity", "gemini", "meta_llama"]

    # Delay between queries (not between platforms)
    QUERY_DELAY = 1.5  # seconds between query batches

    def __init__(self, db: Database):
        """Initialize the parallel collection engine."""
        self.db = db
        self.adapters: Dict[str, Any] = {}
        self.adapter_errors: Dict[str, str] = {}

        self._initialize_adapters()

    def _initialize_adapters(self):
        """Initialize platform adapters."""
        adapter_classes = {
            "chatgpt": ChatGPTPlatform,
            "claude": ClaudePlatform,
            "perplexity": PerplexityPlatform,
            "gemini": GeminiPlatform,
            "meta_llama": MetaPlatform,
        }

        for platform, adapter_class in adapter_classes.items():
            try:
                self.adapters[platform] = adapter_class()
                logger.info(f"Initialized {platform} adapter")
            except Exception as e:
                self.adapter_errors[platform] = str(e)
                logger.warning(f"Failed to initialize {platform}: {e}")

    def _collect_single_platform(
        self,
        query_text: str,
        platform: str,
        parser: ResponseParser,
        owned_domains: List[str]
    ) -> CollectionResult:
        """Collect from a single platform (runs in thread)."""
        adapter = self.adapters.get(platform)
        if not adapter:
            return CollectionResult(
                query_id="",
                platform=platform,
                success=False,
                error_message=f"Adapter not initialized: {platform}"
            )

        try:
            # Call the platform
            response = adapter.query(query_text)

            # Extract text and citations
            if isinstance(response, dict):
                response_text = response.get('text', response.get('content', str(response)))
                citations = response.get('citations', [])
                search_enabled = "web" if citations else "unknown"
            else:
                response_text = str(response)
                citations = []
                search_enabled = "unknown"

            # Parse response for brand info
            parsed = parser.parse_response(response_text)

            # Process citations
            processed_citations = []
            for cite in citations:
                if isinstance(cite, dict):
                    url = cite.get('url', cite.get('source', ''))
                elif isinstance(cite, str):
                    url = cite
                else:
                    continue

                if url:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]

                    processed_citations.append({
                        'url': url,
                        'domain': domain,
                        'title': cite.get('title', '') if isinstance(cite, dict) else ''
                    })

            return CollectionResult(
                query_id="",  # Will be set by caller
                platform=platform,
                success=True,
                response_text=response_text,
                search_enabled=search_enabled,
                brand_mentioned=parsed.get('brand_mentioned', False),
                brand_prominence=parsed.get('brand_prominence'),
                brand_sentiment=parsed.get('brand_sentiment'),
                featured_brand=parsed.get('featured_brand'),
                all_brands_mentioned=parsed.get('all_brands_mentioned', []),
                competitive_context=parsed.get('competitive_context'),
                citations=processed_citations,
                retry_count=0
            )

        except Exception as e:
            logger.error(f"Error collecting from {platform}: {e}")
            return CollectionResult(
                query_id="",
                platform=platform,
                success=False,
                error_message=str(e),
                retry_count=0
            )

    def _save_result(self, result: CollectionResult, study_id: str, query_id: str):
        """Save a collection result to the database."""
        try:
            response_id = self.db.create_response(
                query_id=query_id,
                study_id=study_id,
                platform=result.platform,
                response_text=result.response_text or "",
                search_enabled=result.search_enabled,
                brand_mentioned=result.brand_mentioned,
                brand_prominence=result.brand_prominence,
                brand_sentiment=result.brand_sentiment,
                featured_brand=result.featured_brand,
                all_brands_mentioned='|'.join(result.all_brands_mentioned or []),
                competitive_context=result.competitive_context
            )

            # Save citations
            if result.citations:
                for cite in result.citations:
                    self.db.create_citation(
                        response_id=response_id,
                        source_url=cite.get('url', ''),
                        source_domain=cite.get('domain', ''),
                        citation_context=cite.get('title', ''),
                        citation_tier=self._classify_citation_tier(cite.get('domain', ''), [])
                    )

        except Exception as e:
            logger.error(f"Error saving result: {e}")

    def _classify_citation_tier(self, domain: str, owned_domains: List[str]) -> str:
        """Classify a citation into tiers."""
        domain_lower = domain.lower()

        for owned in owned_domains:
            if owned.lower() in domain_lower:
                return 'owned'

        editorial = ['forbes.com', 'techcrunch.com', 'gq.com', 'vogue.com', 'wired.com',
                    'businessinsider.com', 'bloomberg.com', 'nytimes.com']
        if any(ed in domain_lower for ed in editorial):
            return 'editorial'

        retail = ['nordstrom.com', 'amazon.com', 'rei.com', 'bestbuy.com',
                 'target.com', 'walmart.com']
        if any(rt in domain_lower for rt in retail):
            return 'retail'

        social = ['reddit.com', 'youtube.com', 'twitter.com', 'instagram.com']
        if any(soc in domain_lower for soc in social):
            return 'social'

        return 'other'

    def run_collection(
        self,
        study_id: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_workers: int = 5
    ) -> Dict[str, Any]:
        """
        Run parallel data collection for a study.

        Args:
            study_id: The study ID to collect data for
            progress_callback: Optional callback(completed, total, message)
            max_workers: Number of parallel threads (default 5, one per platform)

        Returns:
            Dict with collection statistics
        """
        # Get study info
        study = self.db.get_study(study_id)
        if not study:
            raise ValueError(f"Study not found: {study_id}")

        # Get queries
        queries = self.db.get_queries(study_id)
        if not queries:
            raise ValueError(f"No queries found for study: {study_id}")

        # Initialize parser
        parser = ResponseParser(
            brand_name=study.brand_name,
            competitors=study.discovered_competitors
        )

        owned_domains = study.owned_domains or []

        total_queries = len(queries)
        total_tasks = total_queries * len(self.adapters)

        logger.info(f"Starting PARALLEL collection: {total_queries} queries × {len(self.adapters)} platforms = {total_tasks} tasks")
        print(f"\n🚀 Running in PARALLEL mode ({len(self.adapters)} platforms per query)")

        # Update study status
        self.db.update_study_status(study_id, "collecting")

        completed = 0
        failed = 0
        start_time = time.time()

        # Process each query with parallel platform calls
        for q_idx, query in enumerate(queries):
            query_start = time.time()

            if progress_callback:
                progress_callback(
                    completed,
                    total_tasks,
                    f"Query {q_idx+1}/{total_queries}: {query.query_text[:50]}..."
                )

            # Run all platforms in parallel for this query
            results = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self._collect_single_platform,
                        query.query_text,
                        platform,
                        parser,
                        owned_domains
                    ): platform
                    for platform in self.adapters.keys()
                }

                for future in as_completed(futures):
                    platform = futures[future]
                    try:
                        result = future.result()
                        result.query_id = query.id
                        results[platform] = result
                    except Exception as e:
                        logger.error(f"Thread error for {platform}: {e}")
                        results[platform] = CollectionResult(
                            query_id=query.id,
                            platform=platform,
                            success=False,
                            error_message=str(e)
                        )

            # Save all results for this query
            for platform, result in results.items():
                self._save_result(result, study_id, query.id)

                if result.success:
                    completed += 1
                else:
                    failed += 1

            # Progress update
            query_time = time.time() - query_start
            elapsed = time.time() - start_time
            queries_done = q_idx + 1
            avg_per_query = elapsed / queries_done
            eta = avg_per_query * (total_queries - queries_done)

            print(f"  ✓ Query {queries_done}/{total_queries} complete ({query_time:.1f}s) | ETA: {eta:.0f}s remaining")

            # Small delay between queries to avoid burst rate limits
            if q_idx < total_queries - 1:
                time.sleep(self.QUERY_DELAY)

        # Update study status
        self.db.update_study_status(study_id, "collected")

        total_time = time.time() - start_time

        stats = {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_tasks * 100 if total_tasks > 0 else 0,
            "platforms_available": list(self.adapters.keys()),
            "total_time_seconds": total_time,
            "parallel_mode": True,
            "queries_per_second": total_queries / total_time if total_time > 0 else 0
        }

        logger.info(f"Parallel collection complete in {total_time:.1f}s: {completed}/{total_tasks} successful")

        if progress_callback:
            progress_callback(completed, total_tasks, f"Complete! {total_time:.1f}s total")

        return stats


def run_parallel_collection(study_id: str):
    """Convenience function to run parallel collection."""
    db = Database()
    engine = ParallelCollectionEngine(db)
    return engine.run_collection(study_id)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        study_id = sys.argv[1]
        print(f"\n🚀 Running parallel collection for study: {study_id}\n")
        stats = run_parallel_collection(study_id)
        print(f"\n{'='*60}")
        print(f"  PARALLEL COLLECTION COMPLETE")
        print(f"{'='*60}")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Total time: {stats['total_time_seconds']:.1f}s")
        print(f"  Queries/second: {stats['queries_per_second']:.2f}")
    else:
        print("Usage: python parallel_collection.py <study_id>")

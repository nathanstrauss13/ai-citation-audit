"""
Data Collection Engine - Runs queries across LLM platforms.

This engine:
1. Takes queries from database or QuerySet
2. Runs each query across 5 LLM platforms (with RAG enabled)
3. Parses responses for prominence, competitive field, citations
4. Saves to database with checkpointing
5. Supports resume from last checkpoint

Usage:
    from engines import CollectionEngine
    from schema import Database

    db = Database()
    engine = CollectionEngine(db)

    # Run collection for a study
    engine.run_collection(study_id)

    # Or resume from checkpoint
    engine.resume_collection(study_id)
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

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

# Import platform adapters
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform
from platforms.meta import MetaPlatform

from schema.database import Database, Query, Response

logger = logging.getLogger(__name__)


@dataclass
class CollectionTask:
    """A single collection task (query × platform)."""
    query_id: str
    query_text: str
    platform: str


@dataclass
class CollectionResult:
    """Result from a single collection task."""
    query_id: str
    platform: str
    success: bool
    response_text: Optional[str] = None
    search_enabled: str = "unknown"
    brand_mentioned: bool = False
    brand_prominence: Optional[str] = None
    brand_sentiment: Optional[str] = None
    featured_brand: Optional[str] = None
    all_brands_mentioned: List[str] = None
    competitive_context: Optional[str] = None
    citations: List[Dict] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class ResponseParser:
    """Parses LLM responses for brand mentions, prominence, and competitive field."""

    def __init__(self, brand_name: str, competitors: List[str] = None):
        """
        Initialize parser with brand and competitor information.

        Args:
            brand_name: Primary brand to track
            competitors: List of known competitors (optional, for enhanced detection)
        """
        self.brand_name = brand_name
        self.brand_lower = brand_name.lower()
        self.competitors = competitors or []

        # Build brand detection patterns
        self.brand_patterns = self._build_brand_patterns(brand_name)

    def _build_brand_patterns(self, brand: str) -> List[re.Pattern]:
        """Build regex patterns for brand detection."""
        patterns = []
        brand_lower = brand.lower()

        # Exact match with word boundaries
        patterns.append(re.compile(rf'\b{re.escape(brand_lower)}\b', re.IGNORECASE))

        # Handle common variations
        # e.g., "lululemon" -> "lulu lemon", "lululemon athletica"
        if ' ' not in brand_lower:
            # Try splitting camelCase or compound words
            patterns.append(re.compile(rf'\b{re.escape(brand_lower)}\s+\w+\b', re.IGNORECASE))

        return patterns

    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse a response for brand information.

        Returns:
            Dict with: brand_mentioned, brand_prominence, brand_sentiment,
                      featured_brand, all_brands_mentioned, competitive_context
        """
        if not response_text or len(response_text.strip()) < 50:
            return {
                "brand_mentioned": False,
                "brand_prominence": "not_mentioned",
                "brand_sentiment": None,
                "featured_brand": "None",
                "all_brands_mentioned": [],
                "competitive_context": None
            }

        text_lower = response_text.lower()

        # Check if brand is mentioned
        brand_mentioned = self._check_brand_mentioned(text_lower)

        # Classify prominence
        prominence = self._classify_prominence(response_text, text_lower, brand_mentioned)

        # Extract all brands mentioned
        all_brands = self._extract_all_brands(response_text)

        # Determine featured brand (winner)
        featured_brand = self._determine_featured_brand(response_text, all_brands)

        # Extract competitive context
        competitive_context = self._extract_competitive_context(response_text)

        # Assess sentiment (if brand mentioned)
        sentiment = self._assess_sentiment(response_text, text_lower) if brand_mentioned else None

        return {
            "brand_mentioned": brand_mentioned,
            "brand_prominence": prominence,
            "brand_sentiment": sentiment,
            "featured_brand": featured_brand,
            "all_brands_mentioned": all_brands,
            "competitive_context": competitive_context
        }

    def _check_brand_mentioned(self, text_lower: str) -> bool:
        """Check if the primary brand is mentioned."""
        for pattern in self.brand_patterns:
            if pattern.search(text_lower):
                return True
        return False

    def _classify_prominence(self, text: str, text_lower: str, brand_mentioned: bool) -> str:
        """
        Classify brand prominence level.

        Levels:
        - not_mentioned: Brand absent
        - mentioned: Listed among 5+ alternatives
        - listed: Among top 3-5
        - recommended: Explicitly suggested
        - featured_first: #1 or "best overall"
        """
        if not brand_mentioned:
            return "not_mentioned"

        # Check for featured_first indicators
        featured_first_patterns = [
            r'(?:^|\n)\s*(?:1\.|#1|first|top pick)[:\s]+[^.]*' + re.escape(self.brand_lower),
            r'\b' + re.escape(self.brand_lower) + r'\b[^.]*(?:is the best|is my top|stands out as the best|is the gold standard|is the leader|takes the top spot)',
            r'(?:best overall|top choice|my recommendation|highly recommend|number one)[^.]*\b' + re.escape(self.brand_lower) + r'\b',
            r'\b' + re.escape(self.brand_lower) + r'\b[^.]*(?:is the best choice|is my #1|is number one)',
        ]

        for pattern in featured_first_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                return "featured_first"

        # Check for recommended indicators
        recommended_patterns = [
            r'(?:recommend|suggest|consider|try)[^.]*\b' + re.escape(self.brand_lower) + r'\b',
            r'\b' + re.escape(self.brand_lower) + r'\b[^.]*(?:is excellent|is great|is perfect for|is ideal)',
            r'(?:great option|excellent choice|solid pick)[^.]*\b' + re.escape(self.brand_lower) + r'\b',
        ]

        for pattern in recommended_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "recommended"

        # Check position in numbered lists
        list_position = self._get_list_position(text, self.brand_lower)
        if list_position is not None:
            if list_position == 1:
                return "featured_first"
            elif list_position <= 3:
                return "recommended"
            elif list_position <= 5:
                return "listed"
            else:
                return "mentioned"

        # Count total brands to determine if "listed" vs "mentioned"
        all_brands = self._extract_all_brands(text)
        if len(all_brands) >= 5:
            return "mentioned"
        elif len(all_brands) >= 2:
            return "listed"

        return "recommended"  # Mentioned with few alternatives = recommended

    def _get_list_position(self, text: str, brand_lower: str) -> Optional[int]:
        """Get position of brand in a numbered list."""
        # Match numbered list items: "1. Brand", "1) Brand", "1: Brand"
        list_pattern = r'(?:^|\n)\s*(\d+)[.\):\s]+([^\n]+)'
        matches = re.findall(list_pattern, text, re.MULTILINE)

        for num_str, content in matches:
            if brand_lower in content.lower():
                try:
                    return int(num_str)
                except ValueError:
                    pass

        return None

    def _extract_all_brands(self, text: str) -> List[str]:
        """Extract all brand names mentioned in order of appearance."""
        # Start with known competitors
        found_brands = []
        text_lower = text.lower()

        # Check primary brand
        if self._check_brand_mentioned(text_lower):
            found_brands.append(self.brand_name)

        # Check known competitors
        for competitor in self.competitors:
            if competitor.lower() in text_lower:
                if competitor not in found_brands:
                    found_brands.append(competitor)

        # Also try to detect unknown brands using capitalization patterns
        # This is approximate but catches many brand names
        brand_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        potential_brands = re.findall(brand_pattern, text)

        # Filter to likely brand names (exclude common words)
        common_words = {
            'The', 'This', 'That', 'These', 'Those', 'Here', 'There',
            'Best', 'Top', 'Great', 'Good', 'First', 'Second', 'Third',
            'However', 'Therefore', 'Overall', 'Additionally', 'Furthermore',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        }

        for potential in potential_brands:
            if potential not in common_words and potential not in found_brands:
                # Only add if it looks like it could be a brand
                if len(potential) >= 3 and not potential.isupper():
                    found_brands.append(potential)

        return found_brands[:20]  # Limit to prevent noise

    def _determine_featured_brand(self, text: str, all_brands: List[str]) -> str:
        """Determine which brand is featured/recommended as the winner."""
        if not all_brands:
            return "None"

        text_lower = text.lower()

        # Check if response is clearly "no recommendation"
        no_rec_patterns = [
            r'(?:depends on|it depends|varies based on|hard to say)',
            r'(?:all of these|each has|they all have)',
            r'(?:no clear winner|no single best)',
        ]

        for pattern in no_rec_patterns:
            if re.search(pattern, text_lower):
                if len(all_brands) > 1:
                    return "Mixed"

        # Check for explicit winner
        for brand in all_brands:
            brand_lower = brand.lower()

            winner_patterns = [
                r'(?:^|\n)\s*1[.\):\s]+[^.]*\b' + re.escape(brand_lower) + r'\b',
                r'\b' + re.escape(brand_lower) + r'\b[^.]*(?:is the best|is my top|takes the top)',
                r'(?:best overall|top pick|my recommendation)[^.]*\b' + re.escape(brand_lower) + r'\b',
            ]

            for pattern in winner_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                    return brand

        # If only one brand mentioned substantially, it's the featured one
        if len(all_brands) == 1:
            return all_brands[0]

        # If primary brand is in top position
        list_pos = self._get_list_position(text, self.brand_lower)
        if list_pos == 1:
            return self.brand_name

        # Check first mentioned brand in a list context
        for brand in all_brands[:3]:
            if self._get_list_position(text, brand.lower()) == 1:
                return brand

        # Multiple brands, no clear winner
        return "Mixed"

    def _extract_competitive_context(self, text: str) -> Optional[str]:
        """Extract a brief competitive context narrative."""
        # Look for comparison language
        text_lower = text.lower()

        comparison_indicators = [
            'compared to', 'versus', 'vs', 'unlike', 'similar to',
            'better than', 'worse than', 'more than', 'less than',
            'stands out', 'differentiates', 'competitive'
        ]

        for indicator in comparison_indicators:
            if indicator in text_lower:
                # Found comparison language, extract surrounding context
                idx = text_lower.find(indicator)
                start = max(0, idx - 100)
                end = min(len(text), idx + 150)
                snippet = text[start:end].strip()

                # Clean up
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."

                return snippet

        return None

    def _assess_sentiment(self, text: str, text_lower: str) -> str:
        """Assess sentiment toward the brand."""
        # Find sentences containing the brand
        brand_sentences = []
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            if self.brand_lower in sentence.lower():
                brand_sentences.append(sentence)

        if not brand_sentences:
            return "neutral"

        combined = ' '.join(brand_sentences).lower()

        # Enthusiastic indicators
        enthusiastic = ['love', 'amazing', 'excellent', 'outstanding', 'best', 'favorite', 'gold standard']
        if any(word in combined for word in enthusiastic):
            return "enthusiastic"

        # Positive indicators
        positive = ['good', 'great', 'quality', 'recommend', 'nice', 'solid', 'reliable']
        if any(word in combined for word in positive):
            return "positive"

        # Negative indicators
        negative = ['expensive', 'overpriced', 'disappointing', 'poor', 'bad', 'avoid', 'issue', 'problem']
        if any(word in combined for word in negative):
            return "negative"

        return "neutral"


class CollectionEngine:
    """
    Engine that runs data collection across LLM platforms.

    Features:
    - Parallel-ish collection (one platform at a time to respect rate limits)
    - Checkpointing for resume capability
    - Prominence parsing (not just mention detection)
    - Citation extraction and tier classification
    - Progress callbacks for UI integration
    """

    PLATFORMS = ["chatgpt", "claude", "perplexity", "gemini", "meta_llama"]

    # Rate limiting delays (seconds) per platform
    PLATFORM_DELAYS = {
        "chatgpt": 1.0,
        "claude": 1.0,
        "perplexity": 2.0,  # More conservative
        "gemini": 1.0,
        "meta_llama": 0.5,
    }

    def __init__(self, db: Database):
        """Initialize the collection engine."""
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

    def run_collection(
        self,
        study_id: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Run data collection for a study.

        Args:
            study_id: The study ID to collect data for
            progress_callback: Optional callback(completed, total, message)

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

        # Initialize parser with brand info
        parser = ResponseParser(
            brand_name=study.brand_name,
            competitors=study.discovered_competitors
        )

        # Build task list
        tasks = []
        for query in queries:
            for platform in self.PLATFORMS:
                if platform in self.adapters:
                    tasks.append(CollectionTask(
                        query_id=query.id,
                        query_text=query.query_text,
                        platform=platform
                    ))

        total_tasks = len(tasks)
        logger.info(f"Starting collection: {len(queries)} queries × {len(self.adapters)} platforms = {total_tasks} tasks")

        # Create checkpoint
        self.db.create_checkpoint(
            study_id=study_id,
            total_tasks=total_tasks,
            pending_tasks=[{"query_id": t.query_id, "platform": t.platform} for t in tasks]
        )

        # Update study status
        self.db.update_study_status(study_id, "collecting")

        # Run collection
        completed = 0
        failed = 0
        results = []

        for i, task in enumerate(tasks):
            if progress_callback:
                progress_callback(completed, total_tasks, f"Collecting {task.platform} for query {task.query_id[:8]}...")

            result = self._collect_single(task, parser, study.owned_domains)
            results.append(result)

            # Save to database
            self._save_result(result, study_id)

            if result.success:
                completed += 1
            else:
                failed += 1

            # Update checkpoint
            remaining = [{"query_id": t.query_id, "platform": t.platform} for t in tasks[i+1:]]
            self.db.update_checkpoint(
                study_id=study_id,
                completed_tasks=completed,
                failed_tasks=failed,
                last_query_id=task.query_id,
                last_platform=task.platform,
                pending_tasks=remaining
            )

            # Rate limiting
            delay = self.PLATFORM_DELAYS.get(task.platform, 1.0)
            time.sleep(delay)

        # Update study status
        self.db.update_study_status(study_id, "collected")

        # Update query statuses
        for query in queries:
            responses = self.db.get_responses(query.id)
            if len(responses) == len(self.adapters):
                self.db.update_query_status(query.id, "collected")
            elif len(responses) > 0:
                self.db.update_query_status(query.id, "partial")
            else:
                self.db.update_query_status(query.id, "failed")

        stats = {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_tasks * 100 if total_tasks > 0 else 0,
            "platforms_available": list(self.adapters.keys()),
            "platforms_failed": list(self.adapter_errors.keys())
        }

        logger.info(f"Collection complete: {completed}/{total_tasks} successful ({stats['success_rate']:.1f}%)")

        if progress_callback:
            progress_callback(completed, total_tasks, "Collection complete!")

        return stats

    def resume_collection(
        self,
        study_id: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """Resume collection from last checkpoint."""
        checkpoint = self.db.get_checkpoint(study_id)
        if not checkpoint:
            logger.info("No checkpoint found, starting fresh collection")
            return self.run_collection(study_id, progress_callback)

        pending = checkpoint.get("pending_tasks", [])
        if not pending:
            logger.info("No pending tasks, collection already complete")
            return {
                "total_tasks": checkpoint["total_tasks"],
                "completed": checkpoint["completed_tasks"],
                "failed": checkpoint["failed_tasks"],
                "resumed": True
            }

        # Get study for parser
        study = self.db.get_study(study_id)
        parser = ResponseParser(
            brand_name=study.brand_name,
            competitors=study.discovered_competitors
        )

        # Get query texts
        queries = {q.id: q for q in self.db.get_queries(study_id)}

        # Build remaining tasks
        tasks = []
        for task_info in pending:
            query = queries.get(task_info["query_id"])
            if query and task_info["platform"] in self.adapters:
                tasks.append(CollectionTask(
                    query_id=task_info["query_id"],
                    query_text=query.query_text,
                    platform=task_info["platform"]
                ))

        total_tasks = checkpoint["total_tasks"]
        completed = checkpoint["completed_tasks"]
        failed = checkpoint["failed_tasks"]

        logger.info(f"Resuming collection: {len(tasks)} tasks remaining")

        self.db.update_study_status(study_id, "collecting")

        for i, task in enumerate(tasks):
            if progress_callback:
                progress_callback(completed, total_tasks, f"Resuming {task.platform}...")

            result = self._collect_single(task, parser, study.owned_domains)
            self._save_result(result, study_id)

            if result.success:
                completed += 1
            else:
                failed += 1

            remaining = [{"query_id": t.query_id, "platform": t.platform} for t in tasks[i+1:]]
            self.db.update_checkpoint(
                study_id=study_id,
                completed_tasks=completed,
                failed_tasks=failed,
                last_query_id=task.query_id,
                last_platform=task.platform,
                pending_tasks=remaining
            )

            delay = self.PLATFORM_DELAYS.get(task.platform, 1.0)
            time.sleep(delay)

        self.db.update_study_status(study_id, "collected")

        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_tasks * 100 if total_tasks > 0 else 0,
            "resumed": True
        }

    def _collect_single(
        self,
        task: CollectionTask,
        parser: ResponseParser,
        owned_domains: List[str]
    ) -> CollectionResult:
        """Collect a single query from a single platform."""
        adapter = self.adapters.get(task.platform)
        if not adapter:
            return CollectionResult(
                query_id=task.query_id,
                platform=task.platform,
                success=False,
                error_message=f"Adapter not available: {task.platform}"
            )

        max_retries = 2
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # Call the platform
                result = adapter.get_citations(task.query_text)

                response_text = result.get("response", "")
                citations = result.get("citations", [])

                if not response_text or len(response_text.strip()) < 50:
                    last_error = "Empty or too short response"
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    break

                # Parse the response
                parsed = parser.parse_response(response_text)

                # Determine search_enabled status
                search_enabled = "yes" if citations else "partial"
                # Check for indicators of no search
                if "I don't have" in response_text or "my knowledge cutoff" in response_text.lower():
                    search_enabled = "no"

                # Process citations
                processed_citations = []
                for cit in citations:
                    url = cit.get("url", "")
                    domain = cit.get("domain", "") or self._extract_domain(url)

                    # Classify tier
                    tier, influence = self._classify_citation(domain, owned_domains)

                    processed_citations.append({
                        "url": url,
                        "domain": domain,
                        "tier": tier,
                        "influence_potential": influence
                    })

                return CollectionResult(
                    query_id=task.query_id,
                    platform=task.platform,
                    success=True,
                    response_text=response_text,
                    search_enabled=search_enabled,
                    brand_mentioned=parsed["brand_mentioned"],
                    brand_prominence=parsed["brand_prominence"],
                    brand_sentiment=parsed["brand_sentiment"],
                    featured_brand=parsed["featured_brand"],
                    all_brands_mentioned=parsed["all_brands_mentioned"],
                    competitive_context=parsed["competitive_context"],
                    citations=processed_citations,
                    retry_count=attempt
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Collection error ({task.platform}, attempt {attempt+1}): {e}")
                if attempt < max_retries:
                    time.sleep(2 * (attempt + 1))

        return CollectionResult(
            query_id=task.query_id,
            platform=task.platform,
            success=False,
            error_message=last_error,
            retry_count=max_retries
        )

    def _save_result(self, result: CollectionResult, study_id: str):
        """Save a collection result to the database."""
        try:
            # Create response
            response_id = self.db.create_response(
                query_id=result.query_id,
                platform=result.platform,
                raw_text=result.response_text,
                search_enabled=result.search_enabled,
                brand_mentioned=result.brand_mentioned,
                brand_prominence=result.brand_prominence,
                brand_sentiment=result.brand_sentiment,
                featured_brand=result.featured_brand,
                all_brands_mentioned=result.all_brands_mentioned or [],
                competitive_context=result.competitive_context,
                error_message=result.error_message,
                retry_count=result.retry_count
            )

            # Create citations
            if result.citations:
                for cit in result.citations:
                    self.db.create_citation(
                        response_id=response_id,
                        url=cit["url"],
                        domain=cit["domain"],
                        tier=cit.get("tier"),
                        influence_potential=cit.get("influence_potential")
                    )

            logger.debug(f"Saved result: {result.platform} for {result.query_id[:8]}")

        except Exception as e:
            logger.error(f"Error saving result: {e}")
            self.db.log_error(
                error_type="save_error",
                error_message=str(e),
                study_id=study_id,
                query_id=result.query_id,
                platform=result.platform
            )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def _classify_citation(self, domain: str, owned_domains: List[str]) -> Tuple[str, str]:
        """Classify a citation by tier and influence potential."""
        domain_lower = domain.lower()

        # Check owned domains
        for owned in owned_domains:
            if owned.lower() in domain_lower or domain_lower in owned.lower():
                return "owned", "high"

        # Use database classification
        tier, influence = self.db._classify_domain(domain_lower)
        return tier, influence


# =============================================================================
# CLI for testing
# =============================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python collection_engine.py <study_id>")
        print("       python collection_engine.py --resume <study_id>")
        sys.exit(1)

    resume = "--resume" in sys.argv
    study_id = sys.argv[-1]

    db = Database()
    engine = CollectionEngine(db)

    def progress(completed, total, message):
        pct = completed / total * 100 if total > 0 else 0
        print(f"[{completed}/{total}] ({pct:.1f}%) {message}")

    if resume:
        stats = engine.resume_collection(study_id, progress_callback=progress)
    else:
        stats = engine.run_collection(study_id, progress_callback=progress)

    print("\n" + "=" * 50)
    print("Collection Statistics:")
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print("=" * 50)

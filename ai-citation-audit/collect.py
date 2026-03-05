#!/usr/bin/env python3
"""
Unified AI Citation Collector

Queries 5-10 LLM platforms in parallel and produces a clean CSV with
full_output + citation URLs. All analytical inference (brand mentions,
winners, competitors) is deferred to dashboard generation where Claude
can do it more accurately.

Usage:
    # Standard 5-platform run
    python collect.py "Lululemon" -q queries.csv

    # Extended 7-platform run
    python collect.py "Lululemon" -q queries.csv -p 7

    # Inline queries (quick test)
    python collect.py "Lululemon" -q "Best yoga pants,Lululemon vs Athleta"

    # With dashboard generation
    python collect.py "Lululemon" -q queries.csv --dashboard

    # With Citation Explorer (interactive tree)
    python collect.py "Lululemon" -q queries.csv --tree

    # Both dashboard and explorer
    python collect.py "Lululemon" -q queries.csv --dashboard --tree

    # Sequential mode (useful for debugging)
    python collect.py "Lululemon" -q queries.csv --sequential
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("collect")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass

from platforms import (
    load_platforms,
    PLATFORM_CONCURRENCY,
    PLATFORM_DELAYS,
    STANDARD_5,
    EXTENDED_7,
    ALL_10,
)

# ---------------------------------------------------------------------------
# Infrastructure / CDN domains to filter from citation data
# ---------------------------------------------------------------------------
INFRA_DOMAIN_PATTERNS = [
    'vertexaisearch', 'googleusercontent', 'googleapis', 'gstatic',
    'cloudflare', 'cdn.', '.cdn', 'amazonaws', 's3.', 'azure',
    'blob.core', 'storage.', 'static.', 'assets.', 'media.',
    'googleads', 'doubleclick', 'googlesyndication', 'google.com/search',
    'bing.com/search', 'duckduckgo.com', 'search.yahoo',
]


def _is_infra_url(url: str) -> bool:
    url_lower = url.lower()
    return any(pat in url_lower for pat in INFRA_DOMAIN_PATTERNS)


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace('www.', '').lower()
    except Exception:
        return ''


# ---------------------------------------------------------------------------
# Query loading
# ---------------------------------------------------------------------------

def load_queries(source: str) -> List[Dict]:
    """Load queries from CSV, JSON, or inline comma-separated text.

    Expected dict keys: id (or query_id), query, category, query_type.
    Optional keys: persona, intent (for Citation Explorer hierarchy).
    """
    if os.path.isfile(source):
        ext = Path(source).suffix.lower()
        if ext == '.csv':
            rows = []
            with open(source, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    q = {
                        'id': row.get('query_id') or row.get('id') or f'Q{i+1:03d}',
                        'query': row.get('query', ''),
                        'category': row.get('category', 'General'),
                        'query_type': row.get('query_type', 'unbranded'),
                        'is_branded': row.get('query_type', '').lower() == 'branded',
                    }
                    # Pass through optional persona/intent columns
                    if row.get('persona', '').strip():
                        q['persona'] = row['persona'].strip()
                    if row.get('intent', '').strip():
                        q['intent'] = row['intent'].strip()
                    rows.append(q)
            return rows
        elif ext == '.json':
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    item.setdefault('id', item.pop('query_id', f'Q{i+1:03d}'))
                    item.setdefault('category', 'General')
                    item.setdefault('query_type', 'unbranded')
                    item['is_branded'] = item.get('query_type', '').lower() == 'branded'
                return data
        logger.error(f"Unsupported file format: {ext}")
        sys.exit(1)
    else:
        # Inline comma-separated queries
        queries = [q.strip() for q in source.split(',') if q.strip()]
        return [
            {
                'id': f'Q{i+1:03d}',
                'query': q,
                'category': 'General',
                'query_type': 'unbranded',
                'is_branded': False,
            }
            for i, q in enumerate(queries)
        ]


# ---------------------------------------------------------------------------
# Core collection
# ---------------------------------------------------------------------------

def _process_single(query_info: Dict, platform_name: str, adapter) -> Optional[Dict]:
    """Query one platform for one prompt. Returns raw data row or error dict."""
    query_text = query_info['query']
    query_id = query_info['id']
    category = query_info.get('category', 'General')

    try:
        result = adapter.get_citations(query_text)
        response_text = result.get('response', '')
        citations = result.get('citations', [])

        # Structured citation URLs from adapter
        citation_urls = [c.get('url', '') for c in citations if c.get('url')]

        # Also extract inline URLs from response text
        if response_text:
            url_patterns = [
                r'https?://[^\s\)\]\"\'<>]+',
                r'\[(?:www\.[^\]]+)\]',
                r'\((?:www\.[^\)]+)\)',
            ]
            for pattern in url_patterns:
                for match in re.findall(pattern, response_text):
                    clean = match.strip('[]()').strip()
                    if clean.startswith('www.'):
                        clean = 'https://' + clean
                    if clean not in citation_urls and clean.startswith('http'):
                        citation_urls.append(clean)

            # Domain-level attributions ("Source: Forbes.com")
            domain_pattern = (
                r'(?:Source|per|according to|from)\s*[:\-]?\s*'
                r'([A-Za-z0-9\-]+\.(?:com|org|net|edu|gov|co\.uk))'
            )
            for domain in re.findall(domain_pattern, response_text, re.IGNORECASE):
                pseudo = f"https://{domain.lower()}"
                if pseudo not in citation_urls:
                    citation_urls.append(pseudo)

        # Filter infrastructure URLs
        citation_urls = [u for u in citation_urls if not _is_infra_url(u)]

        # Extract unique domains
        citation_domains = []
        for url in citation_urls:
            d = _extract_domain(url)
            if d and d not in citation_domains:
                citation_domains.append(d)

        # Lightweight RAG detection
        has_rag = bool(citations)
        if not has_rag and response_text:
            rag_patterns = [
                r'(?:Source|Sources|Reference|References):\s*[\[\(]?(?:www\.|http)',
                r'(?:Source|Sources|Reference|References):\s*[A-Za-z0-9\-]+\.(?:com|org|net|edu|gov)',
                r'\[(?:www\.|http)[^\]]+\]',
                r'\((?:www\.|http)[^\)]+\)',
                r'according to [A-Z][a-z]+(?:\.com|\.org)',
            ]
            for pat in rag_patterns:
                if re.search(pat, response_text, re.IGNORECASE):
                    has_rag = True
                    break

        row = {
            'query_id': query_id,
            'query': query_text,
            'query_type': 'branded' if query_info.get('is_branded') else 'unbranded',
            'category': category,
            'persona': query_info.get('persona', ''),
            'intent': query_info.get('intent', ''),
            'engine': platform_name,
            'search_enabled': 'Yes' if has_rag else 'No',
            'full_output': response_text,
            'citation_urls': '\n'.join(citation_urls),
            'citation_domains': '\n'.join(citation_domains),
            'timestamp': datetime.now().isoformat(),
        }
        return row

    except Exception as e:
        logger.error(f"Error {platform_name}/{query_id}: {type(e).__name__}: {e}")
        return {'_error': str(e), '_platform': platform_name, '_query_id': query_id}


def collect_citations(
    brand_name: str,
    queries: List[Dict],
    platform_set: str = '5',
    output_dir: str = 'output',
    parallel: bool = True,
    max_workers: int = 30,
    generate_dashboard: bool = False,
    generate_tree: bool = False,
    competitors: Optional[List[str]] = None,
    owned_domains: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Dict[str, Any]:
    """Run a complete citation collection job.

    Args:
        brand_name: Focal brand name
        queries: List of query dicts with 'id', 'query', 'category', 'query_type'
        platform_set: '5' for standard, '7' for extended, or list of names
        output_dir: Directory for CSV and dashboard output
        parallel: Use parallel collection (True) or sequential (False)
        max_workers: Max parallel threads (only used if parallel=True)
        generate_dashboard: Generate HTML dashboard after collection
        generate_tree: Generate Citation Explorer HTML after collection
        competitors: Optional list of competitor brand names (for dashboard)
        owned_domains: Optional list of brand's owned domains (for dashboard)
        progress_callback: Optional callback(pct, message) for UI integration

    Returns:
        Dict with results including csv_path, total_responses, errors, etc.
    """
    results = {
        'brand_name': brand_name,
        'total_queries': len(queries),
        'total_responses': 0,
        'total_citations': 0,
        'csv_path': None,
        'dashboard_path': None,
        'tree_path': None,
        'errors': [],
        'platform_stats': {},
    }

    def update(pct: float, msg: str):
        if progress_callback:
            progress_callback(pct, msg)
        logger.info(f"[{pct:.0f}%] {msg}")

    # ---- Load adapters ----
    update(0, "Loading platform adapters...")
    try:
        adapters = load_platforms(platform_set)
    except RuntimeError as e:
        results['errors'].append(str(e))
        return results

    update(2, f"Loaded {len(adapters)} adapters: {', '.join(adapters.keys())}")

    # ---- Preflight health check ----
    update(3, f"Running preflight health check on {len(adapters)} adapters...")
    preflight_query = "What is the most popular consumer brand?"
    failed = []

    def _preflight(name_adapter):
        name, adapter = name_adapter
        try:
            r = adapter.get_citations(preflight_query)
            text = (r or {}).get('response', '').strip()
            return (name, bool(text), len(text) if text else 0, None)
        except Exception as e:
            return (name, False, 0, str(e))

    completed_futures = set()
    with ThreadPoolExecutor(max_workers=len(adapters)) as pool:
        futures = {pool.submit(_preflight, (n, a)): n for n, a in adapters.items()}
        try:
            for future in as_completed(futures, timeout=25):
                completed_futures.add(future)
                try:
                    name, ok, chars, err = future.result(timeout=5)
                    if ok:
                        logger.info(f"PREFLIGHT OK: {name} ({chars} chars)")
                    else:
                        reason = err or "empty response"
                        logger.warning(f"PREFLIGHT FAIL: {name} - {reason}")
                        failed.append(name)
                except Exception as e:
                    name = futures[future]
                    logger.warning(f"PREFLIGHT ERROR: {name} - {e}")
                    failed.append(name)
        except TimeoutError:
            for future, name in futures.items():
                if future not in completed_futures:
                    logger.warning(f"PREFLIGHT TIMEOUT: {name}")
                    failed.append(name)
                    future.cancel()

    for name in failed:
        del adapters[name]
        results['errors'].append(f"{name}: failed preflight health check")

    if not adapters:
        results['errors'].append("All adapters failed preflight")
        return results

    update(5, f"Preflight passed: {', '.join(adapters.keys())}"
              + (f" (failed: {', '.join(failed)})" if failed else ""))

    # ---- Collection ----
    responses = []
    platform_stats = {name: {'success': 0, 'empty': 0, 'error': 0} for name in adapters}
    MAX_RETRIES = 2

    all_tasks = [
        (qi, pname, adapter)
        for qi in queries
        for pname, adapter in adapters.items()
    ]
    total_tasks = len(all_tasks)

    update(5, f"Starting collection: {len(queries)} queries x {len(adapters)} platforms = {total_tasks} calls...")

    if parallel:
        semaphores = {
            name: threading.Semaphore(PLATFORM_CONCURRENCY.get(name, 3))
            for name in adapters
        }

        def _rate_limited(qi, pname, adapter):
            sem = semaphores[pname]
            last_result = None
            for attempt in range(1 + MAX_RETRIES):
                sem.acquire()
                try:
                    result = _process_single(qi, pname, adapter)
                finally:
                    sem.release()
                if result and result.get('full_output', '').strip():
                    platform_stats[pname]['success'] += 1
                    return result
                last_result = result
                if attempt < MAX_RETRIES:
                    wait = 2 * (attempt + 1)
                    logger.info(f"Retry {attempt+1}/{MAX_RETRIES} {pname}/{qi['id']} in {wait}s...")
                    time.sleep(wait)
            # Exhausted retries
            if last_result and last_result.get('_error'):
                platform_stats[pname]['error'] += 1
            else:
                platform_stats[pname]['empty'] += 1
            return last_result

        workers = min(max_workers, len(adapters) * 5)
        completed = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(_rate_limited, qi, pname, adapter): (qi, pname)
                for qi, pname, adapter in all_tasks
            }
            for future in as_completed(future_map):
                qi, pname = future_map[future]
                completed += 1
                if completed % len(adapters) == 0:
                    pct = 5 + (completed / total_tasks * 80)
                    update(pct, f"Completed {completed}/{total_tasks} API calls...")
                try:
                    result = future.result()
                    if result and result.get('full_output', '').strip():
                        responses.append(result)
                    elif result and result.get('_error'):
                        results['errors'].append(f"{pname}/{qi['id']}: {result['_error']}")
                except Exception as e:
                    platform_stats[pname]['error'] += 1
                    results['errors'].append(f"{pname}/{qi['id']}: {e}")
    else:
        # Sequential mode
        completed = 0
        for qi, pname, adapter in all_tasks:
            delay = PLATFORM_DELAYS.get(pname, 1.0)
            last_result = None
            for attempt in range(1 + MAX_RETRIES):
                result = _process_single(qi, pname, adapter)
                if result and result.get('full_output', '').strip():
                    platform_stats[pname]['success'] += 1
                    responses.append(result)
                    last_result = None
                    break
                last_result = result
                if attempt < MAX_RETRIES:
                    time.sleep(2 * (attempt + 1))
            if last_result:
                if last_result.get('_error'):
                    platform_stats[pname]['error'] += 1
                    results['errors'].append(f"{pname}/{qi['id']}: {last_result['_error']}")
                else:
                    platform_stats[pname]['empty'] += 1
            completed += 1
            if completed % len(adapters) == 0:
                pct = 5 + (completed / total_tasks * 80)
                update(pct, f"Completed {completed}/{total_tasks} API calls...")
            time.sleep(delay)

    # ---- Stats ----
    results['total_responses'] = len(responses)
    results['platform_stats'] = platform_stats
    results['expected_responses'] = total_tasks
    total_cites = sum(
        len([u for u in r.get('citation_urls', '').split('\n') if u.strip()])
        for r in responses
    )
    results['total_citations'] = total_cites

    for name, stats in platform_stats.items():
        total = stats['success'] + stats['empty'] + stats['error']
        logger.info(
            f"  {name}: {stats['success']}/{total} success"
            + (f", {stats['empty']} empty" if stats['empty'] else "")
            + (f", {stats['error']} errors" if stats['error'] else "")
        )

    # ---- Save CSV ----
    update(85, "Saving CSV...")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    brand_slug = re.sub(r'[/\\:*?"<>|]+', '_', brand_name.strip()).upper()
    brand_slug = re.sub(r'\s+', '_', brand_slug)
    brand_slug = re.sub(r'_+', '_', brand_slug).strip('_')
    csv_filename = f"{brand_slug}_CITATIONS_{timestamp}.csv"
    csv_path = Path(output_dir) / csv_filename

    if responses:
        fieldnames = [
            'query_id', 'query', 'query_type', 'category',
            'persona', 'intent', 'engine',
            'search_enabled', 'full_output', 'citation_urls',
            'citation_domains', 'timestamp',
        ]
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL,
                extrasaction='ignore',
            )
            writer.writeheader()
            writer.writerows(responses)
        results['csv_path'] = str(csv_path)
        logger.info(f"Saved {len(responses)} rows to {csv_path}")
    else:
        logger.warning("No responses collected — CSV not written")

    # ---- Dashboard generation (optional) ----
    if generate_dashboard and responses:
        update(90, "Generating dashboard...")
        try:
            from generate_dashboard_from_csv import load_csv_data, analyze_csv_data
            from engines.dashboard_v3 import DashboardEngineV3

            rows = load_csv_data(str(csv_path), brand_name, competitors=competitors or [])
            insights = analyze_csv_data(rows, brand_name)

            # Adaptive citation classification
            classified = None
            try:
                from engines.citation_classifier import classify_citations_adaptive
                comp_names = [c.brand_name for c in insights.discovered_competitors[:15]]
                classified = classify_citations_adaptive(
                    domain_counts=insights.citation_metrics.top_domains,
                    brand_name=brand_name,
                    competitor_names=comp_names,
                    api_key=os.environ.get('ANTHROPIC_API_KEY'),
                )
            except Exception as e:
                logger.warning(f"Citation classification failed: {e}")

            engine = DashboardEngineV3()
            html = engine.generate(insights, query_data=rows, classified_citations=classified)

            brand_lower = re.sub(r'[/\\:*?"<>|]+', '_', brand_name.strip()).lower().replace(' ', '_')
            brand_lower = re.sub(r'_+', '_', brand_lower).strip('_')
            dash_filename = f"{brand_lower}_dashboard_{timestamp}.html"
            dash_path = Path(output_dir) / dash_filename

            with open(dash_path, 'w', encoding='utf-8') as f:
                f.write(html)
            results['dashboard_path'] = str(dash_path)
            logger.info(f"Dashboard saved to {dash_path}")

        except Exception as e:
            import traceback
            logger.error(f"Dashboard generation failed: {e}\n{traceback.format_exc()}")
            results['errors'].append(f"Dashboard: {e}")

    # ---- Citation Explorer / tree generation (optional) ----
    if generate_tree and responses:
        update(95, "Generating Citation Explorer...")
        try:
            from engines.citation_tree_engine import CitationTreeEngine

            # Detect persona/intent columns
            has_persona = any(r.get('persona', '').strip() for r in responses)

            engine = CitationTreeEngine()
            tree_html = engine.generate(responses, brand_name, has_persona=has_persona,
                                        competitors=competitors)

            brand_lower = re.sub(r'[/\\:*?"<>|]+', '_', brand_name.strip()).lower().replace(' ', '_')
            brand_lower = re.sub(r'_+', '_', brand_lower).strip('_')
            tree_filename = f"{brand_lower}_citation_explorer_{timestamp}.html"
            tree_path = Path(output_dir) / tree_filename

            with open(tree_path, 'w', encoding='utf-8') as f:
                f.write(tree_html)
            results['tree_path'] = str(tree_path)
            logger.info(f"Citation Explorer saved to {tree_path}")

        except Exception as e:
            import traceback
            logger.error(f"Citation Explorer generation failed: {e}\n{traceback.format_exc()}")
            results['errors'].append(f"Citation Explorer: {e}")

    update(100, "Collection complete!")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run AI citation audit across LLM platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python collect.py "Lululemon" -q queries.csv
  python collect.py "Lululemon" -q queries.csv -p 7
  python collect.py "Lululemon" -q "Best yoga pants,Lululemon vs Athleta"
  python collect.py "Lululemon" -q queries.csv --dashboard
  python collect.py "Lululemon" -q queries.csv --tree
  python collect.py "Lululemon" -q queries.csv --dashboard --tree
        """,
    )
    parser.add_argument("brand", help="Brand name to audit")
    parser.add_argument(
        "-q", "--queries", required=True,
        help="Path to queries CSV/JSON, or inline comma-separated queries",
    )
    parser.add_argument(
        "-p", "--platforms", default='5', choices=['5', '7', '10', 'all'],
        help="Platform set: 5 (standard), 7 (extended), 10/all (full) [default: 5]",
    )
    parser.add_argument(
        "-o", "--output-dir", default="output",
        help="Output directory for CSV and dashboard [default: output]",
    )
    parser.add_argument(
        "-c", "--competitors", default=None,
        help="Comma-separated competitor names (for dashboard)",
    )
    parser.add_argument(
        "--owned-domains", default=None,
        help="Comma-separated owned domains (for dashboard)",
    )
    parser.add_argument(
        "--dashboard", action="store_true",
        help="Generate HTML dashboard after collection",
    )
    parser.add_argument(
        "--tree", action="store_true",
        help="Generate Citation Explorer (interactive tree) after collection",
    )
    parser.add_argument(
        "--sequential", action="store_true",
        help="Use sequential collection instead of parallel",
    )
    parser.add_argument(
        "--max-workers", type=int, default=30,
        help="Max parallel threads [default: 30]",
    )

    args = parser.parse_args()

    queries = load_queries(args.queries)
    if not queries:
        logger.error("No queries loaded")
        sys.exit(1)

    logger.info(f"Brand: {args.brand}")
    logger.info(f"Queries: {len(queries)}")
    logger.info(f"Platforms: {args.platforms}")

    competitors = [c.strip() for c in args.competitors.split(',')] if args.competitors else None
    owned = [d.strip() for d in args.owned_domains.split(',')] if args.owned_domains else None

    def progress(pct, msg):
        print(f"[{pct:5.1f}%] {msg}")

    result = collect_citations(
        brand_name=args.brand,
        queries=queries,
        platform_set=args.platforms,
        output_dir=args.output_dir,
        parallel=not args.sequential,
        max_workers=args.max_workers,
        generate_dashboard=args.dashboard,
        generate_tree=args.tree,
        competitors=competitors,
        owned_domains=owned,
        progress_callback=progress,
    )

    print("\n" + "=" * 60)
    print(f"COLLECTION COMPLETE: {args.brand}")
    print(f"  Responses: {result['total_responses']}/{result.get('expected_responses', '?')}")
    print(f"  Citations: {result['total_citations']}")
    print(f"  CSV: {result['csv_path'] or 'N/A'}")
    print(f"  Dashboard: {result['dashboard_path'] or 'N/A'}")
    print(f"  Explorer: {result['tree_path'] or 'N/A'}")
    if result['errors']:
        print(f"  Errors: {len(result['errors'])}")
        for err in result['errors'][:5]:
            print(f"    - {err}")
        if len(result['errors']) > 5:
            print(f"    ... and {len(result['errors']) - 5} more")
    print("=" * 60)


if __name__ == "__main__":
    main()

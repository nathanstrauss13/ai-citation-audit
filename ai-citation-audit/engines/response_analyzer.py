#!/usr/bin/env python3
"""
Response Analyzer - Uses Claude to analyze AI platform responses at dashboard time.

Replaces the regex-based heuristics that previously ran during data collection.
Reads `full_output` from each CSV row and produces structured analysis fields:
  - brand_mentioned (bool)
  - prominence (featured_first / recommended / listed / mentioned / not_mentioned)
  - position (int or None)
  - competitors_mentioned (list of strings)
  - featured_brand (string - who "won" the response)
  - sentiment (positive / neutral / negative)
"""

import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fallback: regex-based analysis (used when no API key is available)
# ---------------------------------------------------------------------------

def _analyze_response_regex(
    response_text: str,
    brand_name: str,
    competitors: List[str],
) -> Dict[str, Any]:
    """Regex-based response analysis — fast fallback when Claude is unavailable."""
    brand_lower = brand_name.strip('"\'').strip().lower()
    text_lower = (response_text or '').lower()

    # Brand mentioned?
    brand_mentioned = brand_lower in text_lower if response_text else False

    # Prominence / position
    prominence = 'not_mentioned'
    position = None

    if brand_mentioned:
        # Check for featured/first position
        first_patterns = [
            rf'(?:^|\n)\s*1[.\):\s]+[^.]*\b{re.escape(brand_lower)}\b',
            rf'\b{re.escape(brand_lower)}\b[^.]*(?:is the best|is my top|top pick|best overall)',
        ]
        for pattern in first_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                prominence = 'featured_first'
                position = 1
                break

        if prominence == 'not_mentioned':
            list_pattern = r'(?:^|\n)\s*(\d+)[.\):\s]+([^\n]+)'
            matches = re.findall(list_pattern, response_text or '', re.MULTILINE)
            for num_str, content in matches:
                if brand_lower in content.lower():
                    try:
                        pos = int(num_str)
                        position = pos
                        if pos == 1:
                            prominence = 'featured_first'
                        elif pos <= 3:
                            prominence = 'recommended'
                        elif pos <= 5:
                            prominence = 'listed'
                        else:
                            prominence = 'mentioned'
                        break
                    except ValueError:
                        pass

            if prominence == 'not_mentioned' and brand_mentioned:
                prominence = 'mentioned'

    # Competitors mentioned
    comps_found = []
    if response_text:
        for comp in competitors:
            if comp.lower() in text_lower:
                comps_found.append(comp)

    # Featured brand (who won)
    featured_brand = ''
    if prominence == 'featured_first':
        featured_brand = brand_name
    elif response_text:
        for comp in competitors:
            comp_lower = comp.lower()
            first_match = re.search(r'(?:^|\n)\s*1[.\):\s]+([^\n]+)', response_text, re.MULTILINE)
            if first_match and comp_lower in first_match.group(1).lower():
                featured_brand = comp
                break
            winner_patterns = [
                rf'\b{re.escape(comp_lower)}\b[^.]*(?:is the best|is my top|top pick|best overall)',
                rf'(?:best overall|top pick|my recommendation)[^.]*\b{re.escape(comp_lower)}\b',
            ]
            for pattern in winner_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    featured_brand = comp
                    break
            if featured_brand:
                break

    return {
        'brand_mentioned': brand_mentioned,
        'prominence': prominence,
        'position': position,
        'competitors_mentioned': comps_found,
        'featured_brand': featured_brand,
        'sentiment': 'neutral',
    }


# ---------------------------------------------------------------------------
# Claude-based analysis
# ---------------------------------------------------------------------------

def _build_analysis_prompt(
    responses_batch: List[Dict],
    brand_name: str,
    competitors: List[str],
) -> str:
    """Build a prompt for Claude to analyze a batch of AI platform responses."""
    competitor_str = ', '.join(competitors[:15]) if competitors else 'unknown'

    items = []
    for i, resp in enumerate(responses_batch):
        text = (resp.get('full_output') or '')[:3000]  # cap per-response to fit context
        items.append(f'--- RESPONSE {i} ---\n{text}\n')

    responses_block = '\n'.join(items)

    return f"""Analyze these AI platform responses for brand visibility intelligence.

FOCAL BRAND: {brand_name}
KNOWN COMPETITORS: {competitor_str}

For each response, determine:
1. brand_mentioned: Is "{brand_name}" mentioned by name? (true/false)
2. prominence: One of: featured_first (recommended #1 or "best overall"), recommended (positions 2-3), listed (positions 4-5), mentioned (named but not ranked), not_mentioned
3. position: Numeric rank if the response uses a numbered list, otherwise null
4. competitors_mentioned: Array of competitor brand names found in the response. Include ANY brand that competes in the same category, not just the known competitors list above. Be thorough.
5. featured_brand: Which brand is positioned #1 or "best overall"? Empty string if unclear.
6. sentiment: Tone toward {brand_name} specifically: positive, neutral, or negative. Use "neutral" if brand is not mentioned.

{responses_block}

Return ONLY a JSON array with one object per response, in order. No markdown, no explanation.
Example: [{{"brand_mentioned": true, "prominence": "recommended", "position": 2, "competitors_mentioned": ["Nike", "Adidas"], "featured_brand": "Nike", "sentiment": "positive"}}]"""


def _call_claude_api(prompt: str, api_key: str) -> Optional[str]:
    """Call Claude API and return text response."""
    import httpx

    try:
        response = httpx.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=60.0,
        )
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            logger.warning(f"Claude API returned {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"Claude API call failed: {e}")
        return None


def _analyze_batch_with_claude(
    batch: List[Dict],
    brand_name: str,
    competitors: List[str],
    api_key: str,
) -> List[Dict[str, Any]]:
    """Send a batch of responses to Claude for analysis."""
    prompt = _build_analysis_prompt(batch, brand_name, competitors)
    raw = _call_claude_api(prompt, api_key)

    if not raw:
        # Fallback to regex for this batch
        return [_analyze_response_regex(r.get('full_output', ''), brand_name, competitors) for r in batch]

    # Parse JSON from Claude's response
    try:
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        results = json.loads(text)

        if isinstance(results, list) and len(results) == len(batch):
            return results
        else:
            logger.warning(f"Claude returned {len(results) if isinstance(results, list) else 'non-list'} results for batch of {len(batch)}")
            return [_analyze_response_regex(r.get('full_output', ''), brand_name, competitors) for r in batch]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Claude analysis JSON: {e}")
        return [_analyze_response_regex(r.get('full_output', ''), brand_name, competitors) for r in batch]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_responses(
    rows: List[Dict],
    brand_name: str,
    competitors: List[str],
    api_key: Optional[str] = None,
    batch_size: int = 8,
) -> List[Dict]:
    """
    Analyze AI platform responses and enrich rows with analytical fields.

    Args:
        rows: List of CSV row dicts (must have 'full_output')
        brand_name: Focal brand name
        competitors: Known competitor names
        api_key: Anthropic API key (uses regex fallback if None)
        batch_size: Responses per Claude API call

    Returns:
        Same rows list, enriched with analysis fields mapped to the internal
        schema expected by analyze_csv_data:
          - new_focal_brand_found (bool)
          - new_prominence (str)
          - new_focal_position (int or None)
          - new_brands_mentioned (str, pipe-separated)
          - new_primary_competitor (str)
          - new_sentiment (str)
          - citation_count (int)
    """
    if not rows:
        return rows

    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')

    if api_key:
        logger.info(f"Analyzing {len(rows)} responses with Claude (batch_size={batch_size})...")
        # Split into batches
        batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]
        all_results = []

        # Process batches with limited concurrency
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(_analyze_batch_with_claude, batch, brand_name, competitors, api_key): i
                for i, batch in enumerate(batches)
            }
            batch_results = [None] * len(batches)
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    batch_results[idx] = future.result()
                except Exception as e:
                    logger.warning(f"Batch {idx} failed: {e}, using regex fallback")
                    batch_results[idx] = [
                        _analyze_response_regex(r.get('full_output', ''), brand_name, competitors)
                        for r in batches[idx]
                    ]

            for br in batch_results:
                if br:
                    all_results.extend(br)

        logger.info(f"Claude analysis complete: {len(all_results)} responses analyzed")
    else:
        logger.info(f"No API key — using regex fallback for {len(rows)} responses")
        all_results = [
            _analyze_response_regex(r.get('full_output', ''), brand_name, competitors)
            for r in rows
        ]

    # Enrich rows with analysis results
    for row, analysis in zip(rows, all_results):
        row['new_focal_brand_found'] = analysis.get('brand_mentioned', False)
        row['new_prominence'] = analysis.get('prominence', 'not_mentioned')
        row['new_focal_position'] = analysis.get('position')
        row['new_sentiment'] = analysis.get('sentiment', 'neutral')

        # Competitors
        comps = analysis.get('competitors_mentioned', [])
        if isinstance(comps, list):
            row['new_brands_mentioned'] = '|'.join(comps)
        else:
            row['new_brands_mentioned'] = str(comps)

        # Featured brand → primary competitor
        featured = analysis.get('featured_brand', '')
        if featured and featured.lower() != brand_name.strip('"\'').strip().lower():
            row['new_primary_competitor'] = featured
        else:
            row['new_primary_competitor'] = ''

        # Citation count from URLs (already in CSV)
        if 'citation_count' not in row or not row.get('citation_count'):
            urls = row.get('citation_urls', '')
            if urls:
                if '\n' in urls:
                    row['citation_count'] = len([u for u in urls.split('\n') if u.strip()])
                else:
                    row['citation_count'] = len([u for u in urls.split('|') if u.strip()])
            else:
                row['citation_count'] = 0

    return rows

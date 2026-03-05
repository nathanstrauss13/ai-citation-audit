"""
Adaptive Citation Classifier (Hybrid Rule-Based + LLM)

Classifies citation domains into industry-appropriate categories.
Rule-based pass handles obvious cases (owned, wikipedia, social platforms).
LLM pass classifies ambiguous domains with industry context and determines
adaptive tab labels.

Designed to run at dashboard generation time, not collection time.
"""

import json
import logging
import os
import re
from collections import Counter, OrderedDict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Rule-based constants ──────────────────────────────────────────────

SOCIAL_PLATFORMS = {
    'reddit.com', 'youtube.com', 'instagram.com', 'tiktok.com',
    'twitter.com', 'x.com', 'facebook.com', 'pinterest.com',
    'linkedin.com', 'threads.net', 'mastodon.social', 'bsky.app',
    'quora.com', 'tumblr.com',
}

FORUM_PATTERNS = [
    'forum', 'community', 'discuss', 'boards', 'stackexchange',
    'stackoverflow', 'flyertalk',
]

REFERENCE_DOMAINS = {
    'en.wikipedia.org', 'wikipedia.org',
}

# System/CDN domains to exclude entirely
EXCLUDED_PATTERNS = [
    'vertexaisearch', 'googleusercontent', 'googleapis', 'gstatic',
    'cloudflare', 'cdn.', '.cdn', 'amazonaws', 's3.', 'azure',
    'blob.core', 'storage.', 'static.', 'assets.', 'media.',
    'googleads', 'doubleclick', 'googlesyndication', 'google.com/search',
    'bing.com/search', 'duckduckgo.com', 'search.yahoo',
]

# Government / regulatory
GOV_PATTERNS = ['.gov', '.gov.', 'government']

# Academic / research
ACADEMIC_PATTERNS = ['.edu', 'scholar.google', 'researchgate', 'academia.edu', 'arxiv.org', 'pubmed']


def classify_citations_adaptive(
    domain_counts: List[Tuple[str, int]],
    brand_name: str,
    competitor_names: Optional[List[str]] = None,
    api_key: Optional[str] = None,
) -> Dict[str, List[dict]]:
    """
    Classify citation domains into adaptive, industry-appropriate categories.

    Args:
        domain_counts: List of (domain, count) tuples from citation analysis
        brand_name: The focal brand name
        competitor_names: Optional list of competitor brand names
        api_key: Optional Anthropic API key for LLM classification

    Returns:
        OrderedDict of {category_label: [{"domain": str, "total": int}, ...]}
        Categories are ordered by total citation count (descending).
    """
    if not domain_counts:
        return OrderedDict()

    brand_lower = brand_name.lower().replace(' ', '').replace('-', '')
    competitor_lowers = []
    if competitor_names:
        competitor_lowers = [
            c.lower().replace(' ', '').replace('-', '')
            for c in competitor_names if len(c) >= 3
        ]

    # ── Phase 1: Rule-based pass ──────────────────────────────────────
    owned = []
    competitors = []
    social_community = []
    reference = []
    government = []
    academic = []
    excluded = []
    ambiguous = []  # Sent to LLM in phase 2

    for domain, count in domain_counts:
        d_lower = domain.lower()
        entry = {"domain": domain, "total": count}

        # Skip system/CDN domains
        if any(pat in d_lower for pat in EXCLUDED_PATTERNS):
            excluded.append(entry)
            continue

        # Clean malformed domains (e.g. "bmw.comhttp:" from bad URL parsing)
        if 'http' in d_lower and not d_lower.startswith('http'):
            # Strip trailing http/https artifacts
            clean = re.sub(r'https?:?.*$', '', d_lower)
            d_lower = clean

        # Brand owned
        if brand_lower in d_lower.replace('-', '').replace('.', ''):
            owned.append(entry)
            continue

        # Competitor domains
        if competitor_lowers and any(
            comp in d_lower.replace('-', '').replace('.', '')
            for comp in competitor_lowers
        ):
            competitors.append(entry)
            continue

        # Wikipedia / reference
        if any(ref in d_lower for ref in REFERENCE_DOMAINS) or 'wikipedia' in d_lower:
            reference.append(entry)
            continue

        # Social platforms (exact match on base domain)
        base_domain = d_lower.split('/')[-1] if '/' not in d_lower else d_lower
        if any(social in d_lower for social in SOCIAL_PLATFORMS):
            social_community.append(entry)
            continue

        # Forums / community
        if any(pat in d_lower for pat in FORUM_PATTERNS):
            social_community.append(entry)
            continue

        # Government
        if any(pat in d_lower for pat in GOV_PATTERNS):
            government.append(entry)
            continue

        # Academic
        if any(pat in d_lower for pat in ACADEMIC_PATTERNS):
            academic.append(entry)
            continue

        # Everything else → ambiguous, needs LLM
        ambiguous.append(entry)

    # ── Phase 2: LLM classification of ambiguous domains ──────────────
    llm_categories = {}
    if ambiguous:
        llm_categories = _classify_with_llm(
            ambiguous, brand_name, api_key
        )

    # ── Phase 3: Assemble final categories ────────────────────────────
    # Start with rule-based categories that have entries
    result = OrderedDict()

    if owned:
        result["Brand Owned"] = owned
    if reference:
        result["Reference / Wikipedia"] = reference

    # Merge LLM categories
    if llm_categories:
        for cat_name, entries in llm_categories.items():
            if entries:
                result[cat_name] = entries
    elif ambiguous:
        # No LLM available — use enhanced rule-based fallback
        fallback = _fallback_classify(ambiguous, brand_name)
        for cat_name, entries in fallback.items():
            if entries:
                result[cat_name] = entries

    if social_community:
        result["Social & Community"] = social_community
    if government:
        result["Government & Regulatory"] = government
    if academic:
        result["Academic & Research"] = academic
    if competitors:
        result["Competitor Domains"] = competitors

    # Sort each category's entries by count descending
    for cat in result:
        result[cat].sort(key=lambda x: x['total'], reverse=True)

    # Re-order categories by total citations
    sorted_cats = sorted(
        result.items(),
        key=lambda item: sum(e['total'] for e in item[1]),
        reverse=True
    )

    return OrderedDict(sorted_cats)


def _classify_with_llm(
    ambiguous_entries: List[dict],
    brand_name: str,
    api_key: Optional[str] = None,
) -> Dict[str, List[dict]]:
    """
    Send ambiguous domains to LLM for industry-aware classification.
    Batches domains in groups of ~150 to stay within token limits.
    Returns dict of {category_name: [entries]}.
    """
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logger.info("No API key available — skipping LLM classification")
        return {}

    try:
        import anthropic
    except ImportError:
        logger.warning("anthropic package not installed — skipping LLM classification")
        return {}

    client = anthropic.Anthropic(api_key=api_key)

    # Sort by citation count (most-cited first) and batch
    sorted_entries = sorted(ambiguous_entries, key=lambda x: x['total'], reverse=True)
    BATCH_SIZE = 100
    batches = [sorted_entries[i:i + BATCH_SIZE] for i in range(0, len(sorted_entries), BATCH_SIZE)]

    all_result: Dict[str, List[dict]] = {}
    classified_domains: set = set()

    for batch_idx, batch in enumerate(batches):
        logger.info(f"LLM batch {batch_idx + 1}/{len(batches)}: {len(batch)} domains")

        domain_list = "\n".join(
            f"- {e['domain']} ({e['total']} citations)"
            for e in batch
        )

        # For batch 2+, tell the LLM to reuse existing category names
        existing_cats_instruction = ""
        if batch_idx > 0 and all_result:
            existing_names = list(all_result.keys())
            existing_cats_instruction = f"""
**IMPORTANT — Reuse these existing categories from prior batches:**
{', '.join(f'"{n}"' for n in existing_names)}

You MUST use these exact category names where applicable. Only create a new category if none of the above fit a domain."""

        prompt = f"""You are classifying citation sources from AI platform responses about the brand "{brand_name}".

Below are domains that were cited when AI platforms answered questions about {brand_name}. Classify each domain into the MOST SPECIFIC industry-appropriate category.

**Domains to classify:**
{domain_list}
{existing_cats_instruction}
**Rules:**
1. Create 3-6 category names that are specific to this brand's industry. Examples:
   - For an athletic wear brand: "Fitness & Sports Media", "Fashion & Lifestyle Press", "Outdoor / Running Specialist", "Activewear Brands", "Retail / Marketplace"
   - For an automotive brand: "Automotive Trade Press", "Car Marketplace / Listings", "Consumer Reviews", "Lifestyle / Luxury Media"
   - For a hotel brand: "Travel Publications", "Booking Platforms", "Points & Miles Blogs", "Luxury Lifestyle Media"
2. Category names should be concise (2-4 words) and meaningful to a marketing professional
3. Each domain goes in exactly ONE category
4. Don't create a category with fewer than 2 domains unless there's truly no better fit
5. Don't use generic names like "Other" — be specific about what the sources actually are

Return ONLY valid JSON (no commentary before or after):
{{"categories": {{"Category Name": ["domain1.com", "domain2.com"], "Another Category": ["domain3.com"]}}}}"""

        try:
            max_tokens = min(4096, 500 + len(batch) * 25)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()

            # Strip markdown code fences
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to find JSON object if there's text before/after
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start >= 0 and json_end > json_start:
                content = content[json_start:json_end + 1]

            parsed = json.loads(content)
            categories = parsed.get("categories", parsed)

            # Map domain names back to entry objects
            domain_map = {e['domain'].lower(): e for e in batch}

            for cat_name, domains in categories.items():
                if not isinstance(domains, list):
                    continue
                for d in domains:
                    if not isinstance(d, str):
                        continue
                    d_lower = d.lower().strip()
                    matched = domain_map.get(d_lower)
                    if not matched:
                        for key, entry in domain_map.items():
                            if d_lower in key or key in d_lower:
                                matched = entry
                                break
                    if matched and matched['domain'].lower() not in classified_domains:
                        all_result.setdefault(cat_name, []).append(matched)
                        classified_domains.add(matched['domain'].lower())

            batch_classified = sum(1 for e in batch if e['domain'].lower() in classified_domains)
            logger.info(f"  Batch {batch_idx + 1}: classified {batch_classified}/{len(batch)} domains")

        except json.JSONDecodeError as e:
            logger.warning(f"LLM batch {batch_idx + 1} JSON parse error: {e}")
            # Fall through — unclassified domains will be caught below
        except Exception as e:
            logger.warning(f"LLM batch {batch_idx + 1} failed: {e}")

    # ── Post-process: merge near-duplicate category names ──────────────
    all_result = _merge_similar_categories(all_result)

    # Catch any domains the LLM missed across all batches
    uncategorized = [
        e for e in ambiguous_entries
        if e['domain'].lower() not in classified_domains
    ]
    if uncategorized:
        all_result["Other Sources"] = uncategorized

    total_classified = len(classified_domains)
    logger.info(
        f"LLM classified {total_classified}/{len(ambiguous_entries)} domains "
        f"into {len(all_result)} categories"
    )
    return all_result


def _normalize_cat_key(name: str) -> str:
    """Produce a lowercase key for fuzzy category matching.

    Strips punctuation differences so 'Retail / Marketplace',
    'Retail & Marketplace', and 'Retail & Marketplaces' all map to
    the same canonical key.
    """
    key = name.lower()
    # Normalize separators: / & and → single space
    key = re.sub(r'[/&]', ' ', key)
    key = re.sub(r'\band\b', ' ', key)
    # Remove common trailing plurals that cause drift
    key = re.sub(r'(\w)s\b', r'\1', key)      # marketplaces → marketplace
    # Collapse whitespace
    key = re.sub(r'\s+', ' ', key).strip()
    return key


def _merge_similar_categories(
    categories: Dict[str, List[dict]],
) -> Dict[str, List[dict]]:
    """Merge categories with near-identical names.

    Keeps the first-seen name as the canonical label (it came from the
    highest-citation batch, so it's the most representative).
    """
    merged: Dict[str, List[dict]] = {}
    key_to_canonical: Dict[str, str] = {}      # norm_key → display name

    for cat_name, entries in categories.items():
        norm = _normalize_cat_key(cat_name)
        if norm in key_to_canonical:
            canonical = key_to_canonical[norm]
            merged[canonical].extend(entries)
        else:
            key_to_canonical[norm] = cat_name
            merged[cat_name] = list(entries)

    if len(merged) < len(categories):
        logger.info(
            f"Merged {len(categories)} LLM categories → {len(merged)} "
            f"(normalized near-duplicates)"
        )
    return merged


def _fallback_classify(
    ambiguous_entries: List[dict],
    brand_name: str,
) -> Dict[str, List[dict]]:
    """
    Enhanced rule-based fallback when LLM is not available.
    Uses broader pattern matching to create reasonable groupings.
    """
    editorial = []
    trade_industry = []
    marketplace = []
    reviews_ratings = []
    blogs_independent = []
    uncategorized = []

    # Common editorial / major press patterns
    major_press = [
        'forbes', 'nytimes', 'wsj', 'cnn', 'bbc', 'theguardian',
        'washingtonpost', 'usatoday', 'reuters', 'apnews', 'bloomberg',
        'businessinsider', 'insider', 'theatlantic', 'newyorker',
        'time.com', 'newsweek', 'vox', 'slate', 'wired', 'theverge',
        'techcrunch', 'arstechnica', 'engadget', 'cnet',
        'gq', 'esquire', 'vogue', 'allure', 'glamour', 'cosmopolitan',
        'menshealth', 'womenshealth', 'self.com', 'refinery29',
        'luxuo', 'robbreport', 'elitetraveler', 'departures',
        'cnbc', 'yahoo.com', 'msn.com', 'foxbusiness', 'marketwatch',
        'theweek', 'salon', 'vice', 'vulture', 'rollingstone',
        'luxuryinstitute', 'hypespirit', 'robb-report',
    ]

    # Trade / specialist patterns (will match broadly)
    trade_patterns = [
        # Automotive
        'caranddriver', 'motortrend', 'roadandtrack', 'autoexpress',
        'carbuzz', 'autoblog', 'jalopnik', 'thedrive', 'topgear',
        'motor1', 'autocar', 'carsguide', 'topspeed', 'evo.co',
        'whatcar', 'motorauthority', 'carwow', 'carodyssey',
        'motorbiscuit', 'carconfections', 'detaileddrivers',
        'autonexa', 'carweek', 'guideautoweb', 'carsplan',
        'getcybertrucked', 't3.com',
        # Hospitality
        'skift', 'hospitalitynet', 'hotelmanagement',
        # Tech
        'techradar', 'tomsguide', 'pcmag', 'zdnet',
        # Consumer
        'consumerreports', 'jdpower', 'usnews',
    ]

    # Marketplace / listings / shopping
    marketplace_patterns = [
        'amazon', 'ebay', 'walmart', 'target', 'nordstrom',
        'carvana', 'carmax', 'autotrader', 'cars.com', 'truecar',
        'edmunds', 'kbb', 'carfax', 'cargurus', 'autotempest',
        'carsdirect', 'caredge', 'carvira', 'acvauctions', 'lithia',
        'booking.com', 'expedia', 'hotels.com', 'kayak', 'agoda',
        'rei.com', 'zappos', 'bestbuy', 'sephora',
    ]

    # Review / ratings
    review_patterns = [
        'yelp', 'tripadvisor', 'trustpilot', 'glassdoor',
        'g2.com', 'capterra', 'reviews', 'ratings',
        'iseecars', 'goodcarbadcar',
    ]

    # Blog patterns
    blog_patterns = [
        'blog', 'medium.com', 'substack', 'wordpress',
        'ghost.io', 'blogger', 'tumblr', 'blogspot',
    ]

    # EV / charging infrastructure (for automotive)
    ev_patterns = [
        'evgo', 'chargepoint', 'electrifyamerica', 'plugshare',
        'insideevs', 'electrek',
    ]

    for entry in ambiguous_entries:
        d_lower = entry['domain'].lower()

        if any(p in d_lower for p in major_press):
            editorial.append(entry)
        elif any(p in d_lower for p in trade_patterns):
            trade_industry.append(entry)
        elif any(p in d_lower for p in marketplace_patterns):
            marketplace.append(entry)
        elif any(p in d_lower for p in review_patterns):
            reviews_ratings.append(entry)
        elif any(p in d_lower for p in blog_patterns):
            blogs_independent.append(entry)
        elif any(p in d_lower for p in ev_patterns):
            trade_industry.append(entry)
        # Heuristic: domains with news-like words
        elif any(w in d_lower for w in ['news', 'times', 'post', 'journal', 'daily', 'magazine', 'press']):
            editorial.append(entry)
        # Heuristic: .org often = trade or nonprofit
        elif '.org' in d_lower:
            trade_industry.append(entry)
        # Heuristic: dealer / dealership domains
        elif any(w in d_lower for w in ['dealer', 'auto', 'motor', 'car']):
            marketplace.append(entry)
        else:
            uncategorized.append(entry)

    result = OrderedDict()
    if editorial:
        result["Editorial & News"] = editorial
    if trade_industry:
        result["Trade & Specialist Press"] = trade_industry
    if marketplace:
        result["Marketplace & Listings"] = marketplace
    if reviews_ratings:
        result["Reviews & Ratings"] = reviews_ratings
    if blogs_independent:
        result["Blogs & Independent"] = blogs_independent
    if uncategorized:
        result["Other Sources"] = uncategorized

    return result

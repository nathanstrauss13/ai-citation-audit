#!/usr/bin/env python3
"""
Generate dashboard directly from CSV analysis data.

This bypasses the database and generates dashboard from the LLM-analyzed CSV.

Usage:
    python generate_dashboard_from_csv.py <csv_file> <brand_name>
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from engines.analysis_engine import (
    StudyInsights, BrandMetrics, CompetitorMetrics,
    PlatformMetrics, CitationMetrics, SegmentMetrics,
    PROMINENCE_WEIGHTS
)
from engines.dashboard_v3 import DashboardEngineV3


def load_csv_data(csv_path: str, brand_name: str = "", competitors: List[str] = None) -> List[Dict]:
    """Load and parse CSV data, handling multiple schema formats.

    Supports three schemas:
      1. Slim (new) - raw collection data only (A-I + timestamp). Analysis fields
         are produced by Claude at dashboard generation time.
      2. Legacy citation schema - has {brand}_mentioned, {brand}_position, etc.
         (backward compatible with older CSVs).
      3. Analysis schema - already has new_focal_brand_found, new_prominence, etc.
    """
    rows = []
    brand_clean = brand_name.strip('"\'').strip().lower()
    brand_underscore = brand_clean.replace(' ', '_')

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        # Find brand-specific columns flexibly (handles quotes, spaces, underscores)
        def find_brand_column(suffix: str) -> str:
            for pattern in [f'{brand_clean}_{suffix}', f'{brand_underscore}_{suffix}',
                           f'"{brand_clean}"_{suffix}', f'lululemon_{suffix}']:
                if pattern in fieldnames:
                    return pattern
            for col in fieldnames:
                if suffix in col.lower() and 'competitor' not in col.lower():
                    col_clean = col.lower().replace('"', '').replace("'", '').replace('_', ' ')
                    if brand_clean in col_clean or brand_underscore.replace('_', ' ') in col_clean:
                        return col
            return f'{brand_clean}_{suffix}'

        mentioned_col = find_brand_column('mentioned')

        # Detect schema type
        has_legacy_cols = mentioned_col in fieldnames
        is_analysis_schema = 'new_focal_brand_found' in fieldnames or 'new_prominence' in fieldnames
        has_full_output = 'full_output' in fieldnames

        # Slim schema: has full_output + engine but NOT brand_mentioned columns
        is_slim_schema = has_full_output and not has_legacy_cols and not is_analysis_schema

        for row in reader:
            if is_slim_schema:
                # Slim schema: just normalize field names, defer analysis
                row['platform'] = row.get('engine', row.get('platform', 'unknown'))
                row['query_text'] = row.get('query', row.get('query_text', ''))

                # Citation count from URLs
                urls = row.get('citation_urls', '')
                if urls:
                    if '\n' in urls:
                        row['citation_count'] = len([u for u in urls.split('\n') if u.strip()])
                    else:
                        row['citation_count'] = len([u for u in urls.split('|') if u.strip()])
                else:
                    row['citation_count'] = 0

            elif has_legacy_cols:
                # Legacy citation schema (backward compat with older CSVs)
                position_col = find_brand_column('position')
                featured_col = find_brand_column('featured')

                mentioned_val = str(row.get(mentioned_col, '')).lower()
                row['new_focal_brand_found'] = mentioned_val in ('yes', 'true', '1')

                position = row.get(position_col, '')
                featured = str(row.get(featured_col, '')).lower() in ('yes', 'true', '1')

                if featured or position == '1':
                    row['new_prominence'] = 'featured_first'
                elif position in ('2', '3'):
                    row['new_prominence'] = 'recommended'
                elif position in ('4', '5'):
                    row['new_prominence'] = 'listed'
                elif row['new_focal_brand_found']:
                    row['new_prominence'] = 'mentioned'
                else:
                    row['new_prominence'] = 'not_mentioned'

                row['platform'] = row.get('engine', row.get('platform', 'unknown'))
                row['query_text'] = row.get('query', row.get('query_text', ''))
                row['new_sentiment'] = 'neutral'

                featured_brand_val = row.get('featured_brand', '')
                if row['new_prominence'] != 'featured_first' and featured_brand_val:
                    row['new_primary_competitor'] = featured_brand_val
                else:
                    row['new_primary_competitor'] = ''

                try:
                    row['new_focal_position'] = int(position) if position else None
                except (ValueError, TypeError):
                    row['new_focal_position'] = None

                try:
                    row['citation_count'] = int(row.get('total_citations', 0) or 0)
                    if row['citation_count'] == 0:
                        urls = row.get('citation_urls', '')
                        if urls:
                            if '\n' in urls:
                                row['citation_count'] = len([u for u in urls.split('\n') if u.strip()])
                            else:
                                row['citation_count'] = len([u for u in urls.split('|') if u.strip()])
                except (ValueError, TypeError):
                    row['citation_count'] = 0

                comp_str = row.get('competitors_mentioned', '')
                row['new_brands_mentioned'] = comp_str if comp_str else ''

            else:
                # Standard analysis schema
                row['new_focal_brand_found'] = str(row.get('new_focal_brand_found', '')).lower() in ('true', 'yes', '1')
                row['prominence_changed'] = str(row.get('prominence_changed', '')).lower() in ('true', 'yes', '1')
                row['mentioned_changed'] = str(row.get('mentioned_changed', '')).lower() in ('true', 'yes', '1')

            # Parse confidence as float
            try:
                row['confidence'] = float(row.get('confidence', 0) or 0)
            except (ValueError, TypeError):
                row['confidence'] = 0.0

            # Parse citation count (if not already set)
            if 'citation_count' not in row or row['citation_count'] == 0:
                try:
                    row['citation_count'] = int(row.get('citation_count', 0) or 0)
                except (ValueError, TypeError):
                    row['citation_count'] = 0

            # Parse position (if not already set)
            if row.get('new_focal_position') is None:
                try:
                    pos = row.get('new_focal_position', '')
                    row['new_focal_position'] = int(pos) if pos else None
                except (ValueError, TypeError):
                    row['new_focal_position'] = None

            rows.append(row)

    # For slim schema, run Claude analysis to produce the analytical fields
    if is_slim_schema and rows:
        from engines.response_analyzer import analyze_responses
        print(f"  Slim CSV detected ({len(rows)} rows) — running Claude analysis...")
        analyze_responses(
            rows=rows,
            brand_name=brand_name,
            competitors=competitors or [],
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
        )
        print(f"  Analysis complete.")

    return rows


def analyze_csv_data(rows: List[Dict], brand_name: str) -> StudyInsights:
    """Analyze CSV data and produce insights."""

    total = len(rows)
    brand_lower = brand_name.strip('"\'').strip().lower()

    # Detect branded vs unbranded for each row
    # Use query_type column if present, otherwise infer from query text
    for r in rows:
        qt = r.get('query_type', '').lower().strip()
        if qt in ('branded', 'unbranded'):
            r['_is_branded'] = (qt == 'branded')
        else:
            # Heuristic: if brand name appears in the query, it's branded
            query_text = r.get('query_text', '').lower()
            r['_is_branded'] = brand_lower in query_text

    # Use new analysis columns
    mentions = sum(1 for r in rows if r['new_focal_brand_found'])

    # Prominence distribution
    prominence_counts = Counter(r.get('new_prominence', 'unknown') for r in rows)
    featured = prominence_counts.get('featured_first', 0)
    recommended = prominence_counts.get('recommended', 0)
    listed = prominence_counts.get('listed', 0)
    mentioned_only = prominence_counts.get('mentioned', 0)
    not_mentioned = prominence_counts.get('not_mentioned', 0)

    # Prominence score
    prominence_score = sum(
        PROMINENCE_WEIGHTS.get(r.get('new_prominence', 'not_mentioned'), 0)
        for r in rows
    ) / total * 100 if total > 0 else 0

    # Branded / Unbranded split (v17)
    branded_rows = [r for r in rows if r.get('_is_branded')]
    unbranded_rows = [r for r in rows if not r.get('_is_branded')]

    branded_total = len(branded_rows)
    branded_mentions = sum(1 for r in branded_rows if r['new_focal_brand_found'])
    branded_featured = sum(1 for r in branded_rows if r.get('new_prominence') == 'featured_first')

    unbranded_total = len(unbranded_rows)
    unbranded_mentions = sum(1 for r in unbranded_rows if r['new_focal_brand_found'])
    unbranded_featured = sum(1 for r in unbranded_rows if r.get('new_prominence') == 'featured_first')
    unbranded_top3 = sum(1 for r in unbranded_rows if r.get('new_prominence') in ('featured_first', 'recommended'))

    # v17 AEO Score: (Featured Rate * 0.7) + (Top Rate * 0.3) on UNBRANDED only
    unbranded_featured_rate = (unbranded_featured / unbranded_total * 100) if unbranded_total > 0 else 0
    unbranded_top_rate = (unbranded_top3 / unbranded_total * 100) if unbranded_total > 0 else 0
    aeo_score = (unbranded_featured_rate * 0.7) + (unbranded_top_rate * 0.3)

    # Sentiment
    sentiments = Counter(r.get('new_sentiment', 'unknown') for r in rows if r['new_focal_brand_found'])
    total_with_sentiment = sum(sentiments.values()) or 1

    # Brand metrics
    brand_metrics = BrandMetrics(
        total_queries=len(set(r.get('query_text', '') for r in rows)),
        total_responses=total,
        mention_count=mentions,
        mention_rate=mentions/total*100 if total > 0 else 0,
        featured_first_count=featured,
        featured_first_rate=featured/total*100 if total > 0 else 0,
        recommended_count=recommended,
        recommended_rate=recommended/total*100 if total > 0 else 0,
        listed_count=listed,
        listed_rate=listed/total*100 if total > 0 else 0,
        mentioned_only_count=mentioned_only,
        not_mentioned_count=not_mentioned,
        # Branded / Unbranded (v17)
        branded_total=branded_total,
        branded_mention_count=branded_mentions,
        branded_mention_rate=(branded_mentions / branded_total * 100) if branded_total > 0 else 0,
        branded_featured_first_count=branded_featured,
        branded_featured_first_rate=(branded_featured / branded_total * 100) if branded_total > 0 else 0,
        unbranded_total=unbranded_total,
        unbranded_mention_count=unbranded_mentions,
        unbranded_mention_rate=(unbranded_mentions / unbranded_total * 100) if unbranded_total > 0 else 0,
        unbranded_featured_first_count=unbranded_featured,
        unbranded_featured_first_rate=unbranded_featured_rate,
        unbranded_top_rate=unbranded_top_rate,
        aeo_score=aeo_score,
        prominence_score=prominence_score,
        visibility_score=(mentions/total*100 * 0.4) + (prominence_score * 0.6) if total > 0 else 0,
        positive_sentiment_rate=sentiments.get('positive', 0)/total_with_sentiment*100,
        neutral_sentiment_rate=sentiments.get('neutral', 0)/total_with_sentiment*100,
        negative_sentiment_rate=sentiments.get('negative', 0)/total_with_sentiment*100
    )

    # Competitor discovery (use enriched data if available)
    competitor_counts = Counter()
    competitor_featured = Counter()

    for r in rows:
        # Check if we have enriched data from LLM analyzer
        if 'competitors_mentioned' in r and isinstance(r['competitors_mentioned'], list):
            brands = r['competitors_mentioned']
        else:
            brands_str = r.get('new_brands_mentioned', '')
            brands = [b.strip() for b in brands_str.split('|') if b.strip()]

        for brand in brands:
            if brand.lower() != brand_name.lower():
                competitor_counts[brand] += 1

        # Track primary competitor (first position)
        # Use enriched featured_brand if available
        if 'featured_brand' in r:
            primary = r.get('featured_brand', '')
        else:
            primary = r.get('new_primary_competitor', '')

        if primary and primary.lower() != brand_name.lower():
            competitor_featured[primary] += 1

    # Head-to-head analysis
    competitors = []
    for comp, count in competitor_counts.most_common(15):
        # Calculate head-to-head wins/losses
        h2h_wins, h2h_losses, h2h_ties = 0, 0, 0
        for r in rows:
            brands_str = r.get('new_brands_mentioned', '').lower()
            if brand_name.lower() in brands_str and comp.lower() in brands_str:
                focal_pos = r.get('new_focal_position')
                # If brand is position 1, it wins
                if focal_pos == 1:
                    h2h_losses += 1  # Competitor loses
                elif r.get('new_primary_competitor', '').lower() == comp.lower():
                    h2h_wins += 1  # Competitor wins
                else:
                    h2h_ties += 1

        competitors.append(CompetitorMetrics(
            brand_name=comp,
            mention_count=count,
            featured_count=competitor_featured.get(comp, 0),
            mention_rate=count/total*100 if total > 0 else 0,
            featured_rate=competitor_featured.get(comp, 0)/total*100 if total > 0 else 0,
            win_rate=(competitor_featured.get(comp, 0) / count * 100) if count > 0 else 0,
            head_to_head_wins=h2h_wins,
            head_to_head_losses=h2h_losses,
            head_to_head_ties=h2h_ties
        ))

    # Platform metrics
    platform_metrics = []
    platforms = set(r.get('platform', '') for r in rows)

    for platform in sorted(platforms):
        p_rows = [r for r in rows if r.get('platform') == platform]
        p_total = len(p_rows)
        p_mentions = sum(1 for r in p_rows if r['new_focal_brand_found'])
        p_featured = sum(1 for r in p_rows if r.get('new_prominence') == 'featured_first')
        p_score = sum(
            PROMINENCE_WEIGHTS.get(r.get('new_prominence', 'not_mentioned'), 0)
            for r in p_rows
        ) / p_total * 100 if p_total > 0 else 0

        platform_metrics.append(PlatformMetrics(
            platform=platform,
            response_count=p_total,
            mention_rate=p_mentions/p_total*100 if p_total > 0 else 0,
            featured_rate=p_featured/p_total*100 if p_total > 0 else 0,
            prominence_score=p_score
        ))

    # Citation metrics - Use LLM-classified data when available, fall back to heuristics
    def split_delimited(s: str) -> list:
        """Split a string by newline or pipe delimiter (handles both formats)."""
        if not s:
            return []
        if '\n' in s:
            return [x.strip() for x in s.split('\n') if x.strip()]
        return [x.strip() for x in s.split('|') if x.strip()]

    all_citations = []
    for r in rows:
        # Support both column names: 'citations' (analysis schema) and 'citation_urls' (citation schema)
        cites = r.get('citations', '') or r.get('citation_urls', '')
        if cites:
            # Split by newline or pipe, filter out Gemini internal URLs
            filtered = [c for c in split_delimited(cites)
                       if 'vertexaisearch.cloud.google.com' not in c]
            all_citations.extend(filtered)

    # Extract domains - also check citation_domains column directly
    domain_counts = Counter()

    # First try to get domains from citation_domains column (already extracted)
    for r in rows:
        domains_str = r.get('citation_domains', '')
        if domains_str:
            for d in split_delimited(domains_str):
                if d and d != 'vertexaisearch.cloud.google.com':
                    domain_counts[d] += 1

    # If no domains found, extract from URLs
    if not domain_counts and all_citations:
        for url in all_citations:
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.replace('www.', '')
                if domain and domain != 'vertexaisearch.cloud.google.com':
                    domain_counts[domain] += 1
            except:
                pass

    # Use LLM-classified citation data when available (from enhanced analysis)
    # Check for new citation_classifications structure (from classify_citations_only)
    owned_count = 0
    editorial_count = 0
    retail_count = 0
    social_count = 0
    wikipedia_count = 0

    for r in rows:
        # New format: citation_classifications dict with URL lists
        if 'citation_classifications' in r:
            classifications = r.get('citation_classifications', {})
            # Handle both parsed dict and string representation
            if isinstance(classifications, str):
                import ast
                try:
                    classifications = ast.literal_eval(classifications)
                except:
                    classifications = {}

            if isinstance(classifications, dict):
                owned_count += len(classifications.get('owned', []))
                editorial_count += len(classifications.get('editorial', []))
                retail_count += len(classifications.get('retail', []))
                social_count += len(classifications.get('social_community', []))
                wikipedia_count += len(classifications.get('wikipedia', []))
        # Old format: citation count columns
        else:
            owned_count += int(r.get('owned_citations', 0) or 0)
            editorial_count += int(r.get('editorial_citations', 0) or 0)
            retail_count += int(r.get('retail_citations', 0) or 0)
            social_count += int(r.get('social_citations', 0) or 0)

    tier1_count = sum(int(r.get('tier1_citations', 0) or 0) for r in rows)
    tier2_count = sum(int(r.get('tier2_citations', 0) or 0) for r in rows)
    brand_cited_count = sum(int(r.get('brand_cited_sources', 0) or 0) for r in rows)

    # Always run heuristic classification on domain counts.
    # If LLM data exists, it supplements; if not, it's the primary source.
    # This ensures all citations are classified, not just those the LLM saw.
    if len(all_citations) > 0:
        # Industry-aware classification
        # Detect hospitality industry from common signals
        hospitality_signals = ['hotel', 'resort', 'travel', 'booking', 'hospitality', 'lodging', 'stay']
        is_hospitality = any(signal in brand_name.lower() for signal in hospitality_signals) or \
                         any(any(signal in d.lower() for signal in ['hotel', 'booking.com', 'tripadvisor', 'expedia'])
                             for d in domain_counts.keys())

        # Heuristic counts from domain analysis — take the max of LLM vs heuristic
        # so we never lose data the LLM missed (truncation, partial classification)
        brand_clean = brand_name.lower().replace(' ', '').replace('-', '')
        h_owned = sum(c for d, c in domain_counts.items() if brand_clean in d.lower().replace('-', ''))
        owned_count = max(owned_count, h_owned)

        if is_hospitality:
            # HOSPITALITY CLASSIFICATION
            travel_press = [
                'cntraveler', 'condenast', 'travelandleisure', 'travel+leisure',
                'thepointsguy', 'pointsguy', 'afar.com', 'fodors', 'frommers',
                'lonelyplanet', 'nationalgeographic', 'travelandtourworld',
                'luxurytraveladvisor', 'luxurytravelmag', 'elitetraveler',
                'hospitalitydesign', 'hospitalitynet', 'hotelmanagement',
                'skift', 'phocuswire', 'travelweekly', 'ttgmedia',
                'hoteliermiddleeast', 'hoteliermagazine', 'hotelnewsresource',
                'tatler', 'rfrequent', 'onemileatatime', 'viewfromthewing',
                'forbes', 'nytimes', 'wsj', 'cnn', 'bbc', 'theguardian',
                'vogue', 'gq', 'esquire', 'architecturaldigest', 'dwell',
                'wallpaper', 'dezeen', 'designboom', 'homejournal',
                'michelin', 'timeout', 'insider', 'businessinsider',
            ]
            h_editorial = sum(c for d, c in domain_counts.items()
                              if any(x in d.lower() for x in travel_press))
            editorial_count = max(editorial_count, h_editorial)

            travel_booking = [
                'booking.com', 'expedia', 'hotels.com', 'tripadvisor', 'kayak',
                'agoda', 'trivago', 'priceline', 'orbitz', 'travelocity',
                'hotwire', 'makemytrip', 'goibibo', 'hostelworld',
                'airbnb', 'vrbo', 'homeaway', 'getaroom', 'hopper',
                'trip.com', 'ctrip', 'skyscanner', 'momondo', 'cheaptickets',
                'directbooker', 'cozycozy', 'google.com/travel',
            ]
            h_retail = sum(c for d, c in domain_counts.items()
                           if any(x in d.lower() for x in travel_booking))
            retail_count = max(retail_count, h_retail)
        else:
            # DEFAULT CLASSIFICATION (Retail/Consumer/Tech)
            h_editorial = sum(c for d, c in domain_counts.items()
                              if any(x in d for x in ['forbes', 'gq', 'esquire', 'menshealth',
                                                      'womenshealth', 'runnersworld', 'self',
                                                      'vogue', 'nytimes', 'wsj', 'cnn',
                                                      'wired', 'techcrunch', 'theverge']))
            editorial_count = max(editorial_count, h_editorial)

            h_retail = sum(c for d, c in domain_counts.items()
                           if any(x in d for x in ['nordstrom', 'rei', 'amazon', 'zappos',
                                                   'dickssportinggoods', 'target', 'walmart',
                                                   'bestbuy', 'macys', 'sephora']))
            retail_count = max(retail_count, h_retail)

        # Social (same for all industries)
        h_social = sum(c for d, c in domain_counts.items()
                       if any(x in d for x in ['reddit', 'youtube', 'instagram', 'tiktok',
                                               'twitter', 'facebook', 'pinterest', 'flyertalk']))
        social_count = max(social_count, h_social)
        brand_cited_count = max(brand_cited_count, owned_count)

    # Calculate content conversion rate (v17: wins when brand's site is cited)
    # Use URL-based detection: check if any owned domain appears in citation_urls
    brand_clean_lower = brand_name.strip('"\'').strip().lower().replace(' ', '')
    owned_domain_patterns = [brand_clean_lower]  # e.g. 'bmw' matches bmw.com, bmwusa.com etc.

    brand_cited_count_url = 0
    wins_when_cited = 0
    for r in rows:
        urls = r.get('citation_urls', '') or r.get('citations', '')
        if urls and any(pat in urls.lower() for pat in owned_domain_patterns):
            brand_cited_count_url += 1
            if r.get('new_prominence') == 'featured_first':
                wins_when_cited += 1

    # Use URL-based count if available, fall back to domain count
    brand_cited_count = max(brand_cited_count, brand_cited_count_url)
    content_conversion_rate = (wins_when_cited / brand_cited_count * 100) if brand_cited_count > 0 else 0

    # Calculate Citation Quality Tiers
    # Tier 1: Major publications (NYT, WSJ, Forbes, BBC, etc.)
    tier1_domains = [
        'nytimes', 'wsj', 'washingtonpost', 'bbc', 'cnn', 'reuters', 'apnews',
        'theguardian', 'ft.com', 'economist', 'npr', 'time.com', 'usatoday',
        'latimes', 'bloomberg', 'forbes', 'fortune', 'businessinsider', 'cnbc',
        'marketwatch', 'hbr', 'vogue', 'gq', 'esquire', 'vanityfair', 'newyorker',
        'theatlantic', 'wired', 'architecturaldigest', 'cntraveler', 'travelandleisure',
        'nationalgeographic', 'smithsonianmag'
    ]
    # Tier 2: Trade press, specialty publications
    tier2_domains = [
        'techcrunch', 'theverge', 'arstechnica', 'engadget', 'cnet', 'zdnet',
        'venturebeat', 'mashable', 'adage', 'adweek', 'prweek', 'fastcompany',
        'inc.com', 'entrepreneur', 'hospitalitynet', 'skift', 'phocuswire',
        'hotelmanagement', 'hotelnewsresource', 'runnersworld', 'menshealth',
        'womenshealth', 'self', 'outsideonline', 'shape', 'elle', 'harpersbazaar',
        'cosmopolitan', 'glamour', 'instyle', 'refinery29', 'wirecutter',
        'thestrategist', 'reviewed', 'rtings', 'tomsguide', 'pcmag', 'techradar',
        'goodhousekeeping', 'sfchronicle', 'bostonglobe', 'chicagotribune',
        'thepointsguy', 'pointsguy', 'onemileatatime', 'frequentmiler'
    ]
    # Tier 3: Blogs, forums, UGC
    tier3_domains = [
        'reddit', 'quora', 'medium', 'substack', 'flyertalk', 'tripadvisor',
        'yelp', 'wordpress', 'blogspot', 'tumblr', 'wix', 'buzzfeed', 'ranker'
    ]

    tier1_count = sum(c for d, c in domain_counts.items()
                      if any(t1 in d.lower() for t1 in tier1_domains))
    tier2_count = sum(c for d, c in domain_counts.items()
                      if any(t2 in d.lower() for t2 in tier2_domains)
                      and not any(t1 in d.lower() for t1 in tier1_domains))
    tier3_count = sum(c for d, c in domain_counts.items()
                      if any(t3 in d.lower() for t3 in tier3_domains)
                      and not any(t1 in d.lower() for t1 in tier1_domains)
                      and not any(t2 in d.lower() for t2 in tier2_domains))
    untiered_count = len(all_citations) - tier1_count - tier2_count - tier3_count

    # Calculate Citation Quality Score (weighted: T1=3, T2=2, T3=1)
    weighted_sum = (tier1_count * 3) + (tier2_count * 2) + (tier3_count * 1)
    max_possible = len(all_citations) * 3 if all_citations else 1
    citation_quality_score = (weighted_sum / max_possible * 100) if max_possible > 0 else 0

    reference_count = sum(c for d, c in domain_counts.items() if any(x in d for x in ['wikipedia', 'britannica']))

    citation_metrics = CitationMetrics(
        total_citations=len(all_citations),
        owned_citations=owned_count,
        editorial_citations=editorial_count,
        retail_citations=retail_count,
        social_citations=social_count,
        affiliate_citations=0,  # Could be enhanced with LLM classification
        reference_citations=reference_count,
        other_citations=max(0, len(all_citations) - owned_count - editorial_count - retail_count - social_count - wikipedia_count - reference_count),
        tier1_citations=tier1_count,
        tier2_citations=tier2_count,
        tier3_citations=tier3_count,
        untiered_citations=untiered_count,
        citation_quality_score=citation_quality_score,
        times_brand_cited=brand_cited_count,
        wins_when_cited=wins_when_cited,
        content_conversion_rate=content_conversion_rate,
        top_domains=domain_counts.most_common(200)  # Capture all citation sources
    )

    # Generate insights based on data
    key_insights = []
    opportunities = []
    threats = []

    # Insight 1: Overall visibility
    key_insights.append(
        f"AI visibility score of {brand_metrics.visibility_score:.1f}% indicates "
        f"{'strong' if brand_metrics.visibility_score > 60 else 'moderate' if brand_metrics.visibility_score > 40 else 'developing'} "
        f"presence across AI platforms. {brand_name} appears in {brand_metrics.mention_rate:.1f}% of relevant queries."
    )

    # Insight 2: Platform variance
    if platform_metrics:
        best_platform = max(platform_metrics, key=lambda p: p.prominence_score)
        worst_platform = min(platform_metrics, key=lambda p: p.prominence_score)
        if best_platform.prominence_score - worst_platform.prominence_score > 15:
            key_insights.append(
                f"Significant platform variance detected: {best_platform.platform} ({best_platform.prominence_score:.1f}) "
                f"outperforms {worst_platform.platform} ({worst_platform.prominence_score:.1f}). "
                f"Platform-specific optimization may be beneficial."
            )

    # Insight 3: Featured rate analysis
    if brand_metrics.featured_first_rate > 25:
        key_insights.append(
            f"Strong featured-first rate of {brand_metrics.featured_first_rate:.1f}% shows {brand_name} "
            f"is frequently positioned as the top recommendation in AI responses."
        )

    # Opportunity 1: Conversion gap
    if brand_metrics.mention_rate > brand_metrics.featured_first_rate + 20:
        opportunities.append(
            f"Conversion opportunity: {brand_metrics.mention_rate:.1f}% mention rate but only "
            f"{brand_metrics.featured_first_rate:.1f}% featured-first rate. Focus on authoritative content "
            f"that positions {brand_name} as the top recommendation."
        )

    # Opportunity 2: Platform optimization
    if platform_metrics:
        low_performers = [p for p in platform_metrics if p.prominence_score < brand_metrics.prominence_score - 10]
        if low_performers:
            opportunities.append(
                f"Platform optimization opportunity: {', '.join(p.platform for p in low_performers)} "
                f"underperform the average. Investigate content sources these platforms prefer."
            )

    # Threat 1: Competitor pressure
    if competitors:
        top_comp = competitors[0]
        if top_comp.mention_count > mentions * 0.8:
            threats.append(
                f"{top_comp.brand_name} appears in {top_comp.mention_rate:.1f}% of responses, "
                f"creating significant competitive pressure. Monitor their content strategy."
            )

    # Threat 2: Low mention categories
    queries_by_mention = {}
    for r in rows:
        q = r.get('query_text', '')
        if q not in queries_by_mention:
            queries_by_mention[q] = {'total': 0, 'mentioned': 0}
        queries_by_mention[q]['total'] += 1
        if r['new_focal_brand_found']:
            queries_by_mention[q]['mentioned'] += 1

    low_mention_queries = [q for q, stats in queries_by_mention.items()
                          if stats['mentioned'] / stats['total'] < 0.3]
    if low_mention_queries:
        threats.append(
            f"{len(low_mention_queries)} query categories show low {brand_name} visibility (<30% mention rate). "
            f"These may require content investment if they're strategic priorities."
        )

    # Platform variance (v17): max mention rate - min mention rate across platforms
    if platform_metrics:
        plat_rates = [p.mention_rate for p in platform_metrics if p.response_count > 0]
        brand_metrics.platform_variance = (max(plat_rates) - min(plat_rates)) if len(plat_rates) > 1 else 0

    # Competitive rank (v17): brand's rank among all discovered brands by mention count
    if competitors:
        # Brand's rank is 1 if it has more mentions than all competitors, otherwise its position
        brand_rank = 1
        for c in competitors:
            if c.mention_count > mentions:
                brand_rank += 1
        brand_metrics.competitive_rank = brand_rank

    # Build insights object
    insights = StudyInsights(
        study_id="csv-analysis",
        brand_name=brand_name,
        study_type="organic_visibility",
        brand_metrics=brand_metrics,
        segment_metrics={},  # Not available from CSV
        discovered_competitors=competitors[:10],
        share_of_voice={c.brand_name: c.mention_rate for c in competitors[:10]},
        citation_metrics=citation_metrics,
        platform_metrics=platform_metrics,
        key_insights=key_insights,
        opportunities=opportunities,
        threats=threats
    )

    # Attach raw query data for the appendix
    insights.query_data = rows

    return insights


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard from CSV")
    parser.add_argument("csv_file", help="Path to analysis CSV")
    parser.add_argument("brand_name", help="Brand name")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--competitors", "-c", help="Comma-separated list of competitors")
    parser.add_argument("--enrich", action="store_true", help="Use LLM to classify citations (fast, lightweight)")

    args = parser.parse_args()

    print("=" * 70)
    print(f"  GENERATING DASHBOARD FROM CSV: {args.brand_name}")
    print("=" * 70)

    # Load data
    print(f"\nLoading CSV: {args.csv_file}")
    cli_competitors = [c.strip() for c in (args.competitors or '').split(',') if c.strip()]
    rows = load_csv_data(args.csv_file, args.brand_name, competitors=cli_competitors)
    print(f"Loaded {len(rows)} responses")

    # Optional: Classify citations with LLM
    if args.enrich:
        print(f"\n🤖 Classifying citations with LLM...")
        print(f"   Analyzing {len(rows)} responses with Claude...")
        print(f"   Note: Competitors already extracted via regex in CSV")

        from llm_response_analyzer import classify_citations_in_csv
        rows = classify_citations_in_csv(rows, args.brand_name)
        print(f"   ✅ Citation classification complete")

        # Save enriched data for debugging
        import csv as csv_module
        enriched_csv_path = args.csv_file.replace('.csv', '_ENRICHED.csv')
        if rows:
            with open(enriched_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv_module.DictWriter(f, fieldnames=rows[0].keys(), quoting=csv_module.QUOTE_ALL)
                writer.writeheader()
                for row in rows:
                    # Convert lists to strings for CSV
                    row_copy = dict(row)
                    for k, v in row_copy.items():
                        if isinstance(v, (list, dict)):
                            row_copy[k] = str(v)
                    writer.writerow(row_copy)
            print(f"   📄 Saved enriched data: {enriched_csv_path}")

    # Analyze
    print("\nAnalyzing data...")
    insights = analyze_csv_data(rows, args.brand_name)

    # Print summary
    print(f"\n  Brand Metrics:")
    print(f"    Total Responses: {insights.brand_metrics.total_responses}")
    print(f"    Mention Rate: {insights.brand_metrics.mention_rate:.1f}%")
    print(f"    Featured First: {insights.brand_metrics.featured_first_rate:.1f}%")
    print(f"    Prominence Score: {insights.brand_metrics.prominence_score:.1f}")
    print(f"    Visibility Score: {insights.brand_metrics.visibility_score:.1f}")

    print(f"\n  Platform Performance:")
    for p in insights.platform_metrics:
        print(f"    {p.platform:12} | Mention: {p.mention_rate:5.1f}% | Featured: {p.featured_rate:5.1f}% | Score: {p.prominence_score:.1f}")

    print(f"\n  Top Competitors:")
    for c in insights.discovered_competitors[:5]:
        print(f"    {c.brand_name:20} | Mentions: {c.mention_count:3} | H2H: {c.head_to_head_wins}W-{c.head_to_head_losses}L")

    # Classify citations adaptively (hybrid rule-based + LLM)
    print("\nClassifying citation sources...")
    classified_citations = None
    try:
        from engines.citation_classifier import classify_citations_adaptive
        domain_counts = insights.citation_metrics.top_domains
        competitor_names = [c.brand_name for c in insights.discovered_competitors[:15]]
        classified_citations = classify_citations_adaptive(
            domain_counts=domain_counts,
            brand_name=args.brand_name,
            competitor_names=competitor_names,
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
        )
        if classified_citations:
            print(f"  Classified into {len(classified_citations)} adaptive categories:")
            for cat_name, entries in classified_citations.items():
                total = sum(e['total'] for e in entries)
                print(f"    {cat_name:30} | {len(entries):3} sources | {total:4} citations")
        else:
            print("  No citations to classify")
    except Exception as e:
        print(f"  ⚠ Citation classification failed ({e}), using legacy tabs")
        classified_citations = None

    # Generate dashboard
    print("\nGenerating dashboard HTML...")
    engine = DashboardEngineV3()
    html = engine.generate(insights, query_data=rows, classified_citations=classified_citations)

    # Save standalone version
    output_path = args.output or f"{args.brand_name.lower().replace(' ', '_')}_dashboard_corrected.html"
    with open(output_path, 'w') as f:
        f.write(html)

    # Generate and save embed version
    embed_html = engine.generate_embed(insights, query_data=rows, classified_citations=classified_citations)
    embed_path = output_path.replace('.html', '_embed.html')
    with open(embed_path, 'w') as f:
        f.write(embed_html)

    print(f"\n{'='*70}")
    print(f"  ✅ Dashboard generated: {output_path}")
    print(f"     File size: {len(html):,} bytes")
    print(f"  ✅ Embed version: {embed_path}")
    print(f"     File size: {len(embed_html):,} bytes")
    print(f"{'='*70}")

    return output_path


if __name__ == "__main__":
    main()

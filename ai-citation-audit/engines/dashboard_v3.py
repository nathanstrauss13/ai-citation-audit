#!/usr/bin/env python3
"""
Dashboard Engine V3 - Mirrors the working Lululemon dashboard structure.

Key features:
- Embeds data as JavaScript arrays for dynamic rendering
- All charts/grids rendered via JavaScript
- Real filtering that re-renders views
- Tab system with proper content panes
"""

import json
from typing import Any, List, Dict
from dataclasses import dataclass

# Import media intelligence for owned/earned analysis
try:
    from .media_intelligence import MediaIntelligenceEngine, prepare_media_intelligence_js
    MEDIA_INTEL_AVAILABLE = True
except ImportError:
    MEDIA_INTEL_AVAILABLE = False


class DashboardEngineV3:
    """Generates interactive HTML dashboards matching the reference implementation."""

    BRAND_COLOR = "#D31334"

    def generate(self, insights: Any, query_data: List[Dict] = None,
                 classified_citations: Dict = None) -> str:
        """Generate the full dashboard HTML.

        Args:
            insights: StudyInsights object with brand/citation metrics
            query_data: Raw row data from CSV
            classified_citations: Optional dict from citation_classifier.classify_citations_adaptive().
                If provided, uses adaptive tabs. Otherwise falls back to legacy hardcoded tabs.
        """
        brand = insights.brand_name

        # Prepare data for embedding
        query_data_list = query_data or getattr(insights, 'query_data', [])
        query_data_js = self._prepare_query_data(query_data_list, brand_name=brand)
        categories_js = self._prepare_categories(insights, query_data)
        platforms_js = self._prepare_platforms(insights)
        competitors_js = self._prepare_competitors(insights)
        sov_data_js = self._prepare_share_of_voice(insights, query_data_list)
        tier_data_js = self._prepare_citation_tiers(insights)
        sentiment_data_js = self._prepare_sentiment_data(insights)

        # Citation classification: adaptive (new) or legacy (fallback)
        if classified_citations:
            citation_categories_js = self._prepare_adaptive_citations(classified_citations)
            use_adaptive_citations = True
        else:
            media_data_js = self._prepare_media_data(insights)
            use_adaptive_citations = False

        # Media Intelligence (Owned/Earned analysis)
        media_intel_js = self._prepare_media_intelligence(insights, query_data_list)

        # v17: Content Conversion data
        content_conversion_js = self._prepare_content_conversion(insights)

        # v17: Branded/Unbranded metrics
        branded_metrics_js = self._prepare_branded_unbranded(insights)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand} AI Citation Intelligence Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
{self._get_styles()}
    </style>
</head>
<body>
    {self._nav_bubbles()}
    <div class="container">
        {self._section_header(insights)}
        <div id="s-overview">{self._section_hero(insights)}</div>
        <div id="s-conversion">{self._section_content_conversion(insights)}</div>
        <div id="s-sov">{self._section_share_of_voice()}</div>
        <div id="s-competitive">{self._section_competitive()}</div>
        <div id="s-categories">{self._section_categories()}</div>
        <div id="s-platforms">{self._section_platforms()}</div>
        <div id="s-position">{self._section_position_analysis(insights)}</div>
        <div id="s-media">{self._section_citations_adaptive(classified_citations) if use_adaptive_citations else self._section_citations()}</div>
        <div id="s-queries">{self._section_query_appendix()}</div>
        <div id="s-methodology">{self._section_methodology(insights)}</div>
    </div>

    <script>
        // Embedded data
        const queryData = {query_data_js};
        const categories = {categories_js};
        const platforms = {platforms_js};
        {"const citationCategories = " + citation_categories_js + ";" if use_adaptive_citations else self._legacy_media_vars(media_data_js)}
        const competitors = {competitors_js};
        const sovData = {sov_data_js};
        const tierData = {tier_data_js};
        const sentimentData = {sentiment_data_js};
        const mediaIntelligence = {media_intel_js};
        const contentConversion = {content_conversion_js};
        const brandedMetrics = {branded_metrics_js};
        const brandName = "{brand}";
        const useAdaptiveCitations = {"true" if use_adaptive_citations else "false"};

        let currentPlatformFilter = 'all';

        {self._get_scripts()}
    </script>
</body>
</html>'''
        return html

    def generate_embed(self, insights: Any, query_data: List[Dict] = None,
                       classified_citations: Dict = None) -> str:
        """Generate embed-ready version (no <html>/<head>/<body> wrapper)."""
        brand = insights.brand_name

        query_data_list = query_data or getattr(insights, 'query_data', [])
        query_data_js = self._prepare_query_data(query_data_list, brand_name=brand)
        categories_js = self._prepare_categories(insights, query_data)
        platforms_js = self._prepare_platforms(insights)
        competitors_js = self._prepare_competitors(insights)
        sov_data_js = self._prepare_share_of_voice(insights, query_data_list)
        tier_data_js = self._prepare_citation_tiers(insights)
        sentiment_data_js = self._prepare_sentiment_data(insights)
        media_intel_js = self._prepare_media_intelligence(insights, query_data_list)
        content_conversion_js = self._prepare_content_conversion(insights)
        branded_metrics_js = self._prepare_branded_unbranded(insights)

        if classified_citations:
            citation_categories_js = self._prepare_adaptive_citations(classified_citations)
            use_adaptive_citations = True
        else:
            media_data_js = self._prepare_media_data(insights)
            use_adaptive_citations = False

        return f'''<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{self._get_styles()}
</style>
<div class="aeo-dashboard-embed">
    {self._nav_bubbles()}
    <div class="container">
        {self._section_header(insights)}
        <div id="s-overview">{self._section_hero(insights)}</div>
        <div id="s-conversion">{self._section_content_conversion(insights)}</div>
        <div id="s-sov">{self._section_share_of_voice()}</div>
        <div id="s-competitive">{self._section_competitive()}</div>
        <div id="s-categories">{self._section_categories()}</div>
        <div id="s-platforms">{self._section_platforms()}</div>
        <div id="s-position">{self._section_position_analysis(insights)}</div>
        <div id="s-media">{self._section_citations_adaptive(classified_citations) if use_adaptive_citations else self._section_citations()}</div>
        <div id="s-queries">{self._section_query_appendix()}</div>
        <div id="s-methodology">{self._section_methodology(insights)}</div>
    </div>
</div>
<script>
    const queryData = {query_data_js};
    const categories = {categories_js};
    const platforms = {platforms_js};
    {"const citationCategories = " + citation_categories_js + ";" if use_adaptive_citations else self._legacy_media_vars(media_data_js)}
    const competitors = {competitors_js};
    const sovData = {sov_data_js};
    const tierData = {tier_data_js};
    const sentimentData = {sentiment_data_js};
    const mediaIntelligence = {media_intel_js};
    const contentConversion = {content_conversion_js};
    const brandedMetrics = {branded_metrics_js};
    const brandName = "{brand}";
    const useAdaptiveCitations = {"true" if use_adaptive_citations else "false"};

    let currentPlatformFilter = 'all';

    {self._get_scripts()}
</script>'''

    def _prepare_query_data(self, rows: List[Dict], brand_name: str = None) -> str:
        """Convert query data to JavaScript array."""
        js_data = []
        for row in rows:
            # When brand is featured first, use the brand name (not 'Target Brand')
            if row.get('new_prominence') == 'featured_first':
                featured_brand = brand_name or row.get('focal_brand', '')
            else:
                featured_brand = row.get('new_primary_competitor', '')

            js_data.append({
                "query": row.get('query_text', '')[:100],
                "category": row.get('category', 'General'),
                "engine": row.get('platform', ''),
                "mentioned": "Yes" if row.get('new_focal_brand_found') else "No",
                "featured": "Yes" if row.get('new_prominence') == 'featured_first' else "No",
                "position": self._position_label(row.get('new_focal_position')),
                "featuredBrand": featured_brand,
                "competitors": row.get('new_brands_mentioned', '').replace('|', '|')
            })
        return json.dumps(js_data)

    def _position_label(self, pos) -> str:
        """Convert position number to label."""
        if not pos:
            return "Not Present"
        try:
            p = int(pos)
            if p == 1:
                return "1st"
            elif p == 2:
                return "2nd"
            elif p == 3:
                return "3rd"
            elif p <= 10:
                return f"{p}th"
            else:
                return "4th+"
        except:
            return "Not Present"

    def _prepare_categories(self, insights: Any, query_data: List[Dict]) -> str:
        """Prepare category statistics."""
        cat_stats = {}
        rows = query_data or getattr(insights, 'query_data', [])

        for row in rows:
            cat = row.get('category', 'General')
            if cat not in cat_stats:
                cat_stats[cat] = {'tests': 0, 'mentions': 0, 'featured': 0, 'sampleQuery': row.get('query_text', '')[:60]}
            cat_stats[cat]['tests'] += 1
            if row.get('new_focal_brand_found'):
                cat_stats[cat]['mentions'] += 1
            if row.get('new_prominence') == 'featured_first':
                cat_stats[cat]['featured'] += 1

        categories = []
        for name, stats in cat_stats.items():
            tests = stats['tests']
            categories.append({
                "name": name,
                "tests": tests,
                "mentions": stats['mentions'],
                "featured": stats['featured'],
                "mentionRate": round(stats['mentions'] / tests * 100, 1) if tests > 0 else 0,
                "featuredRate": round(stats['featured'] / tests * 100, 1) if tests > 0 else 0,
                "sampleQuery": stats['sampleQuery']
            })

        categories.sort(key=lambda x: x['mentionRate'], reverse=True)
        return json.dumps(categories)

    def _prepare_platforms(self, insights: Any) -> str:
        """Prepare platform statistics."""
        platforms = []
        for p in insights.platform_metrics:
            platforms.append({
                "name": p.platform.replace('_', ' ').title(),
                "mentions": int(p.mention_rate * p.response_count / 100),
                "featured": int(p.featured_rate * p.response_count / 100),
                "tests": p.response_count,
                "mentionRate": round(p.mention_rate, 1),
                "featuredRate": round(p.featured_rate, 1),
                "best": p.prominence_score == max(pm.prominence_score for pm in insights.platform_metrics)
            })
        platforms.sort(key=lambda x: x['mentionRate'], reverse=True)
        return json.dumps(platforms)

    def _prepare_media_data(self, insights: Any) -> Dict[str, str]:
        """Prepare citation/media data by category with industry-aware classification."""
        cm = insights.citation_metrics
        brand_lower = insights.brand_name.lower().replace(' ', '').replace('-', '')

        # Detect hospitality industry
        hospitality_signals = ['hotel', 'resort', 'travel', 'booking', 'hospitality', 'lodging']
        domains_list = [d for d, c in cm.top_domains]
        is_hospitality = any(signal in insights.brand_name.lower() for signal in hospitality_signals) or \
                         any(any(signal in d.lower() for signal in ['hotel', 'booking.com', 'tripadvisor', 'expedia'])
                             for d in domains_list[:20])

        earned, owned, shopping, social, wikipedia, other = [], [], [], [], [], []

        # Industry-specific classification lists
        if is_hospitality:
            # HOSPITALITY earned media (travel press, trade, points/miles, reviews)
            earned_domains = [
                # Major travel publications
                'cntraveler', 'condenast', 'travelandleisure', 'travel+leisure',
                'afar', 'fodors', 'frommers', 'lonelyplanet', 'nationalgeographic',
                'travelandtourworld', 'luxurytraveladvisor', 'luxurytravelmag',
                'elitetraveler', 'tatler', 'departures', 'robbreport',
                # Hospitality trade press
                'hospitalitydesign', 'hospitalitynet', 'hotelmanagement',
                'skift', 'phocuswire', 'travelweekly', 'ttgmedia', 'hoteldive',
                'hoteliermiddleeast', 'hoteliermagazine', 'hotelnewsresource',
                'travelpulse', 'businesstraveller', 'travelmarketreport',
                'hotelbusiness', 'htrends', 'hospitalitytechnology',
                # Points/miles/loyalty sites
                'thepointsguy', 'pointsguy', 'onemileatatime', 'viewfromthewing',
                'frequentmiler', 'nerdwallet', 'upgradedpoints', 'milestomemories',
                'bankrate', 'thewiseflyer', 'god-save-the-points',
                # Travel reviews/rankings
                'travel.usnews', 'usnews.com/travel', 'jdpower', 'theluxurytravelexpert',
                'luxurylifestyleawards', 'worldtravelawards',
                # General news/business
                'forbes', 'nytimes', 'wsj', 'cnn', 'bbc', 'theguardian',
                'vogue', 'gq', 'esquire', 'architecturaldigest', 'dwell',
                'wallpaper', 'dezeen', 'designboom', 'homejournal',
                'michelin', 'timeout', 'insider', 'businessinsider',
            ]
            # HOSPITALITY shopping (travel booking & meta-search)
            shopping_domains = [
                'booking.com', 'expedia', 'hotels.com', 'tripadvisor', 'kayak',
                'agoda', 'trivago', 'priceline', 'orbitz', 'travelocity',
                'hotwire', 'makemytrip', 'hostelworld', 'airbnb', 'vrbo',
                'trip.com', 'ctrip', 'skyscanner', 'momondo', 'cheaptickets',
                'directbooker', 'cozycozy', 'getaroom', 'hopper',
                'travelzoo', 'secret-escapes', 'laterooms',
            ]
        else:
            # DEFAULT earned media (retail/consumer)
            earned_domains = [
                'forbes', 'gq', 'esquire', 'menshealth', 'womenshealth',
                'runnersworld', 'self', 'vogue', 'nytimes', 'wsj', 'cnn',
                'businessinsider', 'wired', 'techcrunch', 'theverge',
                'allure', 'glamour', 'refinery29', 'buzzfeed',
            ]
            # DEFAULT shopping (retail)
            shopping_domains = [
                'nordstrom', 'rei', 'amazon', 'zappos', 'dickssportinggoods',
                'target', 'walmart', 'macys', 'bestbuy', 'sephora', 'ulta',
                'bloomingdales', 'saksfifthavenue', 'neiman',
            ]

        # Social domains (same for all industries)
        social_domains = ['reddit', 'youtube', 'instagram', 'tiktok', 'twitter', 'facebook', 'pinterest', 'flyertalk']

        # System/platform domains to filter out entirely
        excluded_domains = [
            'vertexaisearch', 'googleusercontent', 'googleapis', 'gstatic',
            'cloudflare', 'cdn.', '.cdn', 'amazonaws', 's3.', 'azure',
            'blob.core', 'storage.', 'static.', 'assets.', 'media.',
            'googleads', 'doubleclick', 'googlesyndication', 'google.com/search',
        ]

        # Get competitor names for filtering
        competitor_names = [c.brand_name.lower().replace(' ', '').replace('-', '')
                           for c in insights.discovered_competitors[:15]]

        # Automotive-specific shopping (for BMW and similar)
        auto_shopping = ['carvana', 'carmax', 'autotrader', 'cars.com', 'truecar',
                        'edmunds', 'kbb', 'carfax', 'cargurus', 'autotempest',
                        'carsdirect', 'motor1', 'caranddriver', 'motortrend']

        for domain, count in cm.top_domains:
            d_lower = domain.lower()

            # Skip excluded system domains
            if any(x in d_lower for x in excluded_domains):
                continue

            entry = {
                "domain": domain,
                "total": count,
                "lulu": count if brand_lower in d_lower.replace('-', '') else int(count * 0.5),
                "luluPct": 100.0 if brand_lower in d_lower.replace('-', '') else 50.0,
                "type": self._classify_domain_type(domain, is_hospitality)
            }

            # Check if it's brand owned
            if brand_lower in d_lower.replace('-', ''):
                owned.append(entry)
            # Check if it's a competitor domain - exclude entirely (shown in competitive landscape)
            elif any(comp in d_lower.replace('-', '') for comp in competitor_names if len(comp) >= 3):
                continue  # Skip competitors - they're covered in competitive landscape section
            # Check for earned media
            elif any(x in d_lower for x in earned_domains):
                earned.append(entry)
            # Check for shopping/retail
            elif any(x in d_lower for x in shopping_domains) or any(x in d_lower for x in auto_shopping):
                shopping.append(entry)
            # Check for social
            elif any(x in d_lower for x in social_domains):
                social.append(entry)
            # Check for common blog patterns -> earned media
            elif any(x in d_lower for x in ['blog', 'medium.com', 'substack', 'wordpress', 'ghost.io', 'blogger', 'tumblr']):
                entry["type"] = "Blog"
                earned.append(entry)
            # Check for news sites -> earned media
            elif any(x in d_lower for x in ['news', 'times', 'post', 'journal', 'herald', 'gazette', 'tribune', 'daily', 'weekly', 'magazine', 'review', 'insider', 'report']):
                entry["type"] = "News"
                earned.append(entry)
            # Check for trade/industry publications -> earned media
            elif any(x in d_lower for x in ['trade', 'industry', 'professional', 'association', '.org']):
                entry["type"] = "Trade"
                earned.append(entry)
            # Check for reference sites
            elif 'wikipedia' in d_lower:
                entry["type"] = "Wikipedia"
                wikipedia.append(entry)
            else:
                other.append(entry)

        return {
            'earned': json.dumps(earned),
            'owned': json.dumps(owned),
            'shopping': json.dumps(shopping),
            'social': json.dumps(social),
            'wikipedia': json.dumps(wikipedia),
            'other': json.dumps(other)
        }

    def _classify_domain_type(self, domain: str, is_hospitality: bool = False) -> str:
        """Classify domain into type with industry awareness."""
        d = domain.lower()

        if is_hospitality:
            # Hospitality-specific types
            if any(x in d for x in ['cntraveler', 'travelandleisure', 'afar', 'lonelyplanet', 'departures']):
                return "Travel Magazine"
            elif any(x in d for x in ['thepointsguy', 'onemileatatime', 'frequentmiler', 'flyertalk',
                                       'nerdwallet', 'upgradedpoints', 'milestomemories', 'bankrate']):
                return "Points/Miles"
            elif any(x in d for x in ['hospitalitydesign', 'hospitalitynet', 'hotelmanagement', 'skift',
                                       'phocuswire', 'hoteldive', 'travelpulse', 'travelweekly',
                                       'businesstraveller', 'hotelbusiness', 'htrends']):
                return "Industry Trade"
            elif any(x in d for x in ['michelin', 'timeout', 'fodors', 'frommers', 'usnews', 'jdpower']):
                return "Travel Guide"
            elif any(x in d for x in ['booking', 'expedia', 'hotels.com', 'tripadvisor', 'kayak', 'agoda']):
                return "OTA"
            elif any(x in d for x in ['airbnb', 'vrbo']):
                return "Alternative Lodging"
            elif any(x in d for x in ['architecturaldigest', 'dwell', 'dezeen', 'wallpaper']):
                return "Design"
            elif any(x in d for x in ['tatler', 'vogue', 'gq', 'robbreport', 'elitetraveler']):
                return "Lifestyle"
            # Competitor hotel chains
            elif any(x in d for x in ['hilton', 'hyatt', 'ihg', 'accor', 'wyndham', 'choicehotels',
                                       'fourseasons', 'ritzcarlton', 'mandarinoriental', 'shangri-la',
                                       'peninsula', 'aman', 'belmond', 'rosewood', 'fairmont']):
                return "Competitor"

        # General classification (fallback for all industries)
        if any(x in d for x in ['forbes', 'businessinsider', 'wsj', 'nytimes']):
            return "Business/News"
        elif any(x in d for x in ['menshealth', 'womenshealth', 'self']):
            return "Health"
        elif any(x in d for x in ['runnersworld', 'irunfar']):
            return "Running"
        elif any(x in d for x in ['gq', 'vogue', 'esquire']):
            return "Fashion"
        elif any(x in d for x in ['amazon', 'nordstrom', 'rei']):
            return "Retail"
        elif any(x in d for x in ['reddit', 'youtube', 'instagram']):
            return "Social"
        elif any(x in d for x in ['wikipedia']):
            return "Reference"
        else:
            return "General"

    def _prepare_competitors(self, insights: Any) -> str:
        """Prepare competitor data with enhanced Share of Voice metrics."""
        comps = []

        # Calculate total mentions across all brands for SOV
        brand_mentions = insights.brand_metrics.mention_count
        total_competitor_mentions = sum(c.mention_count for c in insights.discovered_competitors[:15])
        total_all_mentions = brand_mentions + total_competitor_mentions

        for c in insights.discovered_competitors[:15]:
            # Calculate SOV percentage
            sov_pct = (c.mention_count / total_all_mentions * 100) if total_all_mentions > 0 else 0

            # Calculate co-occurrence rate (how often competitor appears when brand is mentioned)
            # This requires query_data which we'll compute in JavaScript
            total_h2h = c.head_to_head_wins + c.head_to_head_losses + getattr(c, 'head_to_head_ties', 0)
            h2h_win_rate = (c.head_to_head_wins / total_h2h * 100) if total_h2h > 0 else 0

            comps.append({
                "name": c.brand_name,
                "mentions": c.mention_count,
                "featured": c.featured_count,
                "h2hWins": c.head_to_head_wins,
                "h2hLosses": c.head_to_head_losses,
                "h2hTies": getattr(c, 'head_to_head_ties', 0),
                "sovPct": round(sov_pct, 1),
                "h2hWinRate": round(h2h_win_rate, 1)
            })
        return json.dumps(comps)

    def _prepare_share_of_voice(self, insights: Any, query_data: List[Dict]) -> str:
        """Prepare Share of Voice metrics for dashboard (UNBRANDED QUERIES ONLY)."""
        brand_name = insights.brand_name
        bm = insights.brand_metrics

        # Filter to UNBRANDED queries only (queries that don't contain brand name or competitor names)
        brand_lower = brand_name.lower()
        competitor_names_lower = [c.brand_name.lower() for c in insights.discovered_competitors[:15]]

        unbranded_queries = []
        for row in query_data:
            query_text = row.get('query_text', '').lower()
            # Check if query contains brand or competitor names
            is_branded = brand_lower in query_text or any(comp in query_text for comp in competitor_names_lower)
            if not is_branded:
                unbranded_queries.append(row)

        # Count brand mentions in UNBRANDED queries only
        brand_mentions_unbranded = sum(1 for r in unbranded_queries if r.get('new_focal_brand_found'))

        # Count competitor mentions in UNBRANDED queries only
        all_brand_mentions = {}
        all_brand_mentions[brand_name] = brand_mentions_unbranded

        for c in insights.discovered_competitors[:15]:
            comp_name_lower = c.brand_name.lower()
            # Count how many unbranded queries mentioned this competitor
            comp_mentions = sum(1 for r in unbranded_queries
                              if comp_name_lower in r.get('new_brands_mentioned', '').lower())
            all_brand_mentions[c.brand_name] = comp_mentions

        total_mentions = sum(all_brand_mentions.values())

        # Calculate SOV percentages
        sov_data = []
        brand_sov = (brand_mentions_unbranded / total_mentions * 100) if total_mentions > 0 else 0
        sov_data.append({
            "name": brand_name,
            "mentions": brand_mentions_unbranded,
            "sovPct": round(brand_sov, 1),
            "isTarget": True
        })

        for c in insights.discovered_competitors[:10]:
            # Use unbranded query mention counts
            comp_mentions_unbranded = all_brand_mentions.get(c.brand_name, 0)
            comp_sov = (comp_mentions_unbranded / total_mentions * 100) if total_mentions > 0 else 0
            sov_data.append({
                "name": c.brand_name,
                "mentions": comp_mentions_unbranded,
                "sovPct": round(comp_sov, 1),
                "isTarget": False
            })

        # Calculate Featured Share (who wins #1 positions) - UNBRANDED queries only
        featured_share = {}

        # Count brand's featured wins in unbranded queries
        brand_featured_unbranded = sum(1 for r in unbranded_queries
                                      if r.get('new_prominence') == 'featured_first')
        featured_share[brand_name] = brand_featured_unbranded

        # Count competitor featured wins in unbranded queries
        for c in insights.discovered_competitors[:10]:
            comp_name = c.brand_name
            # Count featured wins where this competitor was the primary winner
            comp_featured = sum(1 for r in unbranded_queries
                              if r.get('new_primary_competitor', '') == comp_name or
                              (r.get('new_prominence') != 'featured_first' and comp_name in r.get('new_brands_mentioned', '')))
            featured_share[comp_name] = comp_featured

        total_featured = sum(featured_share.values())

        featured_data = []
        for name, count in sorted(featured_share.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_featured * 100) if total_featured > 0 else 0
            featured_data.append({
                "name": name,
                "featured": count,
                "pct": round(pct, 1),
                "isTarget": name == brand_name
            })

        return json.dumps({
            "sov": sov_data,
            "featuredShare": featured_data[:10],
            "brandSovPct": round(brand_sov, 1),
            "brandFeaturedPct": round((brand_featured_unbranded / total_featured * 100) if total_featured > 0 else 0, 1),
            "totalMentions": total_mentions,
            "totalFeatured": total_featured,
            "unbrandedQueryCount": len(unbranded_queries),
            "totalQueryCount": len(query_data)
        })

    def _prepare_citation_tiers(self, insights: Any) -> str:
        """Prepare citation tier data for dashboard."""
        cm = insights.citation_metrics

        # Get tier counts with safe fallbacks
        tier1 = getattr(cm, 'tier1_citations', 0)
        tier2 = getattr(cm, 'tier2_citations', 0)
        tier3 = getattr(cm, 'tier3_citations', 0)
        untiered = getattr(cm, 'untiered_citations', 0)
        quality_score = getattr(cm, 'citation_quality_score', 0)

        total = tier1 + tier2 + tier3 + untiered
        if total == 0:
            total = cm.total_citations or 1

        return json.dumps({
            "tier1": tier1,
            "tier2": tier2,
            "tier3": tier3,
            "untiered": untiered,
            "tier1Pct": round(tier1 / total * 100, 1) if total > 0 else 0,
            "tier2Pct": round(tier2 / total * 100, 1) if total > 0 else 0,
            "tier3Pct": round(tier3 / total * 100, 1) if total > 0 else 0,
            "untieredPct": round(untiered / total * 100, 1) if total > 0 else 0,
            "qualityScore": round(quality_score, 1),
            "total": total
        })

    def _prepare_sentiment_data(self, insights: Any) -> str:
        """Prepare sentiment distribution data for dashboard."""
        bm = insights.brand_metrics

        positive = getattr(bm, 'positive_sentiment_rate', 0)
        neutral = getattr(bm, 'neutral_sentiment_rate', 0)
        negative = getattr(bm, 'negative_sentiment_rate', 0)

        # Calculate sentiment score (weighted: positive=1, neutral=0, negative=-1)
        total = positive + neutral + negative
        if total > 0:
            sentiment_score = ((positive * 1) + (neutral * 0) + (negative * -1)) / 100
            # Normalize to 0-100 scale (where 50 is neutral)
            sentiment_score = 50 + (sentiment_score * 50)
        else:
            sentiment_score = 50

        return json.dumps({
            "positive": round(positive, 1),
            "neutral": round(neutral, 1),
            "negative": round(negative, 1),
            "sentimentScore": round(sentiment_score, 1)
        })

    def _prepare_media_intelligence(self, insights: Any, query_data: List[Dict]) -> str:
        """Prepare owned and earned media intelligence data."""
        if not MEDIA_INTEL_AVAILABLE:
            return json.dumps({
                "owned": {"summary": "Media intelligence not available", "recommendations": []},
                "earned": {"summary": "Media intelligence not available", "strengths": [], "opportunities": []}
            })

        try:
            engine = MediaIntelligenceEngine()

            # Get owned domains from insights
            owned_domains = getattr(insights, 'owned_domains', [])
            if not owned_domains:
                # Try to infer from brand name
                brand_lower = insights.brand_name.lower().replace(' ', '')
                owned_domains = [f"{brand_lower}.com"]

            # Get competitor info
            competitor_data = []
            for c in insights.discovered_competitors[:10]:
                comp_name = c.brand_name.lower().replace(' ', '')
                competitor_data.append({
                    'name': c.brand_name,
                    'owned_domains': [f"{comp_name}.com"]
                })

            owned_insight, earned_insight = engine.analyze(
                query_data=query_data,
                brand_name=insights.brand_name,
                owned_domains=owned_domains,
                competitor_data=competitor_data
            )

            return prepare_media_intelligence_js(owned_insight, earned_insight)

        except Exception as e:
            return json.dumps({
                "owned": {"summary": f"Analysis error: {str(e)}", "recommendations": []},
                "earned": {"summary": "Analysis unavailable", "strengths": [], "opportunities": []}
            })

    def _prepare_content_conversion(self, insights: Any) -> str:
        """Prepare Content Conversion Rate data for JS embedding."""
        cm = insights.citation_metrics
        return json.dumps({
            "timesCited": cm.times_brand_cited,
            "winsWhenCited": cm.wins_when_cited,
            "conversionRate": round(cm.content_conversion_rate, 1),
            "consultedNotConverted": cm.times_brand_cited - cm.wins_when_cited,
            "ownedCitations": cm.owned_citations,
            "editorialCitations": cm.editorial_citations,
            "retailCitations": cm.retail_citations,
            "socialCitations": cm.social_citations,
            "otherCitations": cm.other_citations,
            "totalCitations": cm.total_citations,
        })

    def _prepare_branded_unbranded(self, insights: Any) -> str:
        """Prepare branded/unbranded split data for JS embedding."""
        bm = insights.brand_metrics
        return json.dumps({
            "branded": {
                "total": bm.branded_total,
                "mentions": bm.branded_mention_count,
                "mentionRate": round(bm.branded_mention_rate, 1),
                "featured": bm.branded_featured_first_count,
                "featuredRate": round(bm.branded_featured_first_rate, 1),
            },
            "unbranded": {
                "total": bm.unbranded_total,
                "mentions": bm.unbranded_mention_count,
                "mentionRate": round(bm.unbranded_mention_rate, 1),
                "featured": bm.unbranded_featured_first_count,
                "featuredRate": round(bm.unbranded_featured_first_rate, 1),
                "topRate": round(bm.unbranded_top_rate, 1),
            },
            "aeoScore": round(bm.aeo_score, 1),
        })

    def _legacy_media_vars(self, media_data_js: Dict) -> str:
        """Generate legacy JS variable declarations for hardcoded media tabs."""
        return f"""const earnedMedia = {media_data_js['earned']};
        const ownedMedia = {media_data_js['owned']};
        const shoppingMedia = {media_data_js['shopping']};
        const socialMedia = {media_data_js['social']};
        const wikipediaMedia = {media_data_js['wikipedia']};
        const otherMedia = {media_data_js['other']};
        const citationCategories = null;"""

    def _prepare_adaptive_citations(self, classified_citations: Dict) -> str:
        """Convert classified_citations dict to JS-embeddable JSON.

        Input: OrderedDict of {category_name: [{"domain": str, "total": int}, ...]}
        Output: JSON string for embedding as citationCategories JS variable
        """
        # Add lulu/brand percentage placeholders (the classifier doesn't know this)
        js_data = {}
        for cat_name, entries in classified_citations.items():
            js_entries = []
            for e in entries:
                js_entries.append({
                    "domain": e["domain"],
                    "total": e["total"],
                    "type": cat_name,
                })
            js_data[cat_name] = js_entries
        return json.dumps(js_data)

    def _section_citations_adaptive(self, classified_citations: Dict) -> str:
        """Generate citation sources section with dynamic, adaptive tabs."""
        if not classified_citations:
            return self._section_citations()

        # Build tab buttons and content panes dynamically
        tab_buttons = []
        tab_panes = []
        first = True
        for cat_name in classified_citations.keys():
            tab_id = cat_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '-')
            active = ' active' if first else ''
            count = len(classified_citations[cat_name])
            total_cites = sum(e['total'] for e in classified_citations[cat_name])

            tab_buttons.append(
                f'<button class="toggle-btn{active}" onclick="showTab(\'{tab_id}\', this)">'
                f'{cat_name} <span style="opacity:0.6;font-size:0.75em;">({total_cites})</span></button>'
            )
            tab_panes.append(
                f'<div class="tab-content{active}" id="tab-{tab_id}">'
                f'<div class="media-list" id="{tab_id}-media-list"></div>'
                f'</div>'
            )
            first = False

        return f'''
        <section>
            <h2 class="section-title">Citation Sources</h2>
            <p class="section-subtitle">Sources AI platforms reference most, classified by type. Categories are adaptive to the brand\'s industry.</p>

            <div class="tab-container">
                <div class="tab-header">
                    {"".join(tab_buttons)}
                </div>
                {"".join(tab_panes)}
            </div>
        </section>
        '''

    def _section_content_conversion(self, insights: Any) -> str:
        """Generate Content Conversion Rate analysis section (v17)."""
        cm = insights.citation_metrics
        brand = insights.brand_name
        consulted_not_converted = cm.times_brand_cited - cm.wins_when_cited
        return f'''
        <section>
            <h2 class="section-title">Content Conversion Analysis</h2>
            <p class="section-subtitle">When {brand}'s website is cited by AI, does the brand win? Citation ≠ Recommendation.</p>
            <div class="kpi-grid">
                <div class="kpi-card" onclick="toggleKpi(this)">
                    <div class="kpi-value" style="color: var(--accent-cyan);">{cm.times_brand_cited}</div>
                    <div class="kpi-label">Times Brand Cited</div>
                    <div class="kpi-expand">Number of responses where {brand}'s owned domain appears in citation URLs.</div>
                </div>
                <div class="kpi-card" onclick="toggleKpi(this)">
                    <div class="kpi-value" style="color: var(--status-good);">{cm.wins_when_cited}</div>
                    <div class="kpi-label">Wins When Cited</div>
                    <div class="kpi-expand">Number of times {brand} was featured #1 when its own site was cited.</div>
                </div>
                <div class="kpi-card" onclick="toggleKpi(this)">
                    <div class="kpi-value" style="color: var(--accent-primary);">{cm.content_conversion_rate:.1f}%</div>
                    <div class="kpi-label">Conversion Rate</div>
                    <div class="kpi-expand">Wins when cited / times cited. Higher means AI trusts and recommends the brand when it references its content.</div>
                </div>
                <div class="kpi-card" onclick="toggleKpi(this)">
                    <div class="kpi-value" style="color: var(--status-warn);">{consulted_not_converted}</div>
                    <div class="kpi-label">Consulted, Not Converted</div>
                    <div class="kpi-expand">AI referenced {brand}'s content but recommended a competitor instead. Signals content quality or positioning gaps.</div>
                </div>
            </div>
            <div class="competitive-grid" style="margin-top: 1.5rem;">
                <div class="chart-container">
                    <div class="chart-title">Citation Tier Breakdown</div>
                    <div id="citation-tier-bars"></div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Citation Type Distribution</div>
                    <div id="citation-type-pie"></div>
                </div>
            </div>
        </section>
        '''

    def _section_methodology(self, insights: Any) -> str:
        """Generate Methodology section with limitations (v17 requirement)."""
        bm = insights.brand_metrics
        brand = insights.brand_name
        total = bm.total_responses
        platforms = len(insights.platform_metrics)
        queries = bm.total_queries

        return f'''
        <section>
            <h2 class="section-title">Methodology</h2>
            <div class="chart-container">
                <div class="chart-title">Study Configuration</div>
                <p style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.8;">
                    This analysis collected {total} AI responses across {platforms} platforms ({queries} unique queries × {platforms} platforms).
                    All platforms were configured with web search (RAG) enabled where available to ensure comparable, real-time results.
                    Competitors were <strong>discovered from data</strong>, not pre-specified, to eliminate confirmation bias.
                    AEO Score is calculated on unbranded queries only: (Featured Rate × 0.7) + (Top 3 Rate × 0.3).
                </p>
                <div class="chart-title" style="margin-top: 1.5rem;">Limitations</div>
                <ol style="color: var(--text-secondary); font-size: 0.8rem; line-height: 2; padding-left: 1.5rem;">
                    <li><strong>Temporal snapshot</strong> — Results represent one point in time; AI responses vary by session and may change daily.</li>
                    <li><strong>Query phrasing sensitivity</strong> — Different wording of the same intent can yield materially different results.</li>
                    <li><strong>Sample size</strong> — {total} tests provide directional intelligence but may not achieve statistical significance across all segments.</li>
                    <li><strong>No causation</strong> — Correlations between media presence and AI wins do not imply causation.</li>
                    <li><strong>Algorithm evolution</strong> — Platform ranking algorithms change continuously; results may not be reproducible.</li>
                    <li><strong>Classification subjectivity</strong> — Brand mention detection and prominence scoring involve heuristic judgment.</li>
                    <li><strong>RAG variability</strong> — Web search availability and depth varies by platform and user settings.</li>
                    <li><strong>Competitive incompleteness</strong> — Competitor discovery captures brands AI mentions but may miss market players AI doesn't reference.</li>
                    <li><strong>Geographic bias</strong> — Results may vary by user location, language, and personalization settings.</li>
                </ol>
            </div>
        </section>
        '''

    def _nav_bubbles(self) -> str:
        """Generate fixed navigation bubbles (Lululemon v6 style)."""
        return '''
    <nav class="nav-bubbles">
        <a href="#s-overview" class="nav-bubble" data-section="s-overview"><span class="nav-bubble-label">Overview</span></a>
        <a href="#s-conversion" class="nav-bubble" data-section="s-conversion"><span class="nav-bubble-label">Conversion</span></a>
        <a href="#s-sov" class="nav-bubble" data-section="s-sov"><span class="nav-bubble-label">Share of Voice</span></a>
        <a href="#s-competitive" class="nav-bubble" data-section="s-competitive"><span class="nav-bubble-label">Competitive</span></a>
        <a href="#s-categories" class="nav-bubble" data-section="s-categories"><span class="nav-bubble-label">Categories</span></a>
        <a href="#s-platforms" class="nav-bubble" data-section="s-platforms"><span class="nav-bubble-label">Platforms</span></a>
        <a href="#s-position" class="nav-bubble" data-section="s-position"><span class="nav-bubble-label">Position</span></a>
        <a href="#s-media" class="nav-bubble" data-section="s-media"><span class="nav-bubble-label">Media</span></a>
        <a href="#s-queries" class="nav-bubble" data-section="s-queries"><span class="nav-bubble-label">Queries</span></a>
        <a href="#s-methodology" class="nav-bubble" data-section="s-methodology"><span class="nav-bubble-label">Methodology</span></a>
    </nav>
        '''

    def _get_styles(self) -> str:
        """Return CSS styles matching reference dashboard."""
        return '''
        :root {
            --bg-body: #000000;
            --bg-card: #141414;
            --bg-card-soft: #1a1a1a;
            --bg-card-hover: #222222;
            --border: #2a2a2a;
            --border-light: #333333;
            --text-primary: #ffffff;
            --text-secondary: #b8b8b8;
            --text-muted: #8a8a8a;
            --accent-primary: #D31334;
            --accent-secondary: #a00f28;
            --status-good: #4CAF7C;
            --status-warn: #C4A77D;
            --status-risk: #E57373;
            --status-info: #4DD4E4;
            --accent-cyan: #4DD4E4;
            --accent-green: #4CAF7C;
            --accent-coral: #E57373;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Poppins', sans-serif; background: var(--bg-body); color: var(--text-primary); line-height: 1.6; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }

        /* Header */
        .header { text-align: center; margin-bottom: 2rem; padding-top: 2rem; }
        .brand-title { font-size: 2rem; font-weight: 300; letter-spacing: 0.1em; margin-bottom: 0.25rem; }
        .brand-title span { color: var(--accent-primary); }
        .subtitle { font-size: 1rem; font-weight: 300; color: var(--text-secondary); }

        .metadata-bar { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin: 1.5rem 0 2rem 0; padding: 1rem; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border); }
        .metadata-item { text-align: center; }
        .metadata-value { font-size: 1.5rem; font-weight: 300; color: var(--accent-primary); }
        .metadata-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; }

        .section-title { font-size: 1.6rem; font-weight: 300; letter-spacing: 0.04em; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
        .section-subtitle { font-size: 0.85rem; color: var(--text-secondary); margin: -1rem 0 1.5rem 0; }
        section { margin-top: 3rem; }

        /* Hero Grid */
        .hero-grid { display: grid; grid-template-columns: 220px 1fr; gap: 2rem; align-items: start; margin-bottom: 2rem; }

        /* Score Ring */
        .score-ring-container { display: flex; flex-direction: column; align-items: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; transition: all 0.3s ease; }
        .score-ring-container:hover { border-color: var(--border-light); box-shadow: 0 0 15px rgba(211,19,52,0.12), 0 2px 8px rgba(0,0,0,0.1); }
        .score-ring { position: relative; width: 180px; height: 180px; }
        .score-ring-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
        .ring-track { fill: none; stroke: var(--bg-card-soft); stroke-width: 6; }
        .ring-fill { fill: none; stroke-width: 6; stroke-linecap: round; transition: stroke-dashoffset 1s ease-out; }
        .ring-fill.branded { stroke: var(--accent-cyan); }
        .ring-fill.top3 { stroke: var(--accent-green); }
        .ring-fill.featured { stroke: var(--accent-coral); }
        .score-ring-value { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; }
        .score-ring-number { font-size: 2.5rem; font-weight: 300; }
        .score-ring-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; }
        .ring-legend { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1.25rem; width: 100%; }
        .ring-legend-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; }
        .ring-legend-left { display: flex; align-items: center; gap: 0.5rem; }
        .ring-legend-dot { width: 10px; height: 10px; border-radius: 50%; }
        .ring-legend-dot.cyan { background: var(--accent-cyan); }
        .ring-legend-dot.green { background: var(--accent-green); }
        .ring-legend-dot.coral { background: var(--accent-coral); }

        /* KPI Cards */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
        .kpi-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .kpi-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; cursor: pointer; transition: all 0.3s ease; }
        .kpi-card:hover { border-color: var(--accent-primary); box-shadow: 0 0 20px rgba(211,19,52,0.25), 0 2px 12px rgba(211,19,52,0.15); }
        .kpi-value { font-size: 1.8rem; font-weight: 300; color: var(--accent-primary); line-height: 1; }
        .kpi-label { font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem; }
        .kpi-expand { display: none; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.85rem; color: var(--text-secondary); }
        .kpi-card.expanded .kpi-expand { display: block; }

        /* Platform Filter Buttons */
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
        .section-header .section-title { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
        .platform-filter-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .platform-btn { background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px; padding: 0.4rem 0.9rem; font-family: inherit; font-size: 0.75rem; font-weight: 400; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease; }
        .platform-btn:hover { border-color: var(--text-muted); color: var(--text-primary); }
        .platform-btn.active { background: var(--accent-primary); border-color: var(--accent-primary); color: white; }

        /* Competitive Grid */
        .competitive-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
        .chart-container { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; transition: all 0.3s ease; }
        .chart-container:hover { border-color: var(--border-light); box-shadow: 0 0 15px rgba(211,19,52,0.12), 0 2px 8px rgba(0,0,0,0.1); }
        .chart-title { font-size: 1rem; font-weight: 500; margin-bottom: 1rem; }
        .bar-chart { display: flex; flex-direction: column; gap: 0.5rem; }
        .bar-row { display: grid; grid-template-columns: 120px 1fr 60px; gap: 0.75rem; align-items: center; }
        .bar-label { font-size: 0.8rem; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-secondary); }
        .bar-track { height: 20px; background: var(--bg-card-soft); border-radius: 4px; overflow: hidden; }
        .bar-fill { height: 100%; background: #666; border-radius: 4px; }
        .bar-fill.highlight { background: var(--accent-primary); }
        .bar-value { font-size: 0.8rem; color: var(--text-secondary); }

        /* Category Grid */
        .category-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
        .category-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; transition: all 0.3s ease; }
        .category-card:hover { border-color: var(--border-light); }
        .category-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
        .category-name { font-size: 0.95rem; font-weight: 500; }
        .status-chip { font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 500; }
        .status-chip.leading { background: rgba(76,175,124,0.2); color: var(--status-good); }
        .status-chip.competitive { background: rgba(196,167,125,0.2); color: var(--status-warn); }
        .status-chip.developing { background: rgba(77,212,228,0.2); color: var(--status-info); }
        .status-chip.opportunity { background: rgba(229,115,115,0.2); color: var(--status-risk); }
        .category-sample { font-size: 0.75rem; color: var(--text-muted); font-style: italic; margin-bottom: 0.75rem; }
        .category-stats { display: flex; gap: 1rem; margin-bottom: 0.75rem; }
        .category-stat { text-align: center; }
        .category-stat-value { font-size: 1.25rem; font-weight: 300; color: var(--accent-primary); }
        .category-stat-label { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; }
        .progress-track { height: 4px; background: var(--bg-card-soft); border-radius: 2px; overflow: hidden; }
        .progress-fill { height: 100%; background: var(--accent-primary); border-radius: 2px; }

        .sort-controls { display: flex; gap: 0.5rem; }
        .sort-btn { background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px; padding: 0.4rem 0.8rem; font-family: inherit; font-size: 0.75rem; color: var(--text-secondary); cursor: pointer; }
        .sort-btn:hover { border-color: var(--text-muted); }
        .sort-btn.active { background: var(--accent-primary); border-color: var(--accent-primary); color: white; }

        /* Platform Grid */
        .platform-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; }
        .platform-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; text-align: center; transition: all 0.3s ease; }
        .platform-card:hover { border-color: var(--border-light); }
        .platform-card.best { border-color: var(--status-good); background: rgba(76,175,124,0.05); }
        .platform-name { font-size: 0.85rem; font-weight: 500; margin-bottom: 0.75rem; }
        .platform-mention { font-size: 2rem; font-weight: 300; color: var(--accent-primary); }
        .platform-label { font-size: 0.7rem; color: var(--text-secondary); }
        .platform-details { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-secondary); }

        /* Citation Tabs */
        .tab-container { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
        .tab-header { display: flex; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
        .toggle-btn { flex: 1; padding: 1rem; background: transparent; border: none; color: var(--text-secondary); cursor: pointer; font-family: inherit; font-size: 0.85rem; min-width: 120px; }
        .toggle-btn.active { background: var(--bg-card-soft); color: var(--accent-primary); border-bottom: 2px solid var(--accent-primary); }
        .tab-content { display: none; padding: 1.5rem; }
        .tab-content.active { display: block; }
        .media-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .media-row { display: grid; grid-template-columns: 180px 1fr 100px; gap: 1rem; align-items: center; }
        .media-domain { font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-primary); }
        .media-bar-container { position: relative; height: 20px; }
        .media-bar-track { position: absolute; top: 0; left: 0; height: 100%; background: var(--bg-card-soft); border-radius: 4px; }
        .media-bar-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 4px; }
        .media-bar-fill.high { background: var(--status-good); opacity: 0.7; }
        .media-bar-fill.medium { background: var(--status-warn); opacity: 0.7; }
        .media-bar-fill.low { background: var(--status-risk); opacity: 0.7; }
        .media-pct { font-size: 0.75rem; color: var(--text-secondary); text-align: right; }
        .media-type-tag { display: inline-block; font-size: 0.6rem; padding: 0.15rem 0.4rem; border-radius: 3px; margin-left: 0.5rem; background: var(--bg-card-soft); color: var(--text-muted); }

        /* Query Table */
        .query-filters { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; margin-bottom: 1.5rem; }
        .query-filters select { background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 0.5rem 0.75rem; color: var(--text-primary); font-family: inherit; font-size: 0.8rem; }
        .query-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        .query-table th { text-align: left; padding: 0.75rem; border-bottom: 1px solid var(--border); color: var(--text-secondary); font-weight: 500; cursor: pointer; }
        .query-table th:hover { color: var(--text-primary); }
        .query-table td { padding: 0.75rem; border-bottom: 1px solid var(--border); }
        .query-table tr:hover { background: var(--bg-card-soft); }
        .query-text { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .mention-yes { color: var(--status-good); }
        .mention-no { color: var(--text-muted); }
        .results-counter { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem; }

        /* Share of Voice Section */
        .sov-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .sov-grid-simplified { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .sov-pie-card { display: flex; flex-direction: column; align-items: center; }
        .sov-pie-container { display: flex; justify-content: center; padding: 1rem 0; }
        .sov-pie-legend { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; padding: 0.5rem 0; }
        .sov-legend-item { display: flex; align-items: center; gap: 0.4rem; padding: 0.3rem 0.6rem; background: var(--bg-card-soft); border-radius: 4px; font-size: 0.75rem; }
        .sov-legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
        .sov-legend-name { color: var(--text-primary); white-space: nowrap; }
        .sov-legend-pct { color: var(--text-secondary); font-weight: 500; }
        .chart-subtitle { font-size: 0.75rem; color: var(--text-muted); margin: -0.5rem 0 1rem 0; }
        .section-subtitle { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.5rem; }
        .h2h-grid { display: flex; flex-direction: column; gap: 0.5rem; }
        .h2h-row { display: grid; grid-template-columns: 100px 1fr 80px; gap: 0.75rem; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
        .h2h-competitor { font-size: 0.8rem; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .h2h-bar-container { display: flex; gap: 2px; height: 20px; }
        .h2h-bar { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
        .h2h-bar.win { background: var(--status-good); }
        .h2h-bar.loss { background: var(--status-risk); }
        .h2h-bar.tie { background: var(--text-muted); }
        .h2h-stats { font-size: 0.75rem; color: var(--text-secondary); text-align: right; }
        .h2h-win-rate { font-weight: 500; }
        .h2h-win-rate.positive { color: var(--status-good); }
        .h2h-win-rate.negative { color: var(--status-risk); }
        .h2h-win-rate.neutral { color: var(--text-muted); }

        /* Citation Tier Styles */
        .tier-summary-grid { display: grid; grid-template-columns: 200px 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
        .tier-quality-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; text-align: center; }
        .tier-quality-score { font-size: 3rem; font-weight: 300; color: var(--accent-primary); line-height: 1; }
        .tier-quality-label { font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; }
        .tier-quality-desc { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.75rem; }
        .tier-breakdown-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }
        .tier-bar-container { display: flex; height: 24px; border-radius: 4px; overflow: hidden; background: var(--bg-card-soft); }
        .tier-bar { height: 100%; transition: width 0.5s ease; }
        .tier-bar.tier1 { background: var(--status-good); }
        .tier-bar.tier2 { background: var(--status-info); }
        .tier-bar.tier3 { background: var(--status-warn); }
        .tier-bar.untiered { background: var(--text-muted); }
        .tier-legend { display: flex; gap: 1.5rem; margin-top: 1rem; flex-wrap: wrap; }
        .tier-legend-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: var(--text-secondary); }
        .tier-dot { width: 12px; height: 12px; border-radius: 3px; }
        .tier-dot.tier1 { background: var(--status-good); }
        .tier-dot.tier2 { background: var(--status-info); }
        .tier-dot.tier3 { background: var(--status-warn); }
        .tier-dot.untiered { background: var(--text-muted); }
        .tier-legend-desc { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.75rem; }

        /* Sentiment Breakdown */
        .sentiment-breakdown { margin-bottom: 0.75rem; }
        .sentiment-bar-container { display: flex; height: 12px; border-radius: 3px; overflow: hidden; background: var(--bg-card-soft); margin-bottom: 0.5rem; }
        .sentiment-bar { height: 100%; transition: width 0.5s ease; }
        .sentiment-bar.positive { background: var(--status-good); }
        .sentiment-bar.neutral { background: var(--text-muted); }
        .sentiment-bar.negative { background: var(--status-risk); }
        .sentiment-legend { display: flex; gap: 1rem; font-size: 0.7rem; flex-wrap: wrap; }
        .sentiment-item { display: flex; align-items: center; gap: 0.25rem; }
        .sentiment-dot { width: 8px; height: 8px; border-radius: 50%; }
        .sentiment-dot.positive { background: var(--status-good); }
        .sentiment-dot.neutral { background: var(--text-muted); }
        .sentiment-dot.negative { background: var(--status-risk); }

        /* Media Intelligence Cards */
        .media-intel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .owned-content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .owned-kpis { display: flex; gap: 2rem; margin-bottom: 1rem; }
        .owned-kpi { flex: 1; }
        .owned-kpi-value { font-size: 2rem; font-weight: 300; color: var(--accent-primary); line-height: 1.2; }
        .owned-kpi-value.positive { color: var(--status-good); }
        .owned-kpi-value.negative { color: var(--status-risk); }
        .owned-kpi-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
        .owned-kpi-desc { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.35rem; }
        .owned-summary { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; }
        .competitor-owned-table { display: flex; flex-direction: column; gap: 0.5rem; }
        .competitor-owned-row { display: grid; grid-template-columns: 1fr 80px 80px; gap: 0.5rem; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
        .competitor-owned-row.header { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; border-bottom: 1px solid var(--border-light); }
        .competitor-owned-name { font-size: 0.8rem; color: var(--text-primary); }
        .competitor-owned-value { font-size: 0.8rem; text-align: right; }
        .competitor-owned-value.positive { color: var(--status-good); }
        .competitor-owned-value.negative { color: var(--status-risk); }
        .media-intel-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }
        .media-intel-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
        .media-intel-icon { font-family: monospace; font-size: 1.25rem; color: var(--accent-primary); }
        .media-intel-title { font-size: 1rem; font-weight: 500; color: var(--text-primary); }
        .media-intel-kpis { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
        .media-intel-kpi { text-align: center; flex: 1; }
        .media-intel-kpi-value { font-size: 1.5rem; font-weight: 300; color: var(--accent-primary); line-height: 1.2; }
        .media-intel-kpi-value.positive { color: var(--status-good); }
        .media-intel-kpi-value.negative { color: var(--status-risk); }
        .media-intel-kpi-label { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
        .media-intel-kpi-desc { font-size: 0.65rem; color: var(--text-muted); margin-top: 0.35rem; font-style: italic; }
        .media-intel-intro { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem; }
        .media-intel-summary { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.5; }
        .media-intel-recommendations { font-size: 0.8rem; color: var(--text-muted); }
        .media-intel-recommendations ul { margin: 0; padding-left: 1.25rem; }
        .media-intel-recommendations li { margin-bottom: 0.5rem; }
        .media-intel-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1rem; }
        .media-intel-col-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
        .media-intel-count { font-size: 0.75rem; color: var(--text-muted); }
        .media-intel-col-desc { font-size: 0.7rem; color: var(--text-muted); margin-bottom: 0.75rem; }
        .media-outlet-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 200px; overflow-y: auto; }
        .media-outlet-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.75rem; background: var(--bg-card-soft); border-radius: 4px; font-size: 0.8rem; }
        .media-outlet-domain { color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px; }
        .media-outlet-type { font-size: 0.6rem; color: var(--text-muted); margin-left: 0.5rem; }
        .media-outlet-stat { font-size: 0.75rem; white-space: nowrap; }
        .media-outlet-stat.positive { color: var(--status-good); }
        .media-outlet-stat.negative { color: var(--status-risk); }

        @media (max-width: 1200px) {
            .media-intel-grid { grid-template-columns: 1fr; }
            .tier-summary-grid { grid-template-columns: 1fr; }
            .sov-grid { grid-template-columns: 1fr; }
            .platform-grid { grid-template-columns: repeat(3, 1fr); }
            .competitive-grid { grid-template-columns: 1fr; }
            .position-grid { grid-template-columns: 1fr; }
        }
        @media (max-width: 768px) {
            .hero-grid { grid-template-columns: 1fr; }
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
            .kpi-grid-3 { grid-template-columns: 1fr; }
            .platform-grid { grid-template-columns: repeat(2, 1fr); }
            .sov-grid-simplified { grid-template-columns: 1fr; }
            .nav-bubbles { display: none; }
        }

        /* Position Analysis (Lululemon v6 style) */
        .position-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
        .position-chart { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; }
        .position-bar { display: flex; height: 40px; border-radius: 4px; overflow: hidden; margin-bottom: 1rem; }
        .position-segment { display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 500; min-width: 30px; }
        .position-segment.pos-1 { background: #4caf50; color: #fff; }
        .position-segment.pos-2 { background: #8bc34a; color: #fff; }
        .position-segment.pos-3 { background: #ffc107; color: #000; }
        .position-segment.pos-4 { background: #ff9800; color: #fff; }
        .position-legend { display: flex; gap: 1rem; flex-wrap: wrap; }
        .position-legend-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; color: var(--text-secondary); }
        .position-dot { width: 12px; height: 12px; border-radius: 3px; }
        .metric-expandable { transition: all 0.2s ease; }
        .metric-expandable:hover { opacity: 0.8; }

        /* Status Chips */
        .status-chip { font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 500; }
        .status-chip.leading { background: rgba(76,175,124,0.2); color: var(--status-good); }
        .status-chip.competitive { background: rgba(196,167,125,0.2); color: var(--status-warn); }
        .status-chip.developing { background: rgba(77,212,228,0.2); color: var(--status-info); }
        .status-chip.opportunity { background: rgba(229,115,115,0.2); color: var(--status-risk); }

        /* Navigation Bubbles (Lululemon v6 style) */
        .nav-bubbles {
            position: fixed;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            z-index: 1000;
        }
        .nav-bubble {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--border);
            position: relative;
            cursor: pointer;
            transition: all 0.2s ease;
            display: block;
            text-decoration: none;
        }
        .nav-bubble:hover,
        .nav-bubble.active {
            background: var(--accent-primary);
            transform: scale(1.3);
        }
        .nav-bubble-label {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--text-primary);
            color: var(--bg-body);
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }
        .nav-bubble:hover .nav-bubble-label {
            opacity: 1;
        }
        @media print {
            .nav-bubbles { display: none; }
        }
        '''

    def _section_header(self, insights: Any) -> str:
        """Generate header section."""
        bm = insights.brand_metrics
        return f'''
        <header class="header">
            <h1 class="brand-title"><span>{insights.brand_name}</span> AI Citation Intelligence</h1>
            <p class="subtitle">Answer Engine Optimization Dashboard</p>
        </header>

        <div class="metadata-bar">
            <div class="metadata-item">
                <div class="metadata-value">{bm.total_responses}</div>
                <div class="metadata-label">Total Tests</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-value">{len(insights.platform_metrics)}</div>
                <div class="metadata-label">AI Platforms</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-value">{bm.total_queries}</div>
                <div class="metadata-label">Unique Queries</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-value">{len(insights.discovered_competitors)}</div>
                <div class="metadata-label">Competitors</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-value">{insights.citation_metrics.total_citations}</div>
                <div class="metadata-label">Citations</div>
            </div>
        </div>
        '''

    def _section_hero(self, insights: Any) -> str:
        """Generate hero section with score ring and 8 KPIs (v17)."""
        bm = insights.brand_metrics
        cm = insights.citation_metrics

        # Use unbranded metrics for score ring (v17: unbranded is the real competitive test)
        mention_rate = bm.unbranded_mention_rate if bm.unbranded_total > 0 else bm.mention_rate
        featured_rate = bm.unbranded_featured_first_rate if bm.unbranded_total > 0 else bm.featured_first_rate
        top_rate = bm.unbranded_top_rate if bm.unbranded_total > 0 else (bm.featured_first_rate + bm.recommended_rate)
        aeo_score = bm.aeo_score if bm.aeo_score > 0 else bm.visibility_score

        # Competitive rank label
        rank_label = f"#{bm.competitive_rank}" if bm.competitive_rank > 0 else "N/A"

        return f'''
        <section>
            <div class="section-header">
                <h2 class="section-title">Executive Summary</h2>
                <div class="platform-filter-btns" id="exec-filter-btns">
                    <button class="platform-btn active" onclick="filterExecutiveSummary('all', this)">All</button>
                    <button class="platform-btn" onclick="filterExecutiveSummary('chatgpt', this)">ChatGPT</button>
                    <button class="platform-btn" onclick="filterExecutiveSummary('claude', this)">Claude</button>
                    <button class="platform-btn" onclick="filterExecutiveSummary('perplexity', this)">Perplexity</button>
                    <button class="platform-btn" onclick="filterExecutiveSummary('gemini', this)">Gemini</button>
                    <button class="platform-btn" onclick="filterExecutiveSummary('meta_llama', this)">Meta Llama</button>
                </div>
            </div>
            <div class="hero-grid">
                <div class="score-ring-container">
                    <div class="score-ring">
                        <svg class="score-ring-svg" viewBox="0 0 100 100">
                            <circle class="ring-track" cx="50" cy="50" r="45"/>
                            <circle class="ring-fill branded" id="ring-mention" cx="50" cy="50" r="45" data-percent="{mention_rate:.1f}"/>
                            <circle class="ring-track" cx="50" cy="50" r="36"/>
                            <circle class="ring-fill top3" id="ring-top3" cx="50" cy="50" r="36" data-percent="{top_rate:.1f}"/>
                            <circle class="ring-track" cx="50" cy="50" r="27"/>
                            <circle class="ring-fill featured" id="ring-featured" cx="50" cy="50" r="27" data-percent="{featured_rate:.1f}"/>
                        </svg>
                        <div class="score-ring-value">
                            <div class="score-ring-number" id="aeo-score">{aeo_score:.0f}</div>
                            <div class="score-ring-label">AEO Score</div>
                        </div>
                    </div>
                    <div class="ring-legend">
                        <div class="ring-legend-row">
                            <div class="ring-legend-left"><div class="ring-legend-dot cyan"></div><span class="ring-legend-label">Mentioned</span></div>
                            <span class="ring-legend-value" id="legend-mention">{mention_rate:.1f}%</span>
                        </div>
                        <div class="ring-legend-row">
                            <div class="ring-legend-left"><div class="ring-legend-dot green"></div><span class="ring-legend-label">Top 3</span></div>
                            <span class="ring-legend-value" id="legend-top3">{top_rate:.1f}%</span>
                        </div>
                        <div class="ring-legend-row">
                            <div class="ring-legend-left"><div class="ring-legend-dot coral"></div><span class="ring-legend-label">Featured #1</span></div>
                            <span class="ring-legend-value" id="legend-featured">{featured_rate:.1f}%</span>
                        </div>
                    </div>
                </div>

                <div>
                    <div class="kpi-grid">
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-aeo">{aeo_score:.0f}</div>
                            <div class="kpi-label">AEO Score</div>
                            <div class="kpi-expand">Composite score: (Featured Rate × 0.7) + (Top 3 Rate × 0.3) on unbranded queries. Range 0-100.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-rank">{rank_label}</div>
                            <div class="kpi-label">Competitive Rank</div>
                            <div class="kpi-expand">Brand's rank among all discovered competitors by mention frequency. Competitors discovered from data, not pre-specified.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-branded">{bm.branded_mention_rate:.0f}%</div>
                            <div class="kpi-label">Branded Performance</div>
                            <div class="kpi-expand">Mention rate on branded queries (quality gate). Should be ~100%. {bm.branded_total} branded tests.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-mention">{mention_rate:.1f}%</div>
                            <div class="kpi-label">Unbranded Mentioned</div>
                            <div class="kpi-expand">Percentage of unbranded queries where {insights.brand_name} is mentioned. The true competitive test. {bm.unbranded_total} tests.</div>
                        </div>
                    </div>
                    <div class="kpi-grid" style="margin-top: 1rem;">
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-featured">{featured_rate:.1f}%</div>
                            <div class="kpi-label">Unbranded Featured</div>
                            <div class="kpi-expand">Percentage of unbranded queries where {insights.brand_name} is the #1 recommendation.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-conversion">{cm.content_conversion_rate:.1f}%</div>
                            <div class="kpi-label">Content Conversion</div>
                            <div class="kpi-expand">When {insights.brand_name}'s site is cited, how often does it win? {cm.wins_when_cited} wins / {cm.times_brand_cited} cited. "Consulted Not Converted" = {cm.times_brand_cited - cm.wins_when_cited}.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-citations">{cm.total_citations:,}</div>
                            <div class="kpi-label">Total Citations</div>
                            <div class="kpi-expand">Total citation URLs extracted across all AI responses. Classified by tier: {cm.owned_citations} owned, {cm.editorial_citations} editorial, {cm.retail_citations} retail.</div>
                        </div>
                        <div class="kpi-card" onclick="toggleKpi(this)">
                            <div class="kpi-value" id="kpi-variance">{bm.platform_variance:.0f}pts</div>
                            <div class="kpi-label">Platform Variance</div>
                            <div class="kpi-expand">Spread between best and worst performing platforms. High variance (&gt;20pts) suggests platform-specific optimization opportunities.</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        '''

    def _section_share_of_voice(self) -> str:
        """Generate Share of Voice analysis section - simplified with pie chart and LLM filter."""
        return '''
        <section>
            <div class="section-header">
                <h2 class="section-title">Share of Voice</h2>
                <div class="platform-filter-btns" id="sov-filter-btns">
                    <button class="platform-btn active" onclick="filterSOV('all', this)">All</button>
                    <button class="platform-btn" onclick="filterSOV('chatgpt', this)">ChatGPT</button>
                    <button class="platform-btn" onclick="filterSOV('claude', this)">Claude</button>
                    <button class="platform-btn" onclick="filterSOV('perplexity', this)">Perplexity</button>
                    <button class="platform-btn" onclick="filterSOV('gemini', this)">Gemini</button>
                    <button class="platform-btn" onclick="filterSOV('meta_llama', this)">Meta Llama</button>
                </div>
            </div>
            <div class="sov-grid-simplified">
                <div class="chart-container sov-pie-card">
                    <div class="chart-title">Brand Share of Voice</div>
                    <p class="chart-subtitle">Unbranded queries only — who gets mentioned when no specific brand is requested</p>
                    <div class="sov-pie-container" id="sov-pie-chart"></div>
                    <div class="sov-pie-legend" id="sov-pie-legend"></div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Co-occurrence Analysis</div>
                    <p class="chart-subtitle">Which competitors appear when your brand is mentioned</p>
                    <div class="bar-chart" id="cooccurrence-chart"></div>
                </div>
            </div>
        </section>
        '''

    def _section_competitive(self) -> str:
        """Generate competitive analysis section."""
        return '''
        <section>
            <div class="section-header">
                <h2 class="section-title">Competitive Landscape</h2>
                <div class="platform-filter-btns" id="competitive-filter-btns">
                    <button class="platform-btn active" onclick="filterCompetitiveByLLM('all', this)">All</button>
                    <button class="platform-btn" onclick="filterCompetitiveByLLM('chatgpt', this)">ChatGPT</button>
                    <button class="platform-btn" onclick="filterCompetitiveByLLM('claude', this)">Claude</button>
                    <button class="platform-btn" onclick="filterCompetitiveByLLM('perplexity', this)">Perplexity</button>
                    <button class="platform-btn" onclick="filterCompetitiveByLLM('gemini', this)">Gemini</button>
                    <button class="platform-btn" onclick="filterCompetitiveByLLM('meta_llama', this)">Meta Llama</button>
                </div>
            </div>

            <div class="competitive-grid">
                <div class="chart-container">
                    <div class="chart-title">Share of Voice (Mentions)</div>
                    <div class="bar-chart" id="mention-chart"></div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Featured First Wins</div>
                    <div class="bar-chart" id="featured-chart"></div>
                </div>
            </div>
        </section>
        '''

    def _section_media_intelligence(self) -> str:
        """Generate media intelligence section for owned content effectiveness with competitor comparison."""
        return '''
        <section>
            <h2 class="section-title">Owned Content Effectiveness</h2>
            <div class="owned-content-grid">
                <div class="chart-container">
                    <div class="chart-title">Your Performance</div>
                    <div class="owned-kpis">
                        <div class="owned-kpi">
                            <div class="owned-kpi-value" id="owned-citation-rate">--</div>
                            <div class="owned-kpi-label">Citation Rate</div>
                            <div class="owned-kpi-desc">% of AI responses citing your owned domains</div>
                        </div>
                        <div class="owned-kpi">
                            <div class="owned-kpi-value" id="owned-lift">--</div>
                            <div class="owned-kpi-label">Win Rate Lift</div>
                            <div class="owned-kpi-desc">Featured rate improvement when your content is cited</div>
                        </div>
                    </div>
                    <div class="owned-summary" id="owned-summary"></div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Competitor Comparison</div>
                    <p class="chart-subtitle">How competitors' owned content performs in AI citations</p>
                    <div class="competitor-owned-table" id="competitor-owned-table"></div>
                </div>
            </div>
        </section>
        '''

    def _section_categories(self) -> str:
        """Generate category performance section."""
        return '''
        <section>
            <div class="section-header">
                <h2 class="section-title">Category Performance</h2>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <div class="platform-filter-btns" id="category-filter-btns">
                        <button class="platform-btn active" onclick="filterCategoriesByLLM('all', this)">All</button>
                        <button class="platform-btn" onclick="filterCategoriesByLLM('chatgpt', this)">ChatGPT</button>
                        <button class="platform-btn" onclick="filterCategoriesByLLM('claude', this)">Claude</button>
                        <button class="platform-btn" onclick="filterCategoriesByLLM('perplexity', this)">Perplexity</button>
                        <button class="platform-btn" onclick="filterCategoriesByLLM('gemini', this)">Gemini</button>
                        <button class="platform-btn" onclick="filterCategoriesByLLM('meta_llama', this)">Meta Llama</button>
                    </div>
                    <div class="sort-controls">
                        <button class="sort-btn active" onclick="sortCategories('mention', this)">By Mention</button>
                        <button class="sort-btn" onclick="sortCategories('featured', this)">By Featured</button>
                        <button class="sort-btn" onclick="sortCategories('alpha', this)">A-Z</button>
                    </div>
                </div>
            </div>
            <div class="category-grid" id="category-grid"></div>
        </section>
        '''

    def _section_platforms(self) -> str:
        """Generate platform comparison section."""
        return '''
        <section>
            <h2 class="section-title">Platform Comparison</h2>
            <div class="platform-grid" id="platform-grid"></div>
        </section>
        '''

    def _section_position_analysis(self, insights: Any) -> str:
        """Generate Position Analysis section (Lululemon v6 style)."""
        bm = insights.brand_metrics
        brand = insights.brand_name
        # Compute initial position data from brand metrics
        mentioned_total = bm.mention_count or 1
        pos1 = bm.featured_first_count
        pos2 = bm.recommended_count
        pos3 = bm.listed_count
        pos4 = bm.mentioned_only_count
        pos1_pct = round(pos1 / mentioned_total * 100, 1) if mentioned_total else 0
        pos2_pct = round(pos2 / mentioned_total * 100, 1) if mentioned_total else 0
        pos3_pct = round(pos3 / mentioned_total * 100, 1) if mentioned_total else 0
        pos4_pct = round(pos4 / mentioned_total * 100, 1) if mentioned_total else 0
        win_rate = round(pos1 / mentioned_total * 100, 1) if mentioned_total else 0
        top3 = pos1 + pos2 + pos3
        top3_rate = round(top3 / mentioned_total * 100, 1) if mentioned_total else 0

        return f'''
        <section>
            <div class="section-header">
                <h2 class="section-title">Position Analysis</h2>
                <div class="platform-filter-btns" id="position-filter-btns">
                    <button class="platform-btn active" data-llm="all" onclick="filterPositionByLLM('all', this)">All Platforms</button>
                </div>
            </div>
            <p class="section-subtitle">When {brand} is mentioned, where does it appear in the response?</p>
            <div class="position-grid">
                <div class="position-chart">
                    <div class="chart-title">Position Distribution</div>
                    <div class="position-bar" id="position-bar">
                        <div class="position-segment pos-1" style="flex: {pos1_pct};">{pos1_pct}%</div>
                        <div class="position-segment pos-2" style="flex: {pos2_pct};">{pos2_pct}%</div>
                        <div class="position-segment pos-3" style="flex: {pos3_pct};">{pos3_pct}%</div>
                        <div class="position-segment pos-4" style="flex: {pos4_pct};">{pos4_pct}%</div>
                    </div>
                    <div class="position-legend">
                        <div class="position-legend-item"><div class="position-dot" style="background: #4caf50;"></div>1st (Featured)</div>
                        <div class="position-legend-item"><div class="position-dot" style="background: #8bc34a;"></div>2nd-3rd (Recommended)</div>
                        <div class="position-legend-item"><div class="position-dot" style="background: #ffc107;"></div>4th-5th (Listed)</div>
                        <div class="position-legend-item"><div class="position-dot" style="background: #ff9800;"></div>Mentioned Only</div>
                    </div>
                </div>
                <div class="position-chart">
                    <div class="chart-title">Conversion Metrics</div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">Click each metric to see definition.</p>
                    <div style="display: flex; gap: 2rem;">
                        <div class="metric-expandable" onclick="toggleMetricDef(this)" style="text-align: center; cursor: pointer;">
                            <div style="font-size: 2.5rem; font-weight: 300; color: var(--accent-primary);" id="conversion-rate">{win_rate}%</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">Visibility &rarr; Win Rate</div>
                            <div class="metric-definition" style="display: none; margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-card-soft); border-radius: 6px; font-size: 0.8rem; color: var(--text-secondary); text-align: left;">
                                <strong>Definition:</strong> Of the {mentioned_total} responses where {brand} was mentioned, {pos1} featured it as the #1 recommendation ({win_rate}%). This measures how often visibility converts to a win.
                            </div>
                        </div>
                        <div class="metric-expandable" onclick="toggleMetricDef(this)" style="text-align: center; cursor: pointer;">
                            <div style="font-size: 2.5rem; font-weight: 300; color: var(--status-good);" id="top3-rate">{top3_rate}%</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">Top-3 Placement</div>
                            <div class="metric-definition" style="display: none; margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-card-soft); border-radius: 6px; font-size: 0.8rem; color: var(--text-secondary); text-align: left;">
                                <strong>Definition:</strong> Of the {mentioned_total} responses where {brand} was mentioned, {top3} placed it in positions 1, 2, or 3 ({top3_rate}%). High top-3 rate indicates consistent prominent placement when visible.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        '''

    def _section_citations(self) -> str:
        """Generate citation analysis section with tabs."""
        return '''
        <section>
            <h2 class="section-title">Citation Sources</h2>
            <p class="section-subtitle">Top 10 most-cited sources in AI responses, grouped by type. These are the sources AI platforms reference most - regardless of traditional media tiers.</p>

            <div class="tab-container">
                <div class="tab-header">
                    <button class="toggle-btn active" onclick="showTab('earned', this)">Earned Media</button>
                    <button class="toggle-btn" onclick="showTab('owned', this)">Owned Media</button>
                    <button class="toggle-btn" onclick="showTab('shopping', this)">Shopping/Retail</button>
                    <button class="toggle-btn" onclick="showTab('social', this)">Social & Community</button>
                    <button class="toggle-btn" onclick="showTab('wikipedia', this)">Wikipedia</button>
                    <button class="toggle-btn" onclick="showTab('other', this)">Other</button>
                </div>
                <div class="tab-content active" id="tab-earned">
                    <div class="media-list" id="earned-media-list"></div>
                </div>
                <div class="tab-content" id="tab-owned">
                    <div class="media-list" id="owned-media-list"></div>
                </div>
                <div class="tab-content" id="tab-shopping">
                    <div class="media-list" id="shopping-media-list"></div>
                </div>
                <div class="tab-content" id="tab-social">
                    <div class="media-list" id="social-media-list"></div>
                </div>
                <div class="tab-content" id="tab-wikipedia">
                    <div class="media-list" id="wikipedia-media-list"></div>
                </div>
                <div class="tab-content" id="tab-other">
                    <div class="media-list" id="other-media-list"></div>
                </div>
            </div>
        </section>
        '''

    def _section_query_appendix(self) -> str:
        """Generate query appendix section."""
        return '''
        <section>
            <h2 class="section-title">Query Appendix</h2>

            <div class="query-filters">
                <div class="platform-filter-btns" id="query-platform-btns">
                    <button class="platform-btn active" data-platform="all" onclick="filterQueriesByPlatform('all', this)">All</button>
                    <button class="platform-btn" data-platform="chatgpt" onclick="filterQueriesByPlatform('chatgpt', this)">ChatGPT</button>
                    <button class="platform-btn" data-platform="claude" onclick="filterQueriesByPlatform('claude', this)">Claude</button>
                    <button class="platform-btn" data-platform="perplexity" onclick="filterQueriesByPlatform('perplexity', this)">Perplexity</button>
                    <button class="platform-btn" data-platform="gemini" onclick="filterQueriesByPlatform('gemini', this)">Gemini</button>
                    <button class="platform-btn" data-platform="meta_llama" onclick="filterQueriesByPlatform('meta_llama', this)">Meta Llama</button>
                </div>
                <select id="filter-category" onchange="filterQueries()">
                    <option value="all">All Categories</option>
                </select>
                <select id="filter-mentioned" onchange="filterQueries()">
                    <option value="all">All Mentioned</option>
                    <option value="Yes">Mentioned</option>
                    <option value="No">Not Mentioned</option>
                </select>
                <select id="filter-featured" onchange="filterQueries()">
                    <option value="all">All Featured</option>
                    <option value="Yes">Featured</option>
                    <option value="No">Not Featured</option>
                </select>
            </div>

            <p class="results-counter" id="results-counter">Showing 0 results</p>

            <div style="overflow-x: auto;">
                <table class="query-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Query</th>
                            <th onclick="sortTable(1)">Category</th>
                            <th onclick="sortTable(2)">Platform</th>
                            <th onclick="sortTable(3)">Mentioned</th>
                            <th onclick="sortTable(4)">Ranking</th>
                            <th onclick="sortTable(5)">Featured Brand</th>
                        </tr>
                    </thead>
                    <tbody id="query-tbody"></tbody>
                </table>
            </div>
        </section>
        '''

    def _get_scripts(self) -> str:
        """Return JavaScript for interactivity."""
        return '''
        document.addEventListener('DOMContentLoaded', function() {
            initScoreRings();
            initNavigation();
            populatePositionFilterBtns();
            renderContentConversion();
            renderShareOfVoice();
            renderMentionChart();
            renderFeaturedChart();
            renderCategoryGrid();
            renderPlatformGrid();
            renderMediaTabs();
            populateCategoryFilter();
            renderQueryTable();
        });

        function initScoreRings() {
            const rings = document.querySelectorAll('.ring-fill');
            rings.forEach((ring, index) => {
                const percent = parseFloat(ring.dataset.percent);
                const radius = parseFloat(ring.getAttribute('r'));
                const circumference = 2 * Math.PI * radius;

                ring.style.strokeDasharray = circumference;
                ring.style.strokeDashoffset = circumference;

                setTimeout(() => {
                    const offset = circumference * (1 - percent / 100);
                    ring.style.strokeDashoffset = offset;
                }, 300 + (index * 200));
            });
        }

        function toggleKpi(card) { card.classList.toggle('expanded'); }

        function initNavigation() {
            const sections = document.querySelectorAll('div[id^="s-"]');
            const navBubbles = document.querySelectorAll('.nav-bubble');
            if (!navBubbles.length) return;

            // Smooth scroll on click
            navBubbles.forEach(bubble => {
                bubble.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('data-section');
                    const target = document.getElementById(targetId);
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            });

            // Scroll-tracking active state
            window.addEventListener('scroll', function() {
                let current = '';
                sections.forEach(function(section) {
                    if (window.scrollY >= section.offsetTop - 200) {
                        current = section.getAttribute('id');
                    }
                });
                navBubbles.forEach(function(bubble) {
                    bubble.classList.remove('active');
                    if (bubble.getAttribute('data-section') === current) {
                        bubble.classList.add('active');
                    }
                });
            });
        }

        function renderContentConversion() {
            // Citation Tier Bars
            const tierContainer = document.getElementById('citation-tier-bars');
            if (tierContainer && tierData) {
                const tiers = [
                    { label: 'Tier 1 (Major Press)', count: tierData.tier1, color: 'var(--accent-primary)' },
                    { label: 'Tier 2 (Trade/Specialty)', count: tierData.tier2, color: 'var(--status-warn)' },
                    { label: 'Tier 3 (Blogs/UGC)', count: tierData.tier3, color: 'var(--text-muted)' },
                    { label: 'Other', count: tierData.untiered, color: 'var(--border-light)' }
                ];
                const maxCount = Math.max(...tiers.map(t => t.count), 1);
                tierContainer.innerHTML = tiers.map(t => {
                    const pct = (t.count / maxCount * 100).toFixed(0);
                    return '<div class="bar-row"><div class="bar-label">' + t.label + '</div>' +
                        '<div class="bar-track"><div class="bar-fill" style="width:' + pct + '%;background:' + t.color + '"></div></div>' +
                        '<div class="bar-value">' + t.count + '</div></div>';
                }).join('');
            }

            // Citation Type Distribution (simple horizontal stacked)
            const pieContainer = document.getElementById('citation-type-pie');
            if (pieContainer && contentConversion) {
                const cc = contentConversion;
                const total = cc.totalCitations || 1;
                const types = [
                    { label: 'Owned', count: cc.ownedCitations, color: 'var(--accent-primary)' },
                    { label: 'Editorial', count: cc.editorialCitations, color: 'var(--accent-cyan)' },
                    { label: 'Retail', count: cc.retailCitations, color: 'var(--status-warn)' },
                    { label: 'Social', count: cc.socialCitations, color: 'var(--status-good)' },
                    { label: 'Other', count: cc.otherCitations, color: 'var(--text-muted)' }
                ].filter(t => t.count > 0);

                // Stacked bar
                let barHtml = '<div style="display:flex;height:24px;border-radius:4px;overflow:hidden;margin-bottom:1rem;">';
                types.forEach(t => {
                    const pct = (t.count / total * 100).toFixed(1);
                    barHtml += '<div style="width:' + pct + '%;background:' + t.color + ';min-width:2px;" title="' + t.label + ': ' + t.count + ' (' + pct + '%)"></div>';
                });
                barHtml += '</div>';

                // Legend
                barHtml += '<div style="display:flex;flex-wrap:wrap;gap:1rem;">';
                types.forEach(t => {
                    const pct = (t.count / total * 100).toFixed(1);
                    barHtml += '<div style="display:flex;align-items:center;gap:0.4rem;font-size:0.8rem;color:var(--text-secondary);">' +
                        '<div style="width:10px;height:10px;border-radius:50%;background:' + t.color + ';"></div>' +
                        t.label + ' <span style="color:var(--text-primary);">' + t.count + '</span> (' + pct + '%)' +
                        '</div>';
                });
                barHtml += '</div>';

                pieContainer.innerHTML = barHtml;
            }
        }

        let currentExecFilter = 'all';
        let currentSovFilter = 'all';

        function filterExecutiveSummary(llmFilter, btn) {
            currentExecFilter = llmFilter;
            document.querySelectorAll('#exec-filter-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter query data
            const filtered = llmFilter === 'all' ? queryData : queryData.filter(q => q.engine.toLowerCase().replace(' ', '_') === llmFilter);
            const total = filtered.length;
            if (total === 0) return;

            // Calculate filtered metrics
            const mentioned = filtered.filter(q => q.mentioned === 'Yes').length;
            const featured = filtered.filter(q => q.featured === 'Yes').length;
            const top3 = filtered.filter(q => ['1st', '2nd', '3rd'].includes(q.position)).length;

            const mentionRate = Math.round(mentioned / total * 100 * 10) / 10;
            const featuredRate = Math.round(featured / total * 100 * 10) / 10;
            const top3Rate = Math.round(top3 / total * 100 * 10) / 10;
            const aeoScore = Math.round((featuredRate * 0.7) + (top3Rate * 0.3));

            // Update KPIs
            document.getElementById('kpi-mention').textContent = mentionRate + '%';
            document.getElementById('kpi-top3').textContent = top3Rate + '%';
            document.getElementById('kpi-featured').textContent = featuredRate + '%';
            document.getElementById('aeo-score').textContent = aeoScore;

            // Update legend
            document.getElementById('legend-mention').textContent = mentionRate + '%';
            document.getElementById('legend-top3').textContent = top3Rate + '%';
            document.getElementById('legend-featured').textContent = featuredRate + '%';

            // Update rings with animation
            updateRing('ring-mention', mentionRate);
            updateRing('ring-top3', top3Rate);
            updateRing('ring-featured', featuredRate);
        }

        function updateRing(ringId, percent) {
            const ring = document.getElementById(ringId);
            if (!ring) return;
            const radius = parseFloat(ring.getAttribute('r'));
            const circumference = 2 * Math.PI * radius;
            const offset = circumference * (1 - percent / 100);
            ring.style.strokeDashoffset = offset;
        }

        function filterSOV(llmFilter, btn) {
            currentSovFilter = llmFilter;
            document.querySelectorAll('#sov-filter-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderShareOfVoice(llmFilter);
        }

        function renderMediaIntelligence() {
            if (!mediaIntelligence || !mediaIntelligence.owned) return;

            const owned = mediaIntelligence.owned;

            // Owned Content KPIs
            const citationRateEl = document.getElementById('owned-citation-rate');
            if (citationRateEl) {
                citationRateEl.textContent = (owned.brandCitationRate || 0) + '%';
            }

            const liftEl = document.getElementById('owned-lift');
            if (liftEl) {
                const lift = owned.ownedLift || 0;
                liftEl.textContent = (lift > 0 ? '+' : '') + lift + 'pp';
                liftEl.className = 'owned-kpi-value ' + (lift > 5 ? 'positive' : lift < -5 ? 'negative' : '');
            }

            // Owned Summary
            const ownedSummary = document.getElementById('owned-summary');
            if (ownedSummary) ownedSummary.textContent = owned.summary || '';

            // Competitor Comparison Table
            const compTable = document.getElementById('competitor-owned-table');
            if (compTable && owned.competitorComparison) {
                const comps = owned.competitorComparison;
                let tableHtml = '<div class="competitor-owned-row header"><div>Competitor</div><div>Citation Rate</div><div>Win Lift</div></div>';
                tableHtml += comps.slice(0, 8).map(c => {
                    const liftClass = c.lift > 5 ? 'positive' : c.lift < -5 ? 'negative' : '';
                    return '<div class="competitor-owned-row">' +
                        '<div class="competitor-owned-name">' + c.name + '</div>' +
                        '<div class="competitor-owned-value">' + c.citationRate + '%</div>' +
                        '<div class="competitor-owned-value ' + liftClass + '">' + (c.lift > 0 ? '+' : '') + c.lift + 'pp</div>' +
                        '</div>';
                }).join('');
                compTable.innerHTML = tableHtml;
            } else if (compTable) {
                compTable.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No competitor owned content data available.</p>';
            }
        }

        function toggleMetricDef(el) {
            const def = el.querySelector('.metric-definition');
            if (def) def.style.display = def.style.display === 'none' ? 'block' : 'none';
        }

        function populatePositionFilterBtns() {
            const container = document.getElementById('position-filter-btns');
            if (!container) return;
            const engines = [...new Set(queryData.map(q => q.engine))].sort();
            engines.forEach(eng => {
                const btn = document.createElement('button');
                btn.className = 'platform-btn';
                btn.setAttribute('data-llm', eng);
                btn.onclick = function() { filterPositionByLLM(eng, this); };
                btn.textContent = eng.charAt(0).toUpperCase() + eng.slice(1).replace('_', ' ');
                container.appendChild(btn);
            });
        }

        function filterPositionByLLM(llm, btn) {
            document.querySelectorAll('#position-filter-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            let filtered = queryData;
            if (llm !== 'all') filtered = queryData.filter(q => q.engine === llm);

            const mentioned = filtered.filter(q => q.mentioned === 'Yes');
            const total = mentioned.length || 1;

            // Map position labels to categories
            const pos1 = mentioned.filter(q => q.position === '1st').length;
            const pos2 = mentioned.filter(q => ['2nd', '3rd'].includes(q.position)).length;
            const pos3 = mentioned.filter(q => ['4th', '5th'].includes(q.position)).length;
            const pos4 = mentioned.filter(q => !['1st','2nd','3rd','4th','5th','Not Present'].includes(q.position) && q.position !== 'Not Present').length;

            const pos1Pct = ((pos1 / total) * 100).toFixed(1);
            const pos2Pct = ((pos2 / total) * 100).toFixed(1);
            const pos3Pct = ((pos3 / total) * 100).toFixed(1);
            const pos4Pct = ((pos4 / total) * 100).toFixed(1);

            const posBar = document.getElementById('position-bar');
            if (posBar) {
                posBar.innerHTML =
                    '<div class="position-segment pos-1" style="flex:'+pos1Pct+';">'+pos1Pct+'%</div>'+
                    '<div class="position-segment pos-2" style="flex:'+pos2Pct+';">'+pos2Pct+'%</div>'+
                    '<div class="position-segment pos-3" style="flex:'+pos3Pct+';">'+pos3Pct+'%</div>'+
                    '<div class="position-segment pos-4" style="flex:'+pos4Pct+';">'+pos4Pct+'%</div>';
            }

            const featured = pos1;
            const top3 = pos1 + pos2;
            const crEl = document.getElementById('conversion-rate');
            const t3El = document.getElementById('top3-rate');
            if (crEl) crEl.textContent = ((featured / total) * 100).toFixed(1) + '%';
            if (t3El) t3El.textContent = ((top3 / total) * 100).toFixed(1) + '%';
        }

        function renderShareOfVoice(llmFilter) {
            llmFilter = llmFilter || 'all';

            // Filter data by LLM if specified
            const filtered = llmFilter === 'all' ? queryData : queryData.filter(q => q.engine.toLowerCase().replace(' ', '_') === llmFilter);

            // Calculate SOV from filtered data
            const brandMentions = {};
            brandMentions[brandName] = filtered.filter(q => q.mentioned === 'Yes').length;

            filtered.forEach(q => {
                if (q.competitors) {
                    q.competitors.split('|').forEach(comp => {
                        comp = comp.trim();
                        if (comp) brandMentions[comp] = (brandMentions[comp] || 0) + 1;
                    });
                }
            });

            const totalMentions = Object.values(brandMentions).reduce((a, b) => a + b, 0);
            const sovCalc = Object.entries(brandMentions)
                .map(([name, count]) => ({
                    name,
                    mentions: count,
                    sovPct: totalMentions > 0 ? Math.round(count / totalMentions * 1000) / 10 : 0,
                    isTarget: name === brandName
                }))
                .sort((a, b) => b.sovPct - a.sovPct)
                .slice(0, 10);

            // Render SOV as an actual pie chart
            const pieContainer = document.getElementById('sov-pie-chart');
            const legendContainer = document.getElementById('sov-pie-legend');

            // Colors for pie segments
            const colors = ['#D31334', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'];

            // Create SVG pie chart
            let cumulativePercent = 0;
            const pieSegments = sovCalc.map((item, i) => {
                const startAngle = cumulativePercent * 3.6 * (Math.PI / 180);
                cumulativePercent += item.sovPct;
                const endAngle = cumulativePercent * 3.6 * (Math.PI / 180);

                const x1 = 50 + 45 * Math.cos(startAngle - Math.PI/2);
                const y1 = 50 + 45 * Math.sin(startAngle - Math.PI/2);
                const x2 = 50 + 45 * Math.cos(endAngle - Math.PI/2);
                const y2 = 50 + 45 * Math.sin(endAngle - Math.PI/2);

                const largeArc = item.sovPct > 50 ? 1 : 0;
                const color = item.isTarget ? '#D31334' : colors[i % colors.length];

                return '<path d="M50,50 L' + x1 + ',' + y1 + ' A45,45 0 ' + largeArc + ',1 ' + x2 + ',' + y2 + ' Z" fill="' + color + '" stroke="var(--bg-card)" stroke-width="1"/>';
            }).join('');

            pieContainer.innerHTML = '<svg viewBox="0 0 100 100" style="width: 180px; height: 180px;">' + pieSegments + '</svg>';

            // Create legend
            legendContainer.innerHTML = sovCalc.map((item, i) => {
                const color = item.isTarget ? '#D31334' : colors[i % colors.length];
                return '<div class="sov-legend-item"><span class="sov-legend-dot" style="background:' + color + '"></span><span class="sov-legend-name">' + item.name + '</span><span class="sov-legend-pct">' + item.sovPct + '%</span></div>';
            }).join('');

            // Render co-occurrence chart (which competitors appear when brand is mentioned)
            const cooccContainer = document.getElementById('cooccurrence-chart');
            const cooccurrence = {};

            // Count how often each competitor appears in responses where brand is mentioned
            // EXCLUDE the primary brand itself from this chart
            filtered.forEach(q => {
                if (q.mentioned === 'Yes' && q.competitors) {
                    q.competitors.split('|').forEach(comp => {
                        comp = comp.trim();
                        // Filter out the primary brand name (case insensitive)
                        if (comp && comp.toLowerCase() !== brandName.toLowerCase()) {
                            cooccurrence[comp] = (cooccurrence[comp] || 0) + 1;
                        }
                    });
                }
            });

            const filteredBrandMentions = filtered.filter(q => q.mentioned === 'Yes').length;
            const cooccSorted = Object.entries(cooccurrence)
                .map(([name, count]) => ({ name, count, rate: filteredBrandMentions > 0 ? Math.round(count / filteredBrandMentions * 100) : 0 }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 8);

            const maxCooc = Math.max(...cooccSorted.map(c => c.count)) || 1;
            cooccContainer.innerHTML = cooccSorted.map(c =>
                '<div class="bar-row"><div class="bar-label">' + c.name + '</div><div class="bar-track"><div class="bar-fill" style="width:' + (c.count / maxCooc * 100) + '%"></div></div><div class="bar-value">' + c.rate + '%</div></div>'
            ).join('');
        }

        function renderCitationTiers() {
            // Update quality score
            document.getElementById('tier-quality-score').textContent = tierData.qualityScore.toFixed(0);

            // Update tier percentages
            document.getElementById('tier1-pct').textContent = tierData.tier1Pct + '%';
            document.getElementById('tier2-pct').textContent = tierData.tier2Pct + '%';
            document.getElementById('tier3-pct').textContent = tierData.tier3Pct + '%';
            document.getElementById('untiered-pct').textContent = tierData.untieredPct + '%';

            // Animate tier bars
            setTimeout(() => {
                document.getElementById('tier1-bar').style.width = tierData.tier1Pct + '%';
                document.getElementById('tier2-bar').style.width = tierData.tier2Pct + '%';
                document.getElementById('tier3-bar').style.width = tierData.tier3Pct + '%';
                document.getElementById('untiered-bar').style.width = tierData.untieredPct + '%';
            }, 300);
        }

        function renderSentimentBreakdown() {
            // Update sentiment percentages
            document.getElementById('sentiment-pos-pct').textContent = sentimentData.positive + '%';
            document.getElementById('sentiment-neu-pct').textContent = sentimentData.neutral + '%';
            document.getElementById('sentiment-neg-pct').textContent = sentimentData.negative + '%';

            // Animate sentiment bars
            setTimeout(() => {
                document.getElementById('sentiment-pos-bar').style.width = sentimentData.positive + '%';
                document.getElementById('sentiment-neu-bar').style.width = sentimentData.neutral + '%';
                document.getElementById('sentiment-neg-bar').style.width = sentimentData.negative + '%';
            }, 300);
        }

        function renderMentionChart(llmFilter) {
            const container = document.getElementById('mention-chart');
            let filtered = queryData;
            if (llmFilter && llmFilter !== 'all') filtered = queryData.filter(q => q.engine.toLowerCase().replace(' ', '_') === llmFilter);

            const compMentions = {};
            filtered.forEach(q => {
                if (q.mentioned === 'Yes') compMentions[brandName] = (compMentions[brandName] || 0) + 1;
                if (q.competitors) {
                    q.competitors.split('|').forEach(comp => {
                        comp = comp.trim();
                        if (comp) compMentions[comp] = (compMentions[comp] || 0) + 1;
                    });
                }
            });

            const sorted = Object.entries(compMentions)
                .map(([name, mentions]) => ({ name, mentions, isTarget: name === brandName }))
                .sort((a, b) => b.mentions - a.mentions)
                .slice(0, 10);

            const maxMentions = Math.max(...sorted.map(c => c.mentions));
            container.innerHTML = sorted.map(c =>
                '<div class="bar-row"><div class="bar-label">'+c.name+'</div><div class="bar-track"><div class="bar-fill '+(c.isTarget?'highlight':'')+'" style="width:'+(c.mentions/maxMentions*100)+'%"></div></div><div class="bar-value">'+c.mentions+'</div></div>'
            ).join('');
        }

        function renderFeaturedChart(llmFilter) {
            const container = document.getElementById('featured-chart');
            let filtered = queryData;
            if (llmFilter && llmFilter !== 'all') filtered = queryData.filter(q => q.engine.toLowerCase().replace(' ', '_') === llmFilter);

            // For "All" filter, use the pre-computed competitor featured counts
            if (!llmFilter || llmFilter === 'all') {
                const compFeatured = {};
                // Add brand's featured count
                compFeatured[brandName] = filtered.filter(q => q.featured === 'Yes').length;
                // Add competitor featured counts from the competitors array
                competitors.forEach(c => {
                    if (c.featured > 0) {
                        compFeatured[c.name] = c.featured;
                    }
                });

                const sorted = Object.entries(compFeatured)
                    .filter(([name, featured]) => featured > 0)
                    .map(([name, featured]) => ({ name, featured, isTarget: name === brandName }))
                    .sort((a, b) => b.featured - a.featured)
                    .slice(0, 10);

                const maxFeatured = Math.max(...sorted.map(c => c.featured)) || 1;
                container.innerHTML = sorted.map(c =>
                    '<div class="bar-row"><div class="bar-label">'+c.name+'</div><div class="bar-track"><div class="bar-fill '+(c.isTarget?'highlight':'')+'" style="width:'+(c.featured/maxFeatured*100)+'%"></div></div><div class="bar-value">'+c.featured+'</div></div>'
                ).join('');
            } else {
                // For filtered views, calculate from query data
                const compFeatured = {};
                filtered.forEach(q => {
                    if (q.featured === 'Yes') compFeatured[brandName] = (compFeatured[brandName] || 0) + 1;
                    if (q.featuredBrand && q.featuredBrand !== 'None' && q.featuredBrand !== '' && q.featuredBrand !== brandName) {
                        compFeatured[q.featuredBrand] = (compFeatured[q.featuredBrand] || 0) + 1;
                    }
                });

                const sorted = Object.entries(compFeatured)
                    .filter(([name, featured]) => featured > 0)
                    .map(([name, featured]) => ({ name, featured, isTarget: name === brandName }))
                    .sort((a, b) => b.featured - a.featured)
                    .slice(0, 10);

                const maxFeatured = Math.max(...sorted.map(c => c.featured)) || 1;
                container.innerHTML = sorted.length > 0 ? sorted.map(c =>
                    '<div class="bar-row"><div class="bar-label">'+c.name+'</div><div class="bar-track"><div class="bar-fill '+(c.isTarget?'highlight':'')+'" style="width:'+(c.featured/maxFeatured*100)+'%"></div></div><div class="bar-value">'+c.featured+'</div></div>'
                ).join('') : '<p style="color: var(--text-muted);">No featured first data for this platform.</p>';
            }
        }

        function filterCompetitiveByLLM(llm, btn) {
            document.querySelectorAll('#competitive-filter-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMentionChart(llm);
            renderFeaturedChart(llm);
        }

        function filterCategoriesByLLM(llm, btn) {
            document.querySelectorAll('#category-filter-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPlatformFilter = llm;
            const sortBtn = document.querySelector('.sort-btn.active');
            const sortBy = sortBtn ? (sortBtn.textContent.includes('Featured') ? 'featured' : sortBtn.textContent.includes('A-Z') ? 'alpha' : 'mention') : 'mention';
            renderCategoryGrid(sortBy, llm);
        }

        function renderCategoryGrid(sortBy, llmFilter) {
            const container = document.getElementById('category-grid');
            llmFilter = llmFilter || currentPlatformFilter;

            const catStats = {};
            categories.forEach(cat => { catStats[cat.name] = { tests: 0, mentions: 0, featured: 0, sampleQuery: cat.sampleQuery }; });

            let filtered = queryData;
            if (llmFilter && llmFilter !== 'all') filtered = queryData.filter(q => q.engine === llmFilter);

            filtered.forEach(q => {
                if (catStats[q.category]) {
                    catStats[q.category].tests++;
                    if (q.mentioned === 'Yes') catStats[q.category].mentions++;
                    if (q.featured === 'Yes') catStats[q.category].featured++;
                }
            });

            let catArray = Object.entries(catStats).map(([name, stats]) => ({
                name,
                tests: stats.tests,
                mentions: stats.mentions,
                featured: stats.featured,
                mentionRate: stats.tests > 0 ? ((stats.mentions / stats.tests) * 100) : 0,
                featuredRate: stats.tests > 0 ? ((stats.featured / stats.tests) * 100) : 0,
                sampleQuery: stats.sampleQuery
            })).filter(c => c.tests > 0);

            if (sortBy === 'featured') catArray.sort((a,b) => b.featuredRate - a.featuredRate);
            else if (sortBy === 'alpha') catArray.sort((a,b) => a.name.localeCompare(b.name));
            else catArray.sort((a,b) => b.mentionRate - a.mentionRate);

            container.innerHTML = catArray.map(cat => {
                let status = 'opportunity', statusLabel = 'Opportunity';
                if (cat.mentionRate >= 60) { status = 'leading'; statusLabel = 'Leading'; }
                else if (cat.mentionRate >= 40) { status = 'competitive'; statusLabel = 'Competitive'; }
                else if (cat.mentionRate >= 20) { status = 'developing'; statusLabel = 'Developing'; }
                return `<div class="category-card">
                    <div class="category-header"><div class="category-name">${cat.name}</div><span class="status-chip ${status}">${statusLabel}</span></div>
                    <div class="category-sample">"${cat.sampleQuery}"</div>
                    <div class="category-stats"><div class="category-stat"><div class="category-stat-value">${cat.mentionRate.toFixed(1)}%</div><div class="category-stat-label">Mention</div></div><div class="category-stat"><div class="category-stat-value">${cat.featuredRate.toFixed(1)}%</div><div class="category-stat-label">Featured</div></div><div class="category-stat"><div class="category-stat-value">${cat.tests}</div><div class="category-stat-label">Tests</div></div></div>
                    <div class="category-progress"><div class="progress-track"><div class="progress-fill" style="width:${cat.mentionRate}%"></div></div></div>
                </div>`;
            }).join('');
        }

        function sortCategories(sortBy, btn) {
            document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderCategoryGrid(sortBy);
        }

        function renderPlatformGrid() {
            const container = document.getElementById('platform-grid');
            container.innerHTML = platforms.map(p =>
                '<div class="platform-card '+(p.best?'best':'')+'"><div class="platform-name">'+p.name+'</div><div class="platform-mention">'+p.mentionRate+'%</div><div class="platform-label">Mention Rate</div><div class="platform-details"><div>'+p.mentions+'/'+p.tests+' tests</div><div>'+p.featuredRate+'% featured</div></div></div>'
            ).join('');
        }

        function renderMediaTabs() {
            if (useAdaptiveCitations && citationCategories) {
                // Adaptive mode: iterate over dynamic categories
                Object.keys(citationCategories).forEach(catName => {
                    const tabId = catName.toLowerCase().replace(/ /g, '-').replace(/&/g, 'and').replace(/\//g, '-');
                    const containerId = tabId + '-media-list';
                    renderMediaList(containerId, citationCategories[catName]);
                });
            } else {
                // Legacy mode: hardcoded tabs
                if (typeof earnedMedia !== 'undefined') renderMediaList('earned-media-list', earnedMedia);
                if (typeof shoppingMedia !== 'undefined') renderMediaList('shopping-media-list', shoppingMedia);
                if (typeof ownedMedia !== 'undefined') renderMediaList('owned-media-list', ownedMedia);
                if (typeof socialMedia !== 'undefined') renderMediaList('social-media-list', socialMedia);
                if (typeof wikipediaMedia !== 'undefined') renderMediaList('wikipedia-media-list', wikipediaMedia);
                if (typeof otherMedia !== 'undefined') renderMediaList('other-media-list', otherMedia);
            }
        }

        function renderMediaList(containerId, data) {
            const container = document.getElementById(containerId);
            if (!container) return;
            if (!data || data.length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted);">No citations in this category.</p>';
                return;
            }
            // Sort by total citations and limit to top 15
            const sortedData = [...data].sort((a, b) => b.total - a.total).slice(0, 15);
            const maxTotal = Math.max(...sortedData.map(d => d.total));
            container.innerHTML = sortedData.map(m => {
                return '<div class="media-row"><div class="media-domain">'+m.domain+'<span class="media-type-tag">'+(m.type || '')+'</span></div><div class="media-bar-container"><div class="media-bar-track" style="width:'+(m.total/maxTotal*100)+'%"></div><div class="media-bar-fill high" style="width:'+(m.total/maxTotal*100)+'%"></div></div><div class="media-pct"><strong>'+m.total+'</strong> citations</div></div>';
            }).join('');
        }

        function showTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            btn.classList.add('active');
        }

        function populateCategoryFilter() {
            const select = document.getElementById('filter-category');
            const cats = [...new Set(queryData.map(q => q.category))].sort();
            cats.forEach(cat => { const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat; select.appendChild(opt); });
        }

        function renderQueryTable() {
            const tbody = document.getElementById('query-tbody');
            tbody.innerHTML = queryData.map(q => {
                // Combine position and featured into a single "Ranking" column
                let ranking = q.position;
                if (q.featured === 'Yes' || q.position === '1st') {
                    ranking = '🏆 Featured First';
                } else if (q.position === 'Not Present') {
                    ranking = 'Not Listed';
                }

                // Featured Brand column shows who won (could be the brand or a competitor)
                const featuredBrand = q.featuredBrand || '-';

                return '<tr data-category="'+q.category+'" data-engine="'+q.engine+'" data-mentioned="'+q.mentioned+'" data-featured="'+q.featured+'" data-position="'+q.position+'"><td class="query-text">'+q.query+'</td><td>'+q.category+'</td><td>'+q.engine+'</td><td class="'+(q.mentioned==='Yes'?'mention-yes':'mention-no')+'">'+q.mentioned+'</td><td>'+ranking+'</td><td>'+featuredBrand+'</td></tr>';
            }).join('');
            document.getElementById('results-counter').textContent = 'Showing ' + queryData.length + ' of ' + queryData.length + ' results';
        }

        function filterQueriesByPlatform(platform, btn) {
            document.querySelectorAll('#query-platform-btns .platform-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterQueries();
        }

        function filterQueries() {
            const cat = document.getElementById('filter-category').value;
            const platformBtn = document.querySelector('#query-platform-btns .platform-btn.active');
            const plat = platformBtn ? platformBtn.dataset.platform : 'all';
            const mentioned = document.getElementById('filter-mentioned').value;
            const featured = document.getElementById('filter-featured').value;

            const rows = document.querySelectorAll('#query-tbody tr');
            let count = 0;
            rows.forEach(row => {
                let show = true;
                if (cat !== 'all' && row.dataset.category !== cat) show = false;
                if (plat !== 'all' && row.dataset.engine !== plat) show = false;
                if (mentioned !== 'all' && row.dataset.mentioned !== mentioned) show = false;
                if (featured !== 'all' && row.dataset.featured !== featured) show = false;
                row.style.display = show ? '' : 'none';
                if (show) count++;
            });
            document.getElementById('results-counter').textContent = 'Showing ' + count + ' of ' + queryData.length + ' results';
        }

        function sortTable(col) {
            const tbody = document.getElementById('query-tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            rows.sort((a, b) => {
                const aVal = a.cells[col].textContent;
                const bVal = b.cells[col].textContent;
                return aVal.localeCompare(bVal);
            });
            rows.forEach(row => tbody.appendChild(row));
        }
        '''

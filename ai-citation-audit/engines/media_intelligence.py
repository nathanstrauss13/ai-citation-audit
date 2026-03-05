"""
Media Intelligence Engine - Citation-based insights for owned and earned media.

Analyzes citation data to produce actionable intelligence:
- Owned Media: Are brand websites being cited? How does that compare to competitors?
  Do owned citations correlate with wins?
- Earned Media: Which outlets correlate with brand wins (PR strengths)?
  Which outlets favor competitors (PR opportunities)?

Usage:
    from engines.media_intelligence import MediaIntelligenceEngine

    engine = MediaIntelligenceEngine()
    insights = engine.analyze(query_data, brand_name, owned_domains, competitor_domains)
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class OwnedMediaInsight:
    """Insights about brand's owned content citation performance."""

    # Citation counts
    brand_owned_citations: int = 0
    competitor_owned_citations: int = 0
    total_responses: int = 0

    # Performance metrics
    brand_owned_citation_rate: float = 0.0  # % of responses citing brand owned
    competitor_owned_citation_rate: float = 0.0  # % citing any competitor owned

    # Win correlation
    win_rate_with_owned: float = 0.0  # Win rate when brand owned is cited
    win_rate_without_owned: float = 0.0  # Win rate when not cited
    owned_lift: float = 0.0  # Difference (positive = owned helps)

    # Competitor comparison
    competitor_owned_detail: List[Dict] = field(default_factory=list)
    # [{name, citations, citation_rate, win_rate_when_cited}]

    # Assessment
    performance_assessment: str = ""  # "outperforming", "underperforming", "comparable"
    insight_summary: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class EarnedMediaOutlet:
    """Individual earned media outlet analysis."""
    domain: str
    outlet_type: str  # "Trade", "News", "Lifestyle", etc.

    # Citation metrics
    total_citations: int = 0
    brand_citations: int = 0  # Times cited when brand mentioned
    competitor_citations: int = 0  # Times cited when competitor won

    # Win correlation
    brand_win_rate: float = 0.0  # Brand win rate when this outlet cited
    avg_win_rate: float = 0.0  # Overall average for comparison
    lift: float = 0.0  # Difference from average

    # Classification
    is_strength: bool = False  # Correlates with brand wins
    is_opportunity: bool = False  # Favors competitors


@dataclass
class EarnedMediaInsight:
    """Insights about earned media performance and opportunities."""

    # PR Strengths - outlets that correlate with brand wins
    pr_strengths: List[EarnedMediaOutlet] = field(default_factory=list)

    # PR Opportunities - outlets favoring competitors
    pr_opportunities: List[EarnedMediaOutlet] = field(default_factory=list)

    # Summary metrics
    total_earned_outlets: int = 0
    outlets_favoring_brand: int = 0
    outlets_favoring_competitors: int = 0

    # Insight
    insight_summary: str = ""
    recommendations: List[str] = field(default_factory=list)


class MediaIntelligenceEngine:
    """Engine for computing media intelligence from citation data."""

    # Domain classification for earned media types
    OUTLET_TYPES = {
        # Hospitality/Travel
        'cntraveler': 'Travel Magazine', 'travelandleisure': 'Travel Magazine',
        'afar': 'Travel Magazine', 'lonelyplanet': 'Travel Guide',
        'thepointsguy': 'Points/Miles', 'onemileatatime': 'Points/Miles',
        'skift': 'Industry Trade', 'phocuswire': 'Industry Trade',
        'tripadvisor': 'Review Platform', 'yelp': 'Review Platform',
        # General News
        'nytimes': 'Major News', 'wsj': 'Major News', 'forbes': 'Business',
        'cnn': 'Major News', 'bbc': 'Major News', 'bloomberg': 'Business',
        # Tech
        'techcrunch': 'Tech', 'wired': 'Tech', 'theverge': 'Tech',
        # Lifestyle
        'vogue': 'Lifestyle', 'gq': 'Lifestyle', 'esquire': 'Lifestyle',
        # Retail-focused
        'wirecutter': 'Product Review', 'cnet': 'Product Review',
    }

    def __init__(self):
        pass

    def analyze(
        self,
        query_data: List[Dict],
        brand_name: str,
        owned_domains: List[str],
        competitor_data: Optional[List[Dict]] = None
    ) -> Tuple[OwnedMediaInsight, EarnedMediaInsight]:
        """
        Analyze citation data to produce owned and earned media insights.

        Args:
            query_data: List of query result dicts with citation info
            brand_name: Target brand name
            owned_domains: List of brand's owned domains
            competitor_data: Optional list of competitor info with owned_domains

        Returns:
            Tuple of (OwnedMediaInsight, EarnedMediaInsight)
        """
        owned_insight = self._analyze_owned_media(
            query_data, brand_name, owned_domains, competitor_data
        )
        earned_insight = self._analyze_earned_media(
            query_data, brand_name, owned_domains, competitor_data
        )

        return owned_insight, earned_insight

    def _analyze_owned_media(
        self,
        query_data: List[Dict],
        brand_name: str,
        owned_domains: List[str],
        competitor_data: Optional[List[Dict]] = None
    ) -> OwnedMediaInsight:
        """Analyze owned media citation performance."""

        brand_lower = brand_name.lower().replace(' ', '').replace('-', '')
        owned_lower = [d.lower().replace('www.', '') for d in owned_domains]

        total_responses = len(query_data)
        if total_responses == 0:
            return OwnedMediaInsight(insight_summary="No data available")

        # Track metrics
        brand_owned_cited_count = 0
        brand_wins = 0
        brand_wins_with_owned = 0
        brand_wins_without_owned = 0
        responses_with_owned = 0
        responses_without_owned = 0

        # Competitor owned tracking - per competitor
        competitor_owned_cited_count = 0
        competitor_owned_domains = self._get_competitor_owned_domains(competitor_data)

        # Track per-competitor metrics
        competitor_metrics = {}
        if competitor_data:
            for comp in competitor_data:
                comp_name = comp.get('name', comp.get('brand_name', ''))
                if comp_name:
                    competitor_metrics[comp_name] = {
                        'citations': 0,
                        'wins_with_owned': 0,
                        'responses_with_owned': 0
                    }

        for row in query_data:
            # Get citation domains for this response
            citation_domains = self._extract_domains(row)

            # Check if brand owned domain cited
            brand_owned_cited = any(
                any(owned in cite_domain for owned in owned_lower)
                for cite_domain in citation_domains
            )

            # Check if competitor owned domains cited (overall)
            comp_owned_cited = any(
                any(comp_domain in cite_domain for comp_domain in competitor_owned_domains)
                for cite_domain in citation_domains
            )

            # Check per-competitor owned citations
            if competitor_data:
                for comp in competitor_data:
                    comp_name = comp.get('name', comp.get('brand_name', ''))
                    if not comp_name:
                        continue
                    comp_domain_lower = comp_name.lower().replace(' ', '').replace('-', '')
                    comp_cited = any(comp_domain_lower in d.lower() for d in citation_domains)
                    if comp_cited and comp_name in competitor_metrics:
                        competitor_metrics[comp_name]['citations'] += 1
                        competitor_metrics[comp_name]['responses_with_owned'] += 1
                        # Check if this competitor won when their content was cited
                        # (brand did NOT win = competitor opportunity)
                        if not self._is_brand_win(row, brand_name):
                            competitor_metrics[comp_name]['wins_with_owned'] += 1

            # Check if this is a brand win
            is_brand_win = self._is_brand_win(row, brand_name)

            # Update counters
            if brand_owned_cited:
                brand_owned_cited_count += 1
                responses_with_owned += 1
                if is_brand_win:
                    brand_wins_with_owned += 1
            else:
                responses_without_owned += 1
                if is_brand_win:
                    brand_wins_without_owned += 1

            if comp_owned_cited:
                competitor_owned_cited_count += 1

            if is_brand_win:
                brand_wins += 1

        # Calculate metrics
        brand_owned_rate = (brand_owned_cited_count / total_responses * 100) if total_responses > 0 else 0
        comp_owned_rate = (competitor_owned_cited_count / total_responses * 100) if total_responses > 0 else 0

        win_rate_with_owned = (brand_wins_with_owned / responses_with_owned * 100) if responses_with_owned > 0 else 0
        win_rate_without_owned = (brand_wins_without_owned / responses_without_owned * 100) if responses_without_owned > 0 else 0
        owned_lift = win_rate_with_owned - win_rate_without_owned

        # Determine assessment based on WIN RATE LIFT (not volume)
        # High lift = owned content is effective at converting to wins
        # Volume is context, not the assessment criteria
        if owned_lift >= 15:
            assessment = "high_impact"
        elif owned_lift >= 5:
            assessment = "positive_impact"
        elif owned_lift >= -5:
            assessment = "neutral"
        elif owned_lift >= -15:
            assessment = "low_impact"
        else:
            assessment = "negative_impact"

        # Generate insight summary focused on effectiveness, not volume
        if owned_lift >= 15:
            lift_insight = f"Strong signal: +{owned_lift:.0f}pp win rate when your owned content is cited"
        elif owned_lift >= 5:
            lift_insight = f"Positive signal: +{owned_lift:.0f}pp win rate when your owned content is cited"
        elif owned_lift >= -5:
            lift_insight = "Neutral: owned citations don't significantly affect win rate"
        else:
            lift_insight = f"Warning: {owned_lift:.0f}pp win rate when owned content is cited (may indicate content quality issues)"

        # Volume context (separate from effectiveness)
        volume_context = f"Owned domains cited in {brand_owned_rate:.1f}% of responses"
        if comp_owned_rate > 0:
            volume_context += f" (competitors: {comp_owned_rate:.1f}%)"

        insight_summary = f"{lift_insight}. {volume_context}."

        # Generate recommendations based on lift AND volume
        recommendations = []
        if owned_lift >= 15:
            recommendations.append("High-impact owned content - expand citable pages to increase citation volume")
        elif owned_lift >= 5 and brand_owned_rate < 10:
            recommendations.append("Effective content but low visibility - focus on increasing citation frequency")
        elif owned_lift < -5:
            recommendations.append("Owned content may need quality improvements - citations correlate with losses")
        if brand_owned_rate < 5 and owned_lift >= 0:
            recommendations.append("Low owned citation rate - ensure key pages are crawlable and authoritative")

        # Build competitor comparison data
        competitor_owned_detail = []
        for comp_name, metrics in competitor_metrics.items():
            if metrics['citations'] > 0:
                comp_citation_rate = round(metrics['citations'] / total_responses * 100, 1)
                # Win lift: when competitor owned is cited, how often does brand NOT win
                comp_win_rate = (metrics['wins_with_owned'] / metrics['responses_with_owned'] * 100) if metrics['responses_with_owned'] > 0 else 0
                comp_lift = round(comp_win_rate - (100 - (brand_wins / total_responses * 100)), 1)  # Relative to base loss rate
                competitor_owned_detail.append({
                    'name': comp_name,
                    'citations': metrics['citations'],
                    'citation_rate': comp_citation_rate,
                    'lift': comp_lift
                })

        # Sort by citation rate
        competitor_owned_detail.sort(key=lambda x: x['citation_rate'], reverse=True)

        return OwnedMediaInsight(
            brand_owned_citations=brand_owned_cited_count,
            competitor_owned_citations=competitor_owned_cited_count,
            total_responses=total_responses,
            brand_owned_citation_rate=round(brand_owned_rate, 1),
            competitor_owned_citation_rate=round(comp_owned_rate, 1),
            win_rate_with_owned=round(win_rate_with_owned, 1),
            win_rate_without_owned=round(win_rate_without_owned, 1),
            owned_lift=round(owned_lift, 1),
            competitor_owned_detail=competitor_owned_detail,
            performance_assessment=assessment,
            insight_summary=insight_summary,
            recommendations=recommendations
        )

    def _analyze_earned_media(
        self,
        query_data: List[Dict],
        brand_name: str,
        owned_domains: List[str],
        competitor_data: Optional[List[Dict]] = None
    ) -> EarnedMediaInsight:
        """Analyze earned media outlets for PR intelligence."""

        owned_lower = [d.lower().replace('www.', '') for d in owned_domains]

        # Get competitor owned domains to exclude from earned media
        competitor_owned = self._get_competitor_owned_domains(competitor_data)

        # Get competitor names for additional filtering
        competitor_names = []
        if competitor_data:
            for comp in competitor_data:
                name = comp.get('name', comp.get('brand_name', ''))
                if name:
                    competitor_names.append(name)

        # Track per-outlet metrics
        outlet_stats = defaultdict(lambda: {
            'total_citations': 0,
            'brand_win_citations': 0,  # Cited when brand won
            'competitor_win_citations': 0,  # Cited when competitor won
            'brand_mention_citations': 0,  # Cited when brand mentioned
        })

        total_responses = len(query_data)
        total_brand_wins = 0

        for row in query_data:
            citation_domains = self._extract_domains(row)
            is_brand_win = self._is_brand_win(row, brand_name)
            is_brand_mentioned = self._is_brand_mentioned(row, brand_name)

            if is_brand_win:
                total_brand_wins += 1

            for domain in citation_domains:
                # Skip brand's owned domains
                if any(owned in domain for owned in owned_lower):
                    continue

                # Skip competitor owned domains (these are NOT earned media)
                if any(comp in domain for comp in competitor_owned):
                    continue

                # Skip retail/shopping domains
                if self._is_shopping_domain(domain):
                    continue

                # Skip social domains
                if self._is_social_domain(domain):
                    continue

                # Skip system/platform domains and competitor domains
                if self._is_excluded_domain(domain, competitor_names):
                    continue

                outlet_stats[domain]['total_citations'] += 1

                if is_brand_win:
                    outlet_stats[domain]['brand_win_citations'] += 1
                elif not is_brand_mentioned:
                    outlet_stats[domain]['competitor_win_citations'] += 1

                if is_brand_mentioned:
                    outlet_stats[domain]['brand_mention_citations'] += 1

        # Calculate average brand win rate
        avg_brand_win_rate = (total_brand_wins / total_responses * 100) if total_responses > 0 else 0

        # Classify outlets
        pr_strengths = []
        pr_opportunities = []

        for domain, stats in outlet_stats.items():
            if stats['total_citations'] < 2:  # Need minimum citations
                continue

            # Calculate win rate when this outlet is cited
            total = stats['total_citations']
            brand_win_rate = (stats['brand_win_citations'] / total * 100) if total > 0 else 0
            competitor_win_rate = (stats['competitor_win_citations'] / total * 100) if total > 0 else 0
            lift = brand_win_rate - avg_brand_win_rate

            outlet = EarnedMediaOutlet(
                domain=domain,
                outlet_type=self._classify_outlet(domain),
                total_citations=total,
                brand_citations=stats['brand_mention_citations'],
                competitor_citations=stats['competitor_win_citations'],
                brand_win_rate=round(brand_win_rate, 1),
                avg_win_rate=round(avg_brand_win_rate, 1),
                lift=round(lift, 1)
            )

            # Classify as strength or opportunity
            if lift > 10 and stats['brand_win_citations'] >= 2:
                outlet.is_strength = True
                pr_strengths.append(outlet)
            elif lift < -10 or stats['competitor_win_citations'] > stats['brand_win_citations']:
                outlet.is_opportunity = True
                pr_opportunities.append(outlet)

        # Sort by impact
        pr_strengths.sort(key=lambda x: x.lift, reverse=True)
        pr_opportunities.sort(key=lambda x: x.competitor_citations, reverse=True)

        # Generate insight summary
        strength_count = len(pr_strengths)
        opp_count = len(pr_opportunities)

        if strength_count > 0:
            top_strength = pr_strengths[0].domain
            insight_summary = f"{strength_count} outlets correlate with your wins (top: {top_strength}). "
        else:
            insight_summary = "No clear PR strengths identified yet. "

        if opp_count > 0:
            insight_summary += f"{opp_count} outlets favor competitors - potential outreach targets."

        # Generate recommendations
        recommendations = []
        if strength_count > 0:
            recommendations.append(f"Maintain relationships with {', '.join([o.domain for o in pr_strengths[:3]])} - they correlate with your wins")
        if opp_count > 0:
            recommendations.append(f"Target outreach to {', '.join([o.domain for o in pr_opportunities[:3]])} - currently favoring competitors")

        return EarnedMediaInsight(
            pr_strengths=pr_strengths[:10],
            pr_opportunities=pr_opportunities[:10],
            total_earned_outlets=len(outlet_stats),
            outlets_favoring_brand=strength_count,
            outlets_favoring_competitors=opp_count,
            insight_summary=insight_summary,
            recommendations=recommendations
        )

    def _extract_domains(self, row: Dict) -> List[str]:
        """Extract citation domains from a query result row."""
        domains = []

        # Try different field names
        for field in ['citation_domains', 'cited_domains', 'citations']:
            if field in row and row[field]:
                val = row[field]
                if isinstance(val, str):
                    # Parse pipe or comma separated
                    domains.extend([d.strip().lower() for d in val.replace('|', ',').split(',') if d.strip()])
                elif isinstance(val, list):
                    domains.extend([d.lower() for d in val if d])

        return domains

    def _is_brand_win(self, row: Dict, brand_name: str) -> bool:
        """Check if this response is a brand win (featured first)."""
        # Check various field names
        if row.get('new_prominence') == 'featured_first':
            return True
        if row.get(f'{brand_name.lower()}_featured') in [True, 1, '1', 'Yes', 'yes']:
            return True
        if row.get('featured_brand', '').lower() == brand_name.lower():
            return True
        if row.get('focal_brand_featured') in [True, 1, '1', 'Yes', 'yes']:
            return True
        return False

    def _is_brand_mentioned(self, row: Dict, brand_name: str) -> bool:
        """Check if brand was mentioned in this response."""
        if row.get('new_focal_brand_found') in [True, 1, '1', 'Yes', 'yes']:
            return True
        if row.get(f'{brand_name.lower()}_mentioned') in [True, 1, '1', 'Yes', 'yes']:
            return True
        return False

    def _get_competitor_owned_domains(self, competitor_data: Optional[List[Dict]]) -> List[str]:
        """Extract competitor owned domains."""
        if not competitor_data:
            return []

        domains = []
        for comp in competitor_data:
            if 'owned_domains' in comp:
                domains.extend([d.lower() for d in comp['owned_domains']])
            elif 'domain' in comp:
                domains.append(comp['domain'].lower())
            # Infer from brand name
            name = comp.get('name', comp.get('brand_name', ''))
            if name:
                domains.append(f"{name.lower().replace(' ', '')}.com")

        return domains

    def _is_shopping_domain(self, domain: str) -> bool:
        """Check if domain is a shopping/retail site."""
        shopping = ['amazon', 'nordstrom', 'rei.', 'target.', 'walmart', 'booking.com',
                    'expedia', 'hotels.com', 'tripadvisor', 'kayak', 'airbnb']
        return any(s in domain.lower() for s in shopping)

    def _is_social_domain(self, domain: str) -> bool:
        """Check if domain is social media."""
        social = ['reddit', 'youtube', 'twitter', 'facebook', 'instagram',
                  'tiktok', 'pinterest', 'linkedin']
        return any(s in domain.lower() for s in social)

    def _is_excluded_domain(self, domain: str, competitor_names: List[str] = None) -> bool:
        """Check if domain should be excluded from earned media analysis."""
        d = domain.lower()

        # System/platform domains that are not earned media
        excluded_patterns = [
            'vertexaisearch', 'googleusercontent', 'googleapis', 'gstatic',
            'cloudflare', 'cdn.', '.cdn', 'amazonaws', 's3.', 'azure',
            'blob.core', 'storage.', 'static.', 'assets.', 'media.',
            'googleads', 'doubleclick', 'googlesyndication',
            'analytics', 'tracking', '.ai/', 'api.', 'developer.',
            'docs.google', 'drive.google', 'cloud.google',
        ]
        if any(p in d for p in excluded_patterns):
            return True

        # Check if it's a competitor domain (contains competitor brand name)
        if competitor_names:
            for comp_name in competitor_names:
                # Normalize competitor name for matching
                comp_lower = comp_name.lower().replace(' ', '').replace('-', '')
                if len(comp_lower) >= 3 and comp_lower in d.replace('-', '').replace('.', ''):
                    return True

        return False

    def _classify_outlet(self, domain: str) -> str:
        """Classify outlet type."""
        d = domain.lower()
        for key, outlet_type in self.OUTLET_TYPES.items():
            if key in d:
                return outlet_type
        return "General"


def prepare_media_intelligence_js(
    owned_insight: OwnedMediaInsight,
    earned_insight: EarnedMediaInsight
) -> str:
    """Prepare media intelligence data as JavaScript for dashboard embedding."""

    # Convert strengths and opportunities to dict with both volume and lift
    strengths_data = [
        {
            'domain': o.domain,
            'type': o.outlet_type,
            'totalCitations': o.total_citations,  # Volume context
            'brandWinCitations': o.brand_citations,  # Times cited with brand wins
            'brandWinRate': o.brand_win_rate,
            'lift': o.lift  # Win rate lift vs average
        }
        for o in earned_insight.pr_strengths
    ]

    opportunities_data = [
        {
            'domain': o.domain,
            'type': o.outlet_type,
            'totalCitations': o.total_citations,  # Volume context
            'competitorCitations': o.competitor_citations,  # Times cited with competitor wins
            'brandWinRate': o.brand_win_rate,
            'lift': o.lift
        }
        for o in earned_insight.pr_opportunities
    ]

    # Prepare competitor comparison data for JavaScript
    competitor_comparison = [
        {
            'name': c['name'],
            'citationRate': c['citation_rate'],
            'lift': c['lift'],
            'citations': c['citations']
        }
        for c in owned_insight.competitor_owned_detail
    ]

    data = {
        'owned': {
            'brandCitations': owned_insight.brand_owned_citations,
            'competitorCitations': owned_insight.competitor_owned_citations,
            'brandCitationRate': owned_insight.brand_owned_citation_rate,
            'competitorCitationRate': owned_insight.competitor_owned_citation_rate,
            'winRateWithOwned': owned_insight.win_rate_with_owned,
            'winRateWithoutOwned': owned_insight.win_rate_without_owned,
            'ownedLift': owned_insight.owned_lift,
            'assessment': owned_insight.performance_assessment,
            'summary': owned_insight.insight_summary,
            'recommendations': owned_insight.recommendations,
            'competitorComparison': competitor_comparison
        },
        'earned': {
            'strengths': strengths_data,
            'opportunities': opportunities_data,
            'totalOutlets': earned_insight.total_earned_outlets,
            'outletsFavoringBrand': earned_insight.outlets_favoring_brand,
            'outletsFavoringCompetitors': earned_insight.outlets_favoring_competitors,
            'summary': earned_insight.insight_summary,
            'recommendations': earned_insight.recommendations
        }
    }

    return json.dumps(data)

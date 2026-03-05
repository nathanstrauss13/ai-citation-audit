"""
AEO Intelligence Platform - Analysis Engine

Computes comprehensive analytics from collected response data:
- Prominence scoring (5-level)
- Segment-level performance metrics
- Competitor intelligence (discovered from data)
- Citation tier classification
- Content Conversion Rate
- Platform comparison

Usage:
    from engines.analysis_engine import AnalysisEngine
    from schema.database import Database

    db = Database()
    engine = AnalysisEngine(db)

    # Run full analysis
    insights = engine.analyze_study(study_id)

    # Access specific metrics
    print(insights['brand_metrics'])
    print(insights['segment_analysis'])
    print(insights['competitor_intelligence'])
"""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# Prominence scoring weights (for composite score)
PROMINENCE_WEIGHTS = {
    "featured_first": 1.0,
    "recommended": 0.8,
    "listed": 0.5,
    "mentioned": 0.25,
    "not_mentioned": 0.0
}

# Citation tier domains (extensible)
EDITORIAL_DOMAINS = [
    'forbes.com', 'techcrunch.com', 'gq.com', 'vogue.com', 'wired.com',
    'businessinsider.com', 'bloomberg.com', 'nytimes.com', 'wsj.com',
    'theverge.com', 'cnet.com', 'engadget.com', 'mashable.com',
    'fastcompany.com', 'inc.com', 'entrepreneur.com', 'fortune.com',
    'theatlantic.com', 'newyorker.com', 'esquire.com', 'elle.com',
    'harpersbazaar.com', 'cosmopolitan.com', 'instyle.com', 'glamour.com',
    'runnersworld.com', 'menshealth.com', 'womenshealth.com', 'self.com',
    'shape.com', 'outsideonline.com', 'trailrunnermag.com'
]

RETAIL_DOMAINS = [
    'nordstrom.com', 'amazon.com', 'rei.com', 'bestbuy.com',
    'target.com', 'walmart.com', 'macys.com', 'bloomingdales.com',
    'zappos.com', 'saksfifthavenue.com', 'neimanmarcus.com',
    'dickssportinggoods.com', 'footlocker.com', 'finishline.com',
    'backcountry.com', 'moosejaw.com', 'steepandcheap.com',
    'shopbop.com', 'revolve.com', 'asos.com', 'net-a-porter.com'
]

SOCIAL_DOMAINS = [
    'reddit.com', 'youtube.com', 'twitter.com', 'x.com',
    'instagram.com', 'facebook.com', 'tiktok.com', 'pinterest.com',
    'linkedin.com', 'quora.com'
]

AFFILIATE_DOMAINS = [
    'wirecutter.com', 'thestrategist.com', 'nymag.com/strategist',
    'bestproducts.com', 'goodhousekeeping.com', 'reviewed.com',
    'rtings.com', 'tomsguide.com', 'pcmag.com', 'techradar.com'
]

REFERENCE_DOMAINS = [
    'wikipedia.org', 'britannica.com', 'investopedia.com',
    'healthline.com', 'webmd.com', 'mayoclinic.org'
]

# Citation Quality Tiers
# Tier 1: Major publications with high authority (news, business, lifestyle leaders)
TIER1_DOMAINS = [
    # Major News
    'nytimes.com', 'wsj.com', 'washingtonpost.com', 'bbc.com', 'bbc.co.uk',
    'cnn.com', 'reuters.com', 'apnews.com', 'theguardian.com', 'ft.com',
    'economist.com', 'npr.org', 'time.com', 'usatoday.com', 'latimes.com',
    # Business/Finance
    'bloomberg.com', 'forbes.com', 'fortune.com', 'businessinsider.com',
    'cnbc.com', 'marketwatch.com', 'barrons.com', 'hbr.org',
    # Premium Lifestyle
    'vogue.com', 'gq.com', 'esquire.com', 'vanityfair.com', 'newyorker.com',
    'theatlantic.com', 'wired.com', 'architecturaldigest.com', 'cntraveler.com',
    'travelandleisure.com', 'nationalgeographic.com', 'smithsonianmag.com',
]

# Tier 2: Trade press, specialty publications, respected verticals
TIER2_DOMAINS = [
    # Tech Trade
    'techcrunch.com', 'theverge.com', 'arstechnica.com', 'engadget.com',
    'cnet.com', 'zdnet.com', 'venturebeat.com', 'mashable.com',
    # Industry/Trade
    'adage.com', 'adweek.com', 'prweek.com', 'fastcompany.com',
    'inc.com', 'entrepreneur.com', 'hospitalitynet.org', 'skift.com',
    'phocuswire.com', 'hotelmanagement.net', 'hotelnewsresource.com',
    # Specialty Consumer
    'runnersworld.com', 'menshealth.com', 'womenshealth.com', 'self.com',
    'outsideonline.com', 'shape.com', 'elle.com', 'harpersbazaar.com',
    'cosmopolitan.com', 'glamour.com', 'instyle.com', 'refinery29.com',
    # Review/Affiliate (high quality)
    'wirecutter.com', 'thestrategist.com', 'reviewed.com', 'rtings.com',
    'tomsguide.com', 'pcmag.com', 'techradar.com', 'goodhousekeeping.com',
    # Local/Regional Quality
    'sfchronicle.com', 'bostonglobe.com', 'chicagotribune.com',
]

# Tier 3: Blogs, forums, UGC, lower authority sources
TIER3_DOMAINS = [
    # Social/UGC
    'reddit.com', 'quora.com', 'medium.com', 'substack.com',
    # Forums/Community
    'flyertalk.com', 'tripadvisor.com', 'yelp.com',
    # Personal blogs (generic patterns caught separately)
    'wordpress.com', 'blogspot.com', 'tumblr.com', 'wix.com',
    # Low-authority aggregators
    'buzzfeed.com', 'ranker.com', 'therichest.com',
]


@dataclass
class BrandMetrics:
    """Core brand performance metrics."""

    total_queries: int = 0
    total_responses: int = 0

    # Mention metrics
    mention_count: int = 0
    mention_rate: float = 0.0

    # Prominence distribution
    featured_first_count: int = 0
    recommended_count: int = 0
    listed_count: int = 0
    mentioned_only_count: int = 0
    not_mentioned_count: int = 0

    # Derived rates
    featured_first_rate: float = 0.0
    recommended_rate: float = 0.0
    listed_rate: float = 0.0

    # Branded / Unbranded split (v17)
    branded_total: int = 0
    branded_mention_count: int = 0
    branded_mention_rate: float = 0.0
    branded_featured_first_count: int = 0
    branded_featured_first_rate: float = 0.0
    unbranded_total: int = 0
    unbranded_mention_count: int = 0
    unbranded_mention_rate: float = 0.0
    unbranded_featured_first_count: int = 0
    unbranded_featured_first_rate: float = 0.0
    unbranded_top_rate: float = 0.0  # Featured first among unbranded (for AEO Score)

    # Composite scores
    prominence_score: float = 0.0  # Weighted average (0-100)
    visibility_score: float = 0.0  # Overall AI visibility (0-100)
    aeo_score: float = 0.0  # v17: (featured_rate * 0.7) + (top_rate * 0.3) on unbranded

    # Platform variance
    platform_variance: float = 0.0  # Max platform rate - min platform rate

    # Competitive rank (discovered from data)
    competitive_rank: int = 0  # Brand's rank among all discovered brands

    # Sentiment
    positive_sentiment_rate: float = 0.0
    neutral_sentiment_rate: float = 0.0
    negative_sentiment_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SegmentMetrics:
    """Performance metrics for a specific segment."""

    segment_type: str = ""
    segment_value: str = ""

    query_count: int = 0
    response_count: int = 0

    mention_rate: float = 0.0
    featured_rate: float = 0.0
    prominence_score: float = 0.0

    # Comparison to overall
    mention_rate_delta: float = 0.0  # vs overall
    prominence_delta: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompetitorMetrics:
    """Metrics for a discovered competitor."""

    brand_name: str = ""

    mention_count: int = 0
    featured_count: int = 0

    mention_rate: float = 0.0
    featured_rate: float = 0.0
    win_rate: float = 0.0  # Featured when mentioned

    # Head-to-head (vs focal brand)
    head_to_head_wins: int = 0
    head_to_head_losses: int = 0
    head_to_head_ties: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CitationMetrics:
    """Citation intelligence metrics."""

    total_citations: int = 0

    # By type (legacy)
    owned_citations: int = 0
    editorial_citations: int = 0
    retail_citations: int = 0
    social_citations: int = 0
    affiliate_citations: int = 0
    reference_citations: int = 0
    other_citations: int = 0

    # Quality Tiers (NEW)
    tier1_citations: int = 0  # Major publications (NYT, WSJ, Forbes, etc.)
    tier2_citations: int = 0  # Trade press, specialty publications
    tier3_citations: int = 0  # Blogs, forums, UGC
    untiered_citations: int = 0  # Not classified

    # Quality Score (weighted: T1=3, T2=2, T3=1)
    citation_quality_score: float = 0.0  # 0-100 scale

    # Content Conversion
    times_brand_cited: int = 0
    wins_when_cited: int = 0
    content_conversion_rate: float = 0.0

    # Top citing domains
    top_domains: List[Tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlatformMetrics:
    """Metrics for a specific AI platform."""

    platform: str = ""
    response_count: int = 0

    mention_rate: float = 0.0
    featured_rate: float = 0.0
    prominence_score: float = 0.0

    avg_citations_per_response: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StudyInsights:
    """Complete analysis output for a study."""

    study_id: str = ""
    brand_name: str = ""
    study_type: str = ""

    # Core metrics
    brand_metrics: BrandMetrics = field(default_factory=BrandMetrics)

    # Segmented analysis
    segment_metrics: Dict[str, List[SegmentMetrics]] = field(default_factory=dict)
    # e.g., {"business_line": [...], "product_category": [...]}

    # Competitor intelligence
    discovered_competitors: List[CompetitorMetrics] = field(default_factory=list)
    share_of_voice: Dict[str, float] = field(default_factory=dict)

    # Citation analysis
    citation_metrics: CitationMetrics = field(default_factory=CitationMetrics)

    # Platform comparison
    platform_metrics: List[PlatformMetrics] = field(default_factory=list)

    # Key insights (narrative)
    key_insights: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "study_id": self.study_id,
            "brand_name": self.brand_name,
            "study_type": self.study_type,
            "brand_metrics": self.brand_metrics.to_dict(),
            "segment_metrics": {
                seg_type: [m.to_dict() for m in metrics]
                for seg_type, metrics in self.segment_metrics.items()
            },
            "discovered_competitors": [c.to_dict() for c in self.discovered_competitors],
            "share_of_voice": self.share_of_voice,
            "citation_metrics": self.citation_metrics.to_dict(),
            "platform_metrics": [p.to_dict() for p in self.platform_metrics],
            "key_insights": self.key_insights,
            "opportunities": self.opportunities,
            "threats": self.threats
        }

    def to_json(self) -> str:
        """Export as formatted JSON."""
        return json.dumps(self.to_dict(), indent=2)


class AnalysisEngine:
    """
    Computes comprehensive analytics from collected response data.

    Key capabilities:
    - 5-level prominence scoring
    - Segment-level breakdowns
    - Unbiased competitor discovery
    - Citation tier classification
    - Content Conversion Rate calculation
    - Platform comparison
    """

    def __init__(self, db):
        """
        Initialize with database connection.

        Args:
            db: Database instance
        """
        self.db = db

    def classify_domain(self, domain: str, owned_domains: List[str]) -> str:
        """
        Classify a domain into citation tiers.

        Args:
            domain: Domain to classify
            owned_domains: Brand's owned domains

        Returns:
            Tier: 'owned', 'editorial', 'retail', 'social', 'affiliate', 'reference', 'other'
        """
        domain_lower = domain.lower()

        # Check owned first
        for owned in owned_domains:
            if owned.lower() in domain_lower or domain_lower in owned.lower():
                return 'owned'

        # Check editorial
        if any(ed in domain_lower for ed in EDITORIAL_DOMAINS):
            return 'editorial'

        # Check retail
        if any(rt in domain_lower for rt in RETAIL_DOMAINS):
            return 'retail'

        # Check social
        if any(soc in domain_lower for soc in SOCIAL_DOMAINS):
            return 'social'

        # Check affiliate/review sites
        if any(aff in domain_lower for aff in AFFILIATE_DOMAINS):
            return 'affiliate'

        # Check reference
        if any(ref in domain_lower for ref in REFERENCE_DOMAINS):
            return 'reference'

        return 'other'

    def classify_tier(self, domain: str) -> int:
        """
        Classify a domain into quality tiers.

        Args:
            domain: Domain to classify

        Returns:
            Tier: 1 (major publications), 2 (trade press), 3 (blogs/forums), 0 (unclassified)
        """
        domain_lower = domain.lower()

        # Check Tier 1 (major publications)
        if any(t1 in domain_lower for t1 in TIER1_DOMAINS):
            return 1

        # Check Tier 2 (trade press)
        if any(t2 in domain_lower for t2 in TIER2_DOMAINS):
            return 2

        # Check Tier 3 (blogs/forums/UGC)
        if any(t3 in domain_lower for t3 in TIER3_DOMAINS):
            return 3

        # Check for blog patterns (Tier 3)
        blog_patterns = ['blog', 'wordpress', 'blogspot', 'tumblr', 'wix', 'squarespace']
        if any(pattern in domain_lower for pattern in blog_patterns):
            return 3

        return 0  # Unclassified

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain.lower()
        except Exception:
            return url.lower()

    def calculate_prominence_score(self, responses: list) -> float:
        """
        Calculate weighted prominence score (0-100).

        Args:
            responses: List of Response objects

        Returns:
            Prominence score
        """
        if not responses:
            return 0.0

        total_weight = 0.0
        for r in responses:
            prominence = r.brand_prominence or "not_mentioned"
            total_weight += PROMINENCE_WEIGHTS.get(prominence, 0.0)

        # Normalize to 0-100
        max_possible = len(responses) * 1.0  # Max is featured_first for all
        return (total_weight / max_possible) * 100 if max_possible > 0 else 0.0

    def analyze_study(self, study_id: str) -> StudyInsights:
        """
        Run complete analysis for a study.

        Args:
            study_id: Study ID

        Returns:
            StudyInsights with all computed metrics
        """
        logger.info(f"Analyzing study: {study_id}")

        # Get study info
        study = self.db.get_study(study_id)
        if not study:
            raise ValueError(f"Study not found: {study_id}")

        insights = StudyInsights(
            study_id=study_id,
            brand_name=study.brand_name,
            study_type=study.study_type
        )

        # Get all data
        queries = self.db.get_queries(study_id)
        responses = self.db.get_study_responses(study_id)
        segments = self.db.get_segments(study_id)

        if not responses:
            logger.warning(f"No responses found for study {study_id}")
            return insights

        owned_domains = study.owned_domains or []

        # 1. Calculate brand metrics
        insights.brand_metrics = self._calculate_brand_metrics(responses)
        insights.brand_metrics.total_queries = len(queries)

        # 2. Calculate segment metrics
        insights.segment_metrics = self._calculate_segment_metrics(
            queries, responses, segments, insights.brand_metrics
        )

        # 3. Discover and analyze competitors
        insights.discovered_competitors, insights.share_of_voice = \
            self._analyze_competitors(responses, study.brand_name)

        # 4. Calculate citation metrics
        insights.citation_metrics = self._calculate_citation_metrics(
            responses, owned_domains, study.brand_name
        )

        # 5. Calculate platform metrics
        insights.platform_metrics = self._calculate_platform_metrics(responses)

        # 6. Generate narrative insights
        insights.key_insights, insights.opportunities, insights.threats = \
            self._generate_insights(insights)

        logger.info(f"Analysis complete for {study.brand_name}")
        return insights

    def _calculate_brand_metrics(self, responses: list) -> BrandMetrics:
        """Calculate core brand performance metrics."""
        metrics = BrandMetrics(total_responses=len(responses))

        if not responses:
            return metrics

        # Count by prominence level
        prominence_counts = Counter(r.brand_prominence for r in responses)

        metrics.featured_first_count = prominence_counts.get("featured_first", 0)
        metrics.recommended_count = prominence_counts.get("recommended", 0)
        metrics.listed_count = prominence_counts.get("listed", 0)
        metrics.mentioned_only_count = prominence_counts.get("mentioned", 0)
        metrics.not_mentioned_count = prominence_counts.get("not_mentioned", 0)

        # Mention includes all levels except not_mentioned
        metrics.mention_count = metrics.total_responses - metrics.not_mentioned_count

        # Calculate rates
        total = metrics.total_responses
        metrics.mention_rate = (metrics.mention_count / total * 100) if total > 0 else 0.0
        metrics.featured_first_rate = (metrics.featured_first_count / total * 100) if total > 0 else 0.0
        metrics.recommended_rate = (metrics.recommended_count / total * 100) if total > 0 else 0.0
        metrics.listed_rate = (metrics.listed_count / total * 100) if total > 0 else 0.0

        # Calculate prominence score
        metrics.prominence_score = self.calculate_prominence_score(responses)

        # Visibility score (combination of mention rate and prominence)
        metrics.visibility_score = (metrics.mention_rate * 0.4) + (metrics.prominence_score * 0.6)

        # Sentiment analysis
        sentiment_counts = Counter(r.brand_sentiment for r in responses if r.brand_mentioned)
        sentiment_total = sum(sentiment_counts.values())
        if sentiment_total > 0:
            metrics.positive_sentiment_rate = sentiment_counts.get("positive", 0) / sentiment_total * 100
            metrics.neutral_sentiment_rate = sentiment_counts.get("neutral", 0) / sentiment_total * 100
            metrics.negative_sentiment_rate = sentiment_counts.get("negative", 0) / sentiment_total * 100

        return metrics

    def _calculate_segment_metrics(
        self,
        queries: list,
        responses: list,
        segments: list,
        overall_metrics: BrandMetrics
    ) -> Dict[str, List[SegmentMetrics]]:
        """Calculate metrics broken down by segment."""

        # Build query -> segments mapping
        query_segments = defaultdict(list)
        segment_info = {s.id: (s.segment_type, s.segment_value) for s in segments}

        for q in queries:
            if hasattr(q, 'segment_ids') and q.segment_ids:
                for seg_id in q.segment_ids:
                    if seg_id in segment_info:
                        query_segments[q.id].append(segment_info[seg_id])

        # Group responses by segment
        segment_responses = defaultdict(list)
        for r in responses:
            if r.query_id in query_segments:
                for seg_type, seg_value in query_segments[r.query_id]:
                    segment_responses[(seg_type, seg_value)].append(r)

        # Calculate metrics for each segment
        result = defaultdict(list)

        for (seg_type, seg_value), seg_responses in segment_responses.items():
            if not seg_responses:
                continue

            mention_count = sum(1 for r in seg_responses if r.brand_mentioned)
            featured_count = sum(1 for r in seg_responses if r.brand_prominence == "featured_first")

            mention_rate = mention_count / len(seg_responses) * 100
            featured_rate = featured_count / len(seg_responses) * 100
            prominence_score = self.calculate_prominence_score(seg_responses)

            metrics = SegmentMetrics(
                segment_type=seg_type,
                segment_value=seg_value,
                query_count=len(set(r.query_id for r in seg_responses)),
                response_count=len(seg_responses),
                mention_rate=mention_rate,
                featured_rate=featured_rate,
                prominence_score=prominence_score,
                mention_rate_delta=mention_rate - overall_metrics.mention_rate,
                prominence_delta=prominence_score - overall_metrics.prominence_score
            )

            result[seg_type].append(metrics)

        # Sort each segment type by prominence score
        for seg_type in result:
            result[seg_type].sort(key=lambda x: x.prominence_score, reverse=True)

        return dict(result)

    def _analyze_competitors(
        self,
        responses: list,
        focal_brand: str
    ) -> Tuple[List[CompetitorMetrics], Dict[str, float]]:
        """
        Discover competitors from data (unbiased approach).

        Returns:
            Tuple of (competitor_metrics_list, share_of_voice_dict)
        """
        # Extract all brand mentions
        all_mentions = []
        featured_counts = Counter()

        for r in responses:
            if r.all_brands_mentioned:
                # Handle both list and pipe-delimited string formats
                if isinstance(r.all_brands_mentioned, list):
                    brands = [b.strip() for b in r.all_brands_mentioned if b and b.strip()]
                else:
                    brands = [b.strip() for b in r.all_brands_mentioned.split('|') if b.strip()]
                all_mentions.extend(brands)

            if r.featured_brand:
                featured_counts[r.featured_brand.strip()] += 1

        mention_counts = Counter(all_mentions)

        # Calculate total mentions for share of voice
        total_mentions = sum(mention_counts.values())

        # Build competitor metrics (exclude focal brand from competitor list)
        competitors = []
        share_of_voice = {}

        focal_lower = focal_brand.lower()

        for brand, mentions in mention_counts.most_common(15):  # Top 15
            brand_lower = brand.lower()

            # Calculate metrics
            featured = featured_counts.get(brand, 0)
            mention_rate = mentions / len(responses) * 100
            featured_rate = featured / len(responses) * 100
            win_rate = (featured / mentions * 100) if mentions > 0 else 0.0

            # Share of voice
            sov = mentions / total_mentions * 100 if total_mentions > 0 else 0.0
            share_of_voice[brand] = sov

            # Skip focal brand in competitor list
            if focal_lower in brand_lower or brand_lower in focal_lower:
                continue

            # Head-to-head vs focal brand
            h2h_wins = 0
            h2h_losses = 0
            h2h_ties = 0

            for r in responses:
                if not r.all_brands_mentioned:
                    continue
                # Handle both list and pipe-delimited string formats
                if isinstance(r.all_brands_mentioned, list):
                    brands_in_response = [b.strip().lower() for b in r.all_brands_mentioned if b]
                else:
                    brands_in_response = [b.strip().lower() for b in r.all_brands_mentioned.split('|')]

                focal_in = any(focal_lower in b or b in focal_lower for b in brands_in_response)
                competitor_in = any(brand_lower in b or b in brand_lower for b in brands_in_response)

                if focal_in and competitor_in:
                    featured_brand_in_response = (r.featured_brand or "").lower()
                    if focal_lower in featured_brand_in_response:
                        h2h_losses += 1  # Focal brand won (competitor lost)
                    elif brand_lower in featured_brand_in_response:
                        h2h_wins += 1   # Competitor won
                    else:
                        h2h_ties += 1

            competitors.append(CompetitorMetrics(
                brand_name=brand,
                mention_count=mentions,
                featured_count=featured,
                mention_rate=mention_rate,
                featured_rate=featured_rate,
                win_rate=win_rate,
                head_to_head_wins=h2h_wins,
                head_to_head_losses=h2h_losses,
                head_to_head_ties=h2h_ties
            ))

        # Sort by mention count
        competitors.sort(key=lambda x: x.mention_count, reverse=True)

        return competitors[:10], share_of_voice

    def _calculate_citation_metrics(
        self,
        responses: list,
        owned_domains: List[str],
        brand_name: str
    ) -> CitationMetrics:
        """Calculate citation intelligence metrics."""
        metrics = CitationMetrics()

        domain_counts = Counter()
        brand_cited_responses = []
        brand_cited_and_won = 0

        for r in responses:
            citations = self.db.get_response_citations(r.id) if hasattr(r, 'id') else []

            for c in citations:
                metrics.total_citations += 1

                domain = self.extract_domain(c.url) if c.url else (c.domain or "unknown")
                domain_counts[domain] += 1

                # Classify tier
                tier = self.classify_domain(domain, owned_domains)
                if tier == 'owned':
                    metrics.owned_citations += 1
                elif tier == 'editorial':
                    metrics.editorial_citations += 1
                elif tier == 'retail':
                    metrics.retail_citations += 1
                elif tier == 'social':
                    metrics.social_citations += 1
                elif tier == 'affiliate':
                    metrics.affiliate_citations += 1
                elif tier == 'reference':
                    metrics.reference_citations += 1
                else:
                    metrics.other_citations += 1

            # Check if brand's site was cited in this response
            brand_cited = any(
                self.classify_domain(
                    self.extract_domain(c.url) if c.url else (c.domain or ""),
                    owned_domains
                ) == 'owned'
                for c in citations
            )

            if brand_cited:
                metrics.times_brand_cited += 1
                if r.brand_prominence == "featured_first":
                    brand_cited_and_won += 1

        # Content Conversion Rate
        metrics.wins_when_cited = brand_cited_and_won
        if metrics.times_brand_cited > 0:
            metrics.content_conversion_rate = (
                brand_cited_and_won / metrics.times_brand_cited * 100
            )

        # Top citing domains
        metrics.top_domains = domain_counts.most_common(10)

        return metrics

    def _calculate_platform_metrics(self, responses: list) -> List[PlatformMetrics]:
        """Calculate metrics by AI platform."""
        platform_responses = defaultdict(list)

        for r in responses:
            platform_responses[r.platform].append(r)

        result = []
        for platform, platform_resps in sorted(platform_responses.items()):
            mention_count = sum(1 for r in platform_resps if r.brand_mentioned)
            featured_count = sum(1 for r in platform_resps if r.brand_prominence == "featured_first")

            # Count citations per response
            total_citations = 0
            for r in platform_resps:
                citations = self.db.get_response_citations(r.id) if hasattr(r, 'id') else []
                total_citations += len(citations)

            result.append(PlatformMetrics(
                platform=platform,
                response_count=len(platform_resps),
                mention_rate=mention_count / len(platform_resps) * 100 if platform_resps else 0.0,
                featured_rate=featured_count / len(platform_resps) * 100 if platform_resps else 0.0,
                prominence_score=self.calculate_prominence_score(platform_resps),
                avg_citations_per_response=total_citations / len(platform_resps) if platform_resps else 0.0
            ))

        return result

    def _generate_insights(
        self,
        insights: StudyInsights
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate narrative insights from computed metrics.

        Returns:
            Tuple of (key_insights, opportunities, threats)
        """
        key_insights = []
        opportunities = []
        threats = []

        bm = insights.brand_metrics

        # Overall visibility assessment
        if bm.visibility_score >= 70:
            key_insights.append(
                f"Strong AI visibility with {bm.visibility_score:.1f}% composite score. "
                f"{insights.brand_name} is well-positioned in AI-driven discovery."
            )
        elif bm.visibility_score >= 40:
            key_insights.append(
                f"Moderate AI visibility ({bm.visibility_score:.1f}% composite score). "
                f"Room for improvement in prominence positioning."
            )
        else:
            threats.append(
                f"Low AI visibility ({bm.visibility_score:.1f}% composite score). "
                f"Brand is at risk of being overlooked in AI recommendations."
            )

        # Mention vs Featured gap
        if bm.mention_rate > 0 and (bm.featured_first_rate / bm.mention_rate) < 0.3:
            opportunities.append(
                f"Conversion opportunity: {bm.mention_rate:.1f}% mention rate but only "
                f"{bm.featured_first_rate:.1f}% featured-first rate. Focus on authoritative "
                f"content that positions brand as the top recommendation."
            )

        # Segment analysis
        for seg_type, metrics_list in insights.segment_metrics.items():
            if not metrics_list:
                continue

            # Best performing segment
            best = metrics_list[0]
            if best.prominence_delta > 10:
                key_insights.append(
                    f"Strong performance in {seg_type}='{best.segment_value}' "
                    f"(+{best.prominence_delta:.1f} vs overall). Leverage this strength."
                )

            # Underperforming segments
            worst = metrics_list[-1]
            if worst.prominence_delta < -10:
                opportunities.append(
                    f"Underperformance in {seg_type}='{worst.segment_value}' "
                    f"({worst.prominence_delta:.1f} vs overall). Content gap opportunity."
                )

        # Competitor threats
        for comp in insights.discovered_competitors[:3]:
            if comp.head_to_head_wins > comp.head_to_head_losses:
                threats.append(
                    f"{comp.brand_name} outperforms in head-to-head comparisons "
                    f"({comp.head_to_head_wins}W/{comp.head_to_head_losses}L). "
                    f"Analyze their content strategy."
                )

        # Citation analysis
        cm = insights.citation_metrics
        if cm.content_conversion_rate > 0:
            if cm.content_conversion_rate < 40:
                opportunities.append(
                    f"Content Conversion Rate is {cm.content_conversion_rate:.1f}% — "
                    f"AI consults brand content but doesn't recommend. "
                    f"Audit cited pages for conversion signals."
                )
            elif cm.content_conversion_rate > 60:
                key_insights.append(
                    f"Strong Content Conversion Rate ({cm.content_conversion_rate:.1f}%) — "
                    f"When AI cites brand content, it often recommends the brand."
                )

        # Platform variance
        if insights.platform_metrics:
            scores = [p.prominence_score for p in insights.platform_metrics]
            if max(scores) - min(scores) > 20:
                best_platform = max(insights.platform_metrics, key=lambda x: x.prominence_score)
                worst_platform = min(insights.platform_metrics, key=lambda x: x.prominence_score)
                key_insights.append(
                    f"Platform variance detected: {best_platform.platform} "
                    f"({best_platform.prominence_score:.1f}) vs {worst_platform.platform} "
                    f"({worst_platform.prominence_score:.1f}). Platform-specific optimization may help."
                )

        return key_insights, opportunities, threats

    def format_summary(self, insights: StudyInsights) -> str:
        """Format insights as a readable summary."""
        lines = []

        lines.append(f"\n{'='*70}")
        lines.append(f"  ANALYSIS SUMMARY: {insights.brand_name}")
        lines.append(f"{'='*70}\n")

        bm = insights.brand_metrics

        lines.append("BRAND METRICS")
        lines.append("-" * 40)
        lines.append(f"Total Responses: {bm.total_responses}")
        lines.append(f"Mention Rate: {bm.mention_rate:.1f}%")
        lines.append(f"Featured First Rate: {bm.featured_first_rate:.1f}%")
        lines.append(f"Prominence Score: {bm.prominence_score:.1f}")
        lines.append(f"Visibility Score: {bm.visibility_score:.1f}")
        lines.append("")

        lines.append("PROMINENCE DISTRIBUTION")
        lines.append("-" * 40)
        lines.append(f"Featured First: {bm.featured_first_count} ({bm.featured_first_rate:.1f}%)")
        lines.append(f"Recommended: {bm.recommended_count} ({bm.recommended_rate:.1f}%)")
        lines.append(f"Listed: {bm.listed_count} ({bm.listed_rate:.1f}%)")
        lines.append(f"Mentioned Only: {bm.mentioned_only_count}")
        lines.append(f"Not Mentioned: {bm.not_mentioned_count}")
        lines.append("")

        if insights.discovered_competitors:
            lines.append("TOP COMPETITORS (Discovered)")
            lines.append("-" * 40)
            lines.append(f"{'Brand':<20} {'Mentions':<10} {'Featured':<10} {'H2H':<10}")
            for comp in insights.discovered_competitors[:5]:
                h2h = f"{comp.head_to_head_wins}W/{comp.head_to_head_losses}L"
                lines.append(f"{comp.brand_name:<20} {comp.mention_count:<10} {comp.featured_count:<10} {h2h:<10}")
            lines.append("")

        if insights.platform_metrics:
            lines.append("PLATFORM COMPARISON")
            lines.append("-" * 40)
            lines.append(f"{'Platform':<15} {'Mention%':<10} {'Featured%':<10} {'Score':<10}")
            for pm in sorted(insights.platform_metrics, key=lambda x: x.prominence_score, reverse=True):
                lines.append(f"{pm.platform:<15} {pm.mention_rate:>6.1f}%   {pm.featured_rate:>6.1f}%    {pm.prominence_score:>5.1f}")
            lines.append("")

        cm = insights.citation_metrics
        if cm.total_citations > 0:
            lines.append("CITATION ANALYSIS")
            lines.append("-" * 40)
            lines.append(f"Total Citations: {cm.total_citations}")
            lines.append(f"  Owned: {cm.owned_citations}")
            lines.append(f"  Editorial: {cm.editorial_citations}")
            lines.append(f"  Retail: {cm.retail_citations}")
            lines.append(f"  Social: {cm.social_citations}")
            lines.append(f"  Other: {cm.other_citations + cm.affiliate_citations + cm.reference_citations}")
            lines.append(f"Content Conversion Rate: {cm.content_conversion_rate:.1f}%")
            lines.append("")

        if insights.key_insights:
            lines.append("KEY INSIGHTS")
            lines.append("-" * 40)
            for insight in insights.key_insights:
                lines.append(f"• {insight}")
            lines.append("")

        if insights.opportunities:
            lines.append("OPPORTUNITIES")
            lines.append("-" * 40)
            for opp in insights.opportunities:
                lines.append(f"• {opp}")
            lines.append("")

        if insights.threats:
            lines.append("THREATS")
            lines.append("-" * 40)
            for threat in insights.threats:
                lines.append(f"• {threat}")
            lines.append("")

        return "\n".join(lines)

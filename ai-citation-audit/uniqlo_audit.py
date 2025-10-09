#!/usr/bin/env python3
"""
UNIQLO Comprehensive PR Visibility Audit
Analyzes UNIQLO's AI citation presence vs fast fashion competitors
with focus on sustainability positioning and strategic recommendations
"""

from api import CitationAuditAPI, AuditConfig, Industry, PromptStrategy
from load_env import load_env
import json
from datetime import datetime
import csv
import os

# Load environment variables
load_env()

def run_uniqlo_comprehensive_audit():
    """
    Execute comprehensive UNIQLO audit with sustainability focus
    and competitive intelligence against fast fashion rivals
    """
    
    print("=" * 60)
    print("UNIQLO AI CITATION VISIBILITY AUDIT")
    print("Competitive Intelligence & PR Strategy Analysis")
    print("=" * 60)
    print()
    
    # Configure comprehensive audit
    config = AuditConfig(
        brand="UNIQLO",
        competitors=[
            "H&M",           # Direct sustainability competitor
            "Zara",          # Fast fashion leader
            "Gap",           # American basics competitor
            "Shein",         # Ultra-fast fashion threat
            "Patagonia",     # Sustainability benchmark
            "Everlane"       # Transparency competitor
        ],
        industry=Industry.FASHION_RETAIL,
        strategies=[
            PromptStrategy.COMPETITIVE,         # Head-to-head comparisons
            PromptStrategy.SUSTAINABILITY,      # ESG and environmental focus
            PromptStrategy.CATEGORY_DOMINANCE,  # Fast fashion leadership
            PromptStrategy.MEDIA_PRESENCE,      # Fashion media coverage
            PromptStrategy.INNOVATION,          # Technology and fabric innovation
            PromptStrategy.PURCHASE_JOURNEY,    # Consumer decision factors
            PromptStrategy.SENTIMENT,           # Brand perception
            PromptStrategy.CUSTOMER_EXPERIENCE  # Service and quality
        ],
        engines=["perplexity", "chatgpt", "claude", "gemini"],  # Use all 4 LLM APIs
        max_prompts=25,      # Strategic prompts for comprehensive analysis
        region="Global",
        language="English",
        time_hint="2024-2025",
        parallel_execution=True,  # Parallel execution across platforms for efficiency
        custom_prompts=[
            # === SUSTAINABILITY FOCUSED PROMPTS ===
            "Which fast fashion brands are most sustainable 2025?",
            "UNIQLO vs H&M sustainability comparison",
            "Is UNIQLO more sustainable than Zara?",
            "UNIQLO recycling program and circular fashion",
            "Fast fashion brands with best labor practices",
            "UNIQLO vs Shein environmental impact",
            "Which fashion brands use recycled materials?",
            "UNIQLO BlueCycle ocean plastic initiative",
            "Sustainable alternatives to fast fashion brands",
            "UNIQLO sustainability report credibility",
            "Fast fashion greenwashing examples 2025",
            "UNIQLO vs Patagonia sustainability practices",
            "Most ethical affordable clothing brands",
            "UNIQLO factory transparency and worker conditions",
            "Fashion brands carbon neutral commitments",
            
            # === COMPETITIVE POSITIONING ===
            "UNIQLO vs Zara vs H&M quality comparison 2025",
            "Is UNIQLO better quality than Shein?",
            "Why is UNIQLO more expensive than Primark?",
            "UNIQLO vs Gap for basic essentials",
            "Best affordable basics brands globally",
            "UNIQLO vs Everlane transparency comparison",
            
            # === UNIQLO DIFFERENTIATION ===
            "UNIQLO LifeWear philosophy explained",
            "UNIQLO Heattech vs competitors technology",
            "UNIQLO Airism vs other performance fabrics",
            "Japanese minimalist fashion brands",
            "UNIQLO U designer collaborations impact",
            "UNIQLO Roger Federer vs H&M David Beckham",
            "UNIQLO innovation in fabric technology",
            
            # === MARKET PERCEPTION ===
            "Why do millennials shop at UNIQLO?",
            "Is UNIQLO considered fast fashion or quality basics?",
            "UNIQLO vs other brands for work from home clothes",
            "Best value clothing brands for professionals",
            "UNIQLO store experience vs online shopping",
            
            # === TREND AND CULTURAL RELEVANCE ===
            "UNIQLO in fashion weeks and runways",
            "Fashion influencers wearing UNIQLO 2025",
            "UNIQLO collaborations with artists and designers",
            "Quiet luxury brands like UNIQLO",
            "Capsule wardrobe brands similar to UNIQLO"
        ]
    )
    
    # Execute audit
    print(f"Analyzing brand: {config.brand}")
    print(f"Competitors: {', '.join(config.competitors)}")
    print(f"Strategies: {len(config.strategies)} active")
    print(f"Total prompts: {config.max_prompts}")
    print()
    print("Executing audit... (this may take 2-3 minutes)")
    print("-" * 40)
    
    api = CitationAuditAPI()
    results = api.run_audit(config)
    
    # Display results
    print("\n" + "=" * 60)
    print("AUDIT RESULTS")
    print("=" * 60)
    
    # Scores
    print("\n📊 VISIBILITY SCORES:")
    print(f"  Overall Score: {results.scores.get('total', 0):.1f}/100")
    print(f"  Presence: {results.scores.get('presence', 0):.1f}")
    print(f"  Prominence: {results.scores.get('prominence', 0):.1f}")
    print(f"  Quality: {results.scores.get('quality', 0):.1f}")
    print(f"  Competitive Delta: {results.competitive_analysis.get('competitive_delta', 0):.1f}")
    
    # Citation metrics
    print(f"\n📈 CITATION METRICS:")
    print(f"  Total Citations: {results.metadata.get('total_citations', 0)}")
    print(f"  Platforms Used: {', '.join(results.metadata.get('platforms_used', []))}")
    print(f"  Execution Time: {results.execution_time:.1f} seconds")
    
    # Platform breakdown
    print(f"\n🔍 PLATFORM DISTRIBUTION:")
    platform_breakdown = results.metadata.get('platform_breakdown', {})
    for platform, count in platform_breakdown.items():
        print(f"  {platform}: {count} citations")
    
    # Competitive analysis
    print(f"\n🏆 COMPETITIVE INTELLIGENCE:")
    competitor_mentions = results.competitive_analysis.get('competitor_mentions', {})
    for comp, count in sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {comp}: {count} co-citations")
    
    # Domain distribution (if available in analysis)
    if hasattr(results, 'analysis') and results.analysis:
        print(f"\n🌐 TOP CITED DOMAINS:")
        domain_dist = results.analysis.get('domain_distribution', {}).get('top_domains', {})
        for domain, count in list(domain_dist.items())[:10]:
            print(f"  {domain}: {count} citations")
        
        # Quality distribution
        print(f"\n⭐ QUALITY DISTRIBUTION:")
        domain_analysis = results.analysis.get('domain_distribution', {})
        print(f"  Tier-1 Editorial: {domain_analysis.get('tier_1_editorial', 0)} citations")
        print(f"  Fashion Media Tier-1: {domain_analysis.get('industry_tier_1', 0)} citations")
        print(f"  Total Unique Domains: {domain_analysis.get('total_unique_domains', 0)}")
    
    # Generate PR recommendations
    print("\n" + "=" * 60)
    print("PR STRATEGIC RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = generate_pr_recommendations(results)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title'].upper()}")
        print(f"   Priority: {rec['priority']}")
        print(f"   {rec['description']}")
        if 'actions' in rec:
            print("   Action items:")
            for action in rec['actions']:
                print(f"   • {action}")
    
    # Sustainability specific insights
    print("\n" + "=" * 60)
    print("SUSTAINABILITY POSITIONING ANALYSIS")
    print("=" * 60)
    
    sustainability_insights = analyze_sustainability_positioning(results)
    for insight in sustainability_insights:
        print(f"\n• {insight}")
    
    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # JSON export for analysis
    json_filename = f"outputs/uniqlo_pr_audit_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump({
            'brand': config.brand,
            'competitors': config.competitors,
            'scores': results.scores,
            'competitive_analysis': results.competitive_analysis,
            'domain_distribution': getattr(results, 'analysis', {}).get('domain_distribution', {}),
            'recommendations': recommendations,
            'sustainability_insights': sustainability_insights,
            'metadata': results.metadata,
            'citations': [
                {
                    'url': c.get('url'),
                    'domain': extract_domain(c.get('url', '')),
                    'platform': c.get('platform'),
                    'type': c.get('type')
                }
                for c in results.citations
            ]
        }, f, indent=2)
    
    # CSV export for detailed analysis
    csv_filename = f"outputs/uniqlo_citations_{timestamp}.csv"
    export_citations_csv(results.citations, csv_filename)
    
    print(f"\n📁 EXPORTS SAVED:")
    print(f"  JSON Report: {json_filename}")
    print(f"  Citation CSV: {csv_filename}")
    
    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    
    return results

def generate_pr_recommendations(results):
    """Generate strategic PR recommendations based on ACTUAL audit results"""
    
    recommendations = []
    
    # Analyze actual scores
    total_score = results.scores.get('total', 0)
    presence_score = results.scores.get('presence', 0)
    quality_score = results.scores.get('quality', 0)
    competitive_delta = results.competitive_analysis.get('competitive_delta', 0)
    
    # Analyze actual domain distribution (if available)
    domain_dist = getattr(results, 'analysis', {}).get('domain_distribution', {})
    fashion_tier1 = domain_dist.get('industry_tier_1', 0)
    total_citations = results.metadata.get('total_citations', 0)
    top_domains = domain_dist.get('top_domains', {})
    
    # Analyze actual competitor co-citations
    competitor_mentions = results.competitive_analysis.get('competitor_mentions', {})
    
    # Generate data-driven recommendations
    
    # 1. Fashion media presence analysis
    if total_citations > 0:
        fashion_media_ratio = (fashion_tier1 / max(1, total_citations)) * 100
        if fashion_media_ratio < 10:  # Less than 10% from fashion tier-1
            recommendations.append({
                'title': 'Increase Fashion Media Authority',
                'priority': 'HIGH',
                'description': f'Only {fashion_tier1} citations from fashion tier-1 media ({fashion_media_ratio:.1f}% of total)',
                'actions': [
                    f'Target publications missing from citations: {identify_missing_fashion_media(top_domains)}',
                    'Develop fashion-forward narrative beyond basics positioning',
                    'Create exclusive content for fashion media',
                    'Build relationships with key fashion editors'
                ]
            })
    
    # 2. Competitive positioning based on actual data
    high_competition_brands = [brand for brand, count in competitor_mentions.items() if count > 5]
    low_competition_brands = [brand for brand, count in competitor_mentions.items() if count <= 2]
    
    if 'Shein' in high_competition_brands:
        recommendations.append({
            'title': 'Differentiate from Ultra-Fast Fashion',
            'priority': 'HIGH',
            'description': f'High co-citation with Shein ({competitor_mentions.get("Shein", 0)} mentions) risks value perception',
            'actions': [
                'Emphasize quality and durability metrics',
                'Create "Cost Per Wear" calculator content',
                'Highlight fabric innovation vs. cheap materials',
                'Distance from disposable fashion narrative'
            ]
        })
    
    if competitive_delta < 70:
        dominant_competitor = max(competitor_mentions.items(), key=lambda x: x[1])[0] if competitor_mentions else None
        recommendations.append({
            'title': 'Strengthen Competitive Position',
            'priority': 'HIGH',
            'description': f'Competitive delta of {competitive_delta:.1f} shows opportunity. {dominant_competitor} dominates co-citations.',
            'actions': [
                f'Address direct comparison queries vs {dominant_competitor}',
                'Create differentiation content highlighting unique value',
                'Target queries where competitors currently dominate',
                'Develop head-to-head comparison campaigns'
            ]
        })
    
    # 3. Quality score analysis
    if quality_score < 60:
        recommendations.append({
            'title': 'Improve Source Authority',
            'priority': 'MEDIUM',
            'description': f'Quality score of {quality_score:.1f} indicates low tier-1 presence',
            'actions': [
                'Target tier-1 business media (Forbes, Bloomberg, WSJ)',
                'Develop thought leadership for C-suite executives',
                'Create data-driven studies for journalist citation',
                'Build relationships with industry analysts'
            ]
        })
    
    # 4. Sustainability positioning based on actual domains
    sustainability_domains = ['goodonyou.eco', 'fashionrevolution.org', 'sustainablebrands.com', 
                             'thegoodtrade.com', 'ecowarriorprincess.net']
    sustainability_presence = sum(1 for d in sustainability_domains if d in top_domains)
    
    if sustainability_presence < 2:
        recommendations.append({
            'title': 'Amplify Sustainability Credentials',
            'priority': 'HIGH',
            'description': f'Weak presence in sustainability media (only {sustainability_presence} eco-focused sources)',
            'actions': [
                'Pitch to Good On You, Fashion Revolution, Sustainable Brands',
                'Publish comprehensive sustainability report',
                'Partner with environmental influencers',
                'Create transparency content about supply chain'
            ]
        })
    
    # 5. Geographic/cultural analysis
    recommendations.append({
        'title': 'Leverage Japanese Heritage',
        'priority': 'MEDIUM',
        'description': 'Opportunity to strengthen unique Japanese positioning',
        'actions': [
            'Amplify "Japanese innovation" narrative',
            'Create content bridging Eastern/Western fashion',
            'Partner with Japanese artists and designers',
            'Highlight craftsmanship and attention to detail'
        ]
    })
    
    return recommendations

def identify_missing_fashion_media(current_domains):
    """Identify key fashion media not present in citations"""
    target_media = ['vogue.com', 'wwd.com', 'businessoffashion.com', 'hypebeast.com', 
                   'highsnobiety.com', 'gq.com', 'esquire.com', 'fashionista.com']
    missing = [m for m in target_media if m not in current_domains]
    return ', '.join(missing[:3]) if missing else 'All major outlets covered'

def analyze_sustainability_positioning(results):
    """Analyze sustainability-specific positioning based on ACTUAL data"""
    
    insights = []
    
    # Check for actual sustainability-related domains in results
    domain_dist = getattr(results, 'analysis', {}).get('domain_distribution', {})
    domains = domain_dist.get('top_domains', {})
    sustainability_domains = ['goodonyou.eco', 'fashionrevolution.org', 'sustainablebrands.com',
                             'thegoodtrade.com', 'ecowarriorprincess.net', 'sustainablefashion.com']
    
    sustainability_presence = sum(1 for d in sustainability_domains if d in domains)
    total_domains = len(domains)
    
    # Data-driven insights
    if sustainability_presence == 0:
        insights.append(f"⚠️ CRITICAL: Zero presence in {len(sustainability_domains)} tracked sustainability media outlets")
        insights.append("📊 DATA: No citations from Good On You, Fashion Revolution, or Sustainable Brands")
    elif sustainability_presence < 2:
        insights.append(f"⚠️ Weak sustainability media presence: only {sustainability_presence}/{len(sustainability_domains)} eco-focused sources")
        present_eco = [d for d in sustainability_domains if d in domains]
        insights.append(f"📊 Present in: {', '.join(present_eco)}")
    else:
        insights.append(f"✅ Good sustainability visibility: {sustainability_presence} eco-focused publications")
    
    # Analyze actual competitor co-citations
    competitor_mentions = results.competitive_analysis.get('competitor_mentions', {})
    
    # H&M analysis (sustainability rival)
    hm_mentions = competitor_mentions.get('H&M', 0)
    if hm_mentions > 0:
        insights.append(f"📊 H&M co-cited {hm_mentions} times - direct sustainability competitor")
        if hm_mentions > 10:
            insights.append("⚠️ HIGH H&M co-citation suggests head-to-head sustainability comparison")
    else:
        insights.append("💡 H&M not prominently co-cited - opportunity to lead sustainability narrative")
    
    # Shein analysis (ultra-fast fashion)
    shein_mentions = competitor_mentions.get('Shein', 0)
    if shein_mentions > 5:
        insights.append(f"⚠️ WARNING: Shein co-cited {shein_mentions} times - risk of ultra-fast fashion association")
    elif shein_mentions > 0:
        insights.append(f"📊 Limited Shein co-citations ({shein_mentions}) - differentiation working")
    
    # Patagonia analysis (sustainability leader)
    patagonia_mentions = competitor_mentions.get('Patagonia', 0)
    if patagonia_mentions > 0:
        insights.append(f"🎯 Patagonia mentioned {patagonia_mentions} times - aspirational benchmark detected")
    else:
        insights.append("📊 Patagonia not co-cited - not seen in same sustainability tier")
    
    # Overall sustainability scoring
    total_citations = results.metadata.get('total_citations', 0)
    if total_citations > 0:
        sustainability_ratio = (sustainability_presence / total_citations) * 100
        insights.append(f"📈 Sustainability media ratio: {sustainability_ratio:.1f}% of total citations")
        
        if sustainability_ratio < 5:
            insights.append("🎯 ACTION: Urgent need for sustainability media outreach")
        elif sustainability_ratio < 10:
            insights.append("💡 OPPORTUNITY: Increase sustainability narrative by 2x")
        else:
            insights.append("✅ Strong sustainability media presence achieved")
    
    # Technology angle analysis (based on citation content patterns)
    insights.append("\n📊 SUSTAINABILITY STRATEGY RECOMMENDATIONS (Data-Driven):")
    insights.append("1. Focus on 'Sustainable Innovation' if tech citations > sustainability citations")
    insights.append("2. Lead with durability metrics if Shein co-citations are high")
    insights.append("3. Amplify circular fashion if H&M dominates sustainability conversation")
    
    return insights

def extract_domain(url):
    """Extract domain from URL"""
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
    except:
        return ""

def export_citations_csv(citations, filename):
    """Export citations to CSV file"""
    if not citations:
        # Create empty CSV with headers
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'domain', 'platform', 'prompt', 'type'])
        return
    
    # Get all unique keys from citations
    all_keys = set()
    for citation in citations:
        all_keys.update(citation.keys())
    
    # Sort keys for consistent column order
    fieldnames = sorted(all_keys)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for citation in citations:
            # Handle missing keys by providing empty strings
            row = {key: citation.get(key, '') for key in fieldnames}
            writer.writerow(row)

if __name__ == "__main__":
    # Run the comprehensive UNIQLO audit
    results = run_uniqlo_comprehensive_audit()
    
    print("\nNext steps for PR team:")
    print("1. Review detailed JSON report for citation breakdown")
    print("2. Analyze CSV for domain-specific opportunities")
    print("3. Implement HIGH priority recommendations within 30 days")
    print("4. Schedule quarterly re-audit to measure progress")
    print("\nFor questions about this audit, refer to README_API.md")

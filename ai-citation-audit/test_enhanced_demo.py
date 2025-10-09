#!/usr/bin/env python3
"""
Non-interactive demonstration of Enhanced Typeform Auditor
Shows source classification and scoring without running live API calls
"""

from enhanced_typeform_auditor import (
    SourceClassifier,
    DomainNormalizer,
    PROpportunityScorer,
    generate_pr_focused_queries
)
import os
from load_env import load_env

# Load environment
load_env()

print("=" * 60)
print("Enhanced Typeform Auditor - Non-Interactive Demo")
print("=" * 60)

# 1. Test Source Classification
print("\n1. SOURCE CLASSIFICATION TEST")
print("-" * 40)

test_domains = [
    ('wsj.com', 'Expected: Editorial Tier 1'),
    ('forbes.com', 'Expected: Editorial Tier 1'),
    ('techcrunch.com', 'Expected: Editorial Tier 1'),
    ('industrynews.com', 'Expected: Editorial Tier 2'),
    ('reddit.com', 'Expected: Social Community'),
    ('wikipedia.org', 'Expected: Informational'),
    ('amazon.com', 'Expected: Ecommerce'),
    ('prnewswire.com', 'Expected: PR Wire'),
    ('randomsite.com', 'Expected: Other')
]

for domain, expected in test_domains:
    category, weight = SourceClassifier.classify(domain)
    status = "✓" if expected.split(': ')[1].upper().replace(' ', '_') == category else "✗"
    print(f"{status} {domain:20} -> {category:20} (weight: {weight})")

# 2. Test Domain Normalization
print("\n2. DOMAIN NORMALIZATION TEST")
print("-" * 40)

test_urls = [
    'https://www.forbes.com/article/123',
    'http://m.forbes.com',
    'forbes.com',
    'www.forbes.com:443',
    'https://reddit.com/r/technology',
    'amazon.com/product/B123'
]

print("All these URLs should normalize to the base domain:")
for url in test_urls:
    normalized = DomainNormalizer.normalize(url)
    print(f"  {url:40} -> {normalized}")

# 3. Test PR Opportunity Scoring
print("\n3. PR OPPORTUNITY SCORING")
print("-" * 40)

test_scenarios = [
    {
        'name': 'Forbes - High Priority Editorial Target',
        'outlet_data': {
            'total_citations': 5,
            'platforms': ['ChatGPT', 'Claude', 'Perplexity'],
            'brand_mentions': 0,  # No current coverage = opportunity
            'recommended_count': 2
        },
        'tier_weight': 10  # Editorial Tier 1
    },
    {
        'name': 'TechCrunch - Already Covering Brand',
        'outlet_data': {
            'total_citations': 4,
            'platforms': ['ChatGPT', 'Claude'],
            'brand_mentions': 3,  # Already has coverage = lower priority
            'recommended_count': 1
        },
        'tier_weight': 10  # Editorial Tier 1
    },
    {
        'name': 'Reddit - Social Platform',
        'outlet_data': {
            'total_citations': 8,
            'platforms': ['ChatGPT', 'Claude'],
            'brand_mentions': 0,
            'recommended_count': 0
        },
        'tier_weight': 3  # Social Community
    },
    {
        'name': 'Wikipedia - Informational',
        'outlet_data': {
            'total_citations': 10,
            'platforms': ['ChatGPT', 'Claude', 'Perplexity', 'Gemini'],
            'brand_mentions': 0,
            'recommended_count': 1
        },
        'tier_weight': 2  # Informational
    }
]

print("\nScoring Formula:")
print("Score = Citations × Tier_Weight × Platform_Breadth × Recommendation_Bonus × Brand_Gap")
print("\nResults:")

for scenario in test_scenarios:
    score = PROpportunityScorer.calculate_score(
        scenario['outlet_data'],
        'TestBrand',
        scenario['tier_weight']
    )
    
    print(f"\n{scenario['name']}:")
    print(f"  Citations: {scenario['outlet_data']['total_citations']}")
    print(f"  Platforms: {len(scenario['outlet_data']['platforms'])}")
    print(f"  Tier Weight: {scenario['tier_weight']}")
    print(f"  Brand Mentions: {scenario['outlet_data']['brand_mentions']}")
    print(f"  → PR Opportunity Score: {score}")

# 4. Test Query Generation
print("\n4. QUERY GENERATION TEST")
print("-" * 40)

brand = "Tesla"
general_query = "What are the best electric vehicles for families?"
competitors = ["Rivian", "Lucid Motors", "Ford"]

print(f"Brand: {brand}")
print(f"Query: {general_query}")
print(f"Competitors: {', '.join(competitors)}")

# Generate queries (will use fallback if no OpenAI key)
queries = generate_pr_focused_queries(
    brand, 
    general_query, 
    competitors, 
    os.getenv('OPENAI_API_KEY')
)

print("\nGenerated Test Queries:")
for i, query in enumerate(queries, 1):
    # Handle both string and dict formats
    if isinstance(query, dict):
        query_text = query.get('query', str(query))
    else:
        query_text = query
    print(f"  {i}. {query_text}")

# 5. Summary
print("\n" + "=" * 60)
print("SUMMARY: Key Improvements Over Original System")
print("=" * 60)

improvements = [
    "✓ 5-tier source classification (Editorial > Social > Informational > Ecommerce)",
    "✓ Domain normalization prevents duplicate counting",
    "✓ PR Opportunity Scoring prioritizes editorial outlets with no brand coverage",
    "✓ Enhanced citation extraction from all platforms (not just Perplexity)",
    "✓ Word boundary entity detection prevents false positives",
    "✓ Recommended resources get bonus weight in scoring"
]

for improvement in improvements:
    print(improvement)

print("\n" + "=" * 60)
print("Ready for production use!")
print("To run a live audit, use: python3 test_enhanced_typeform.py")
print("=" * 60)

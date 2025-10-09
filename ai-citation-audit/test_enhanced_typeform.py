#!/usr/bin/env python3
"""
Test script for Enhanced Typeform Auditor
Demonstrates PR-focused citation analysis with proper source classification
"""

import os
import json
from datetime import datetime
from enhanced_typeform_auditor import (
    EnhancedTypeformAuditor,
    SourceClassifier,
    generate_pr_focused_queries
)

# Load environment variables
from load_env import load_env
load_env()


def test_source_classification():
    """Test the source classifier"""
    print("\n=== Testing Source Classification ===\n")
    
    test_domains = [
        'wsj.com',           # Editorial Tier 1
        'forbes.com',        # Editorial Tier 1
        'industrynews.com',  # Editorial Tier 2
        'reddit.com',        # Social
        'wikipedia.org',     # Informational
        'amazon.com',        # Ecommerce
        'prnewswire.com',    # PR Wire
        'randomsite.com'     # Other
    ]
    
    for domain in test_domains:
        category, weight = SourceClassifier.classify(domain)
        print(f"{domain:20} -> {category:20} (weight: {weight})")


def run_sample_audit():
    """Run a sample audit with test data"""
    print("\n=== Running Sample Audit ===\n")
    
    # Sample configuration
    brand = "Tesla"
    competitors = ["Rivian", "Lucid Motors", "Ford"]
    
    # Generate PR-focused queries
    openai_key = os.getenv('OPENAI_API_KEY')
    general_query = "What are the best electric vehicles for families?"
    
    print(f"Brand: {brand}")
    print(f"Competitors: {', '.join(competitors)}")
    print(f"General Query: {general_query}\n")
    
    # Generate queries
    queries = generate_pr_focused_queries(brand, general_query, competitors, openai_key)
    
    print("Generated Test Queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    
    # Check if we have API keys
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_perplexity = bool(os.getenv('PERPLEXITY_API_KEY') or os.getenv('PPLX_API_KEY'))
    has_gemini = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'))
    
    print(f"\nAPI Keys Available:")
    print(f"  OpenAI (ChatGPT): {'✓' if has_openai else '✗'}")
    print(f"  Anthropic (Claude): {'✓' if has_anthropic else '✗'}")
    print(f"  Perplexity: {'✓' if has_perplexity else '✗'}")
    print(f"  Gemini: {'✓' if has_gemini else '✗'}")
    
    if not any([has_openai, has_anthropic, has_perplexity, has_gemini]):
        print("\n⚠️  No API keys found. Please set at least one API key to run the audit.")
        return
    
    # Run the audit (limit to 2 queries for testing)
    print(f"\n🚀 Starting audit with {min(2, len(queries))} queries...")
    auditor = EnhancedTypeformAuditor(brand, competitors, queries[:2])
    
    try:
        analysis = auditor.run_audit()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Save full analysis
        analysis_file = f"enhanced_audit_{brand}_{timestamp}.json"
        auditor.save_analysis(analysis_file)
        print(f"\n✓ Full analysis saved to: {analysis_file}")
        
        # Export PR targets
        pr_targets_file = f"pr_targets_{brand}_{timestamp}.csv"
        auditor.export_pr_targets_csv(pr_targets_file)
        print(f"✓ PR targets exported to: {pr_targets_file}")
        
        # Display summary
        print("\n=== Audit Summary ===\n")
        print(f"Brand: {analysis['brand']}")
        print(f"Total Queries: {analysis['total_queries']}")
        print(f"Total Results: {analysis['total_results']}")
        print(f"Brand Mention Rate: {analysis['brand_mention_rate']}%")
        
        # Show outlets by category
        print("\n=== Outlets by Category ===\n")
        for category, outlets in analysis['outlets_by_category'].items():
            if outlets:
                print(f"\n{category} ({len(outlets)} outlets):")
                for outlet in outlets[:3]:  # Show top 3 per category
                    print(f"  • {outlet['domain']}")
                    print(f"    Score: {outlet['pr_opportunity_score']} | Citations: {outlet['total_citations']} | Brand Mentions: {outlet['brand_mentions']}")
        
        # Show top PR targets
        if analysis['top_pr_targets']:
            print("\n=== Top PR Targets (Editorial with no brand coverage) ===\n")
            for i, target in enumerate(analysis['top_pr_targets'][:5], 1):
                print(f"{i}. {target['domain']}")
                print(f"   Category: {target['category']}")
                print(f"   PR Opportunity Score: {target['pr_opportunity_score']}")
                print(f"   Citations: {target['total_citations']} across {target['platform_count']} platforms")
                print(f"   Recommended: {'Yes' if target['recommended_count'] > 0 else 'No'}")
                if target['sample_context']:
                    print(f"   Context: {target['sample_context'][:100]}...")
                print()
        
        # Show methodology
        print("\n=== Methodology ===\n")
        for key, value in analysis['methodology'].items():
            print(f"• {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_scoring():
    """Demonstrate the PR opportunity scoring system"""
    print("\n=== PR Opportunity Scoring Demonstration ===\n")
    
    from enhanced_typeform_auditor import PROpportunityScorer
    
    # Example outlet data
    test_outlets = [
        {
            'name': 'Forbes (Editorial Tier 1, No brand mentions)',
            'data': {
                'total_citations': 5,
                'platforms': ['ChatGPT', 'Claude', 'Perplexity'],
                'brand_mentions': 0,
                'recommended_count': 2
            },
            'tier_weight': 10  # Editorial Tier 1
        },
        {
            'name': 'Reddit (Social, Has brand mentions)',
            'data': {
                'total_citations': 8,
                'platforms': ['ChatGPT', 'Claude'],
                'brand_mentions': 3,
                'recommended_count': 0
            },
            'tier_weight': 3  # Social
        },
        {
            'name': 'Wikipedia (Informational, No brand)',
            'data': {
                'total_citations': 10,
                'platforms': ['ChatGPT', 'Claude', 'Perplexity', 'Gemini'],
                'brand_mentions': 0,
                'recommended_count': 1
            },
            'tier_weight': 2  # Informational
        },
        {
            'name': 'Amazon (Ecommerce)',
            'data': {
                'total_citations': 3,
                'platforms': ['Perplexity'],
                'brand_mentions': 1,
                'recommended_count': 0
            },
            'tier_weight': 1  # Ecommerce
        }
    ]
    
    print("Scoring Formula:")
    print("Score = Citations × Tier Weight × Platform Multiplier × Recommendation Bonus × Brand Gap\n")
    
    for outlet in test_outlets:
        score = PROpportunityScorer.calculate_score(
            outlet['data'],
            'TestBrand',
            outlet['tier_weight']
        )
        
        print(f"{outlet['name']}:")
        print(f"  • Citations: {outlet['data']['total_citations']}")
        print(f"  • Platforms: {len(outlet['data']['platforms'])}")
        print(f"  • Tier Weight: {outlet['tier_weight']}")
        print(f"  • Brand Mentions: {outlet['data']['brand_mentions']}")
        print(f"  • Recommended: {outlet['data']['recommended_count']}x")
        print(f"  → PR Opportunity Score: {score}")
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Typeform Auditor Test Suite")
    print("=" * 60)
    
    # Test source classification
    test_source_classification()
    
    # Demonstrate scoring
    demonstrate_scoring()
    
    # Run sample audit if API keys are available
    print("\n" + "=" * 60)
    user_input = input("\nRun a live audit? This will use API credits. (y/n): ")
    if user_input.lower() == 'y':
        run_sample_audit()
    else:
        print("\nSkipping live audit. Set API keys and run again to test the full system.")
    
    print("\n✅ Test complete!")

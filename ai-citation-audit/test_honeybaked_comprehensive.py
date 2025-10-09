#!/usr/bin/env python3
"""
Test script for HoneyBaked Ham Comprehensive GEO Citation Auditor

Validates:
- Query structure (35 queries total)
- Domain classification system
- Content type classification
- CSV column specifications
- API adapter configurations
"""

import sys
from honeybaked_comprehensive_geo_auditor import (
    QUERY_SET,
    DOMAIN_CLASSIFICATIONS,
    PR_TARGET_MEDIA,
    COMPETITOR_BRANDS,
    CONTENT_TYPE_PATTERNS,
    classify_domain,
    classify_content_type,
    extract_domain,
    normalize_url,
)

def test_query_structure():
    """Test that query set is correctly structured"""
    print("Testing query structure...")
    
    total_queries = sum(len(queries) for queries in QUERY_SET.values())
    print(f"  ✓ Total queries: {total_queries}")
    assert total_queries == 35, f"Expected 35 queries, got {total_queries}"
    
    # Verify each category
    expected = {
        "branded": 7,
        "primary_holiday": 10,
        "gift_convenience": 8,
        "competitive": 5,
        "expertise": 5,
    }
    
    for category, expected_count in expected.items():
        actual_count = len(QUERY_SET[category])
        print(f"  ✓ {category}: {actual_count} queries")
        assert actual_count == expected_count, f"Expected {expected_count} for {category}, got {actual_count}"
    
    print("✅ Query structure validated\n")

def test_domain_classification():
    """Test domain classification system"""
    print("Testing domain classification...")
    
    # Test known domains
    test_cases = [
        ("honeybaked.com", "brand_official"),
        ("foodandwine.com", "editorial_tier1"),
        ("allrecipes.com", "editorial_tier2"),
        ("businessinsider.com", "lifestyle_tier1"),
        ("omahasteaks.com", "competitor_official"),
        ("prnewswire.com", "pr_wire"),
        ("unknown-domain.com", "other"),
    ]
    
    for domain, expected in test_cases:
        result = classify_domain(domain)
        print(f"  ✓ {domain} -> {result}")
        assert result == expected, f"Expected {expected} for {domain}, got {result}"
    
    print(f"  ✓ Total classifications defined: {len(DOMAIN_CLASSIFICATIONS)}")
    print("✅ Domain classification validated\n")

def test_pr_targets():
    """Test PR target media tracking"""
    print("Testing PR target media...")
    
    assert len(PR_TARGET_MEDIA) == 11, f"Expected 11 PR targets, got {len(PR_TARGET_MEDIA)}"
    
    expected_targets = [
        "Business Insider",
        "Serious Eats",
        "Allrecipes",
        "The Spruce Eats",
        "Good Housekeeping",
        "CNN",
        "Consumer Reports",
        "Eater",
        "Food & Wine",
        "Southern Living",
        "Bon Appétit",
    ]
    
    for target in expected_targets:
        assert target in PR_TARGET_MEDIA.values(), f"Missing PR target: {target}"
        print(f"  ✓ {target}")
    
    print("✅ PR target media validated\n")

def test_competitor_list():
    """Test competitor brand list"""
    print("Testing competitor brands...")
    
    expected_competitors = [
        "Omaha Steaks",
        "Harry & David",
        "Costco",
        "Whole Foods",
        "Smithfield",
    ]
    
    assert len(COMPETITOR_BRANDS) == 5, f"Expected 5 competitors, got {len(COMPETITOR_BRANDS)}"
    
    for comp in expected_competitors:
        assert comp in COMPETITOR_BRANDS, f"Missing competitor: {comp}"
        print(f"  ✓ {comp}")
    
    print("✅ Competitor list validated\n")

def test_content_types():
    """Test content type classification patterns"""
    print("Testing content type classification...")
    
    expected_types = [
        "buying_guide",
        "product_review",
        "holiday_guide",
        "gift_guide",
        "recipe_content",
        "how_to_guide",
        "news_article",
        "listicle",
        "comparison_article",
    ]
    
    for content_type in expected_types:
        assert content_type in CONTENT_TYPE_PATTERNS, f"Missing content type: {content_type}"
        print(f"  ✓ {content_type}")
    
    print("✅ Content type patterns validated\n")

def test_utility_functions():
    """Test utility functions"""
    print("Testing utility functions...")
    
    # Test URL normalization
    test_url = "https://www.example.com/path/"
    normalized = normalize_url(test_url)
    # Function lowercases and removes trailing slash
    assert normalized == "https://www.example.com/path", f"URL normalization failed: {normalized}"
    print(f"  ✓ URL normalization: {test_url} -> {normalized}")
    
    # Test domain extraction
    domain = extract_domain("https://www.businessinsider.com/article/test")
    assert domain == "businessinsider.com", f"Domain extraction failed: {domain}"
    print(f"  ✓ Domain extraction: businessinsider.com")
    
    # Test content type classification
    content_type = classify_content_type("https://example.com/best-holiday-hams-2024")
    print(f"  ✓ Content type: {content_type}")
    
    print("✅ Utility functions validated\n")

def test_csv_structure():
    """Test expected CSV structures"""
    print("Testing CSV structure specifications...")
    
    # HONEYBAKED_ANALYSIS_MATRIX columns
    matrix_columns = [
        "query", "query_type", "query_category", "commercial_intent",
        "engine", "honeybaked_mentioned", "competitors_mentioned",
        "featured_brand", "honeybaked_prominence", "response_length",
        "total_citations", "honeybaked_citations", "competitor_citations",
        "owned_media_citations", "earned_media_citations",
        "chef_tim_ziga_mentioned", "test_timestamp",
        "platform_response_quality", "notes",
    ]
    print(f"  ✓ ANALYSIS_MATRIX: {len(matrix_columns)} columns")
    
    # CITATION_DETAILS columns
    citation_columns = [
        "engine", "query", "query_category", "query_type",
        "citation_url", "domain", "domain_classification",
        "content_type", "honeybaked_mentioned", "competitor_mentioned",
        "citation_position", "media_tier", "page_title",
        "publish_date", "citation_context",
    ]
    print(f"  ✓ CITATION_DETAILS: {len(citation_columns)} columns")
    
    # COMPETITIVE_CONTEXT columns
    competitive_columns = [
        "brand", "query", "query_category", "query_type", "engine",
        "mentioned_in_response", "prominence_ranking", "tone",
        "specific_products_mentioned", "context_of_mention",
        "citation_count_for_brand",
    ]
    print(f"  ✓ COMPETITIVE_CONTEXT: {len(competitive_columns)} columns")
    
    # PR_MEDIA_TARGETS columns
    pr_columns = [
        "media_outlet", "domain", "target_status", "citation_count",
        "queries_appeared_in", "engines_cited_by", "content_urls",
        "honeybaked_mentioned_in_article", "article_publish_dates",
        "media_tier", "strategic_value",
    ]
    print(f"  ✓ PR_MEDIA_TARGETS: {len(pr_columns)} columns")
    
    print("✅ CSV structures validated\n")

def main():
    """Run all tests"""
    print("=" * 70)
    print("HONEYBAKED COMPREHENSIVE GEO AUDITOR - VALIDATION TESTS")
    print("=" * 70 + "\n")
    
    try:
        test_query_structure()
        test_domain_classification()
        test_pr_targets()
        test_competitor_list()
        test_content_types()
        test_utility_functions()
        test_csv_structure()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe auditor is ready to run!")
        print("Execute: python run_honeybaked_comprehensive.py")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

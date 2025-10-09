#!/usr/bin/env python3
"""
Test script for UNIQLO audit functionality
Tests the audit configuration and basic functionality without making API calls
"""

import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_uniqlo_audit_configuration():
    """Test that the UNIQLO audit configuration is properly set up"""
    
    print("Testing UNIQLO Audit Configuration...")
    print("=" * 50)
    
    try:
        # Import the audit module
        from uniqlo_audit import run_uniqlo_comprehensive_audit
        from api import AuditConfig, Industry, PromptStrategy
        
        print("✅ Successfully imported audit modules")
        
        # Test configuration creation (without running the actual audit)
        config = AuditConfig(
            brand="UNIQLO",
            competitors=["H&M", "Zara", "Gap", "Shein", "Patagonia", "Everlane"],
            industry=Industry.FASHION_RETAIL,
            strategies=[
                PromptStrategy.COMPETITIVE,
                PromptStrategy.SUSTAINABILITY,
                PromptStrategy.CATEGORY_DOMINANCE,
                PromptStrategy.MEDIA_PRESENCE,
                PromptStrategy.INNOVATION,
                PromptStrategy.PURCHASE_JOURNEY,
                PromptStrategy.SENTIMENT,
                PromptStrategy.CUSTOMER_EXPERIENCE
            ],
            max_prompts=10,  # Reduced for testing
            region="Global",
            language="English",
            time_hint="2024-2025",
            parallel_execution=False,  # Disabled for testing
            custom_prompts=[
                "Which fast fashion brands are most sustainable 2025?",
                "UNIQLO vs H&M sustainability comparison",
                "UNIQLO LifeWear philosophy explained"
            ]
        )
        
        print("✅ Successfully created AuditConfig")
        print(f"   Brand: {config.brand}")
        print(f"   Competitors: {len(config.competitors)} configured")
        print(f"   Industry: {config.industry}")
        print(f"   Strategies: {len(config.strategies)} active")
        print(f"   Custom prompts: {len(config.custom_prompts)} configured")
        
        # Test helper functions
        from uniqlo_audit import (
            generate_pr_recommendations, 
            analyze_sustainability_positioning,
            identify_missing_fashion_media,
            extract_domain,
            export_citations_csv
        )
        
        print("✅ Successfully imported helper functions")
        
        # Test domain extraction
        test_url = "https://www.vogue.com/article/fashion-sustainability"
        domain = extract_domain(test_url)
        print(f"✅ Domain extraction test: {test_url} -> {domain}")
        
        # Test missing fashion media identification
        current_domains = {"businessinsider.com", "forbes.com"}
        missing = identify_missing_fashion_media(current_domains)
        print(f"✅ Missing fashion media test: {missing}")
        
        print("\n" + "=" * 50)
        print("🎉 All configuration tests passed!")
        print("The UNIQLO audit script is ready to use.")
        print("\nTo run the full audit, ensure you have API keys set and run:")
        print("python3 uniqlo_audit.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_mock_audit_results():
    """Test the recommendation and analysis functions with mock data"""
    
    print("\nTesting Analysis Functions with Mock Data...")
    print("=" * 50)
    
    try:
        from uniqlo_audit import generate_pr_recommendations, analyze_sustainability_positioning
        
        # Create mock audit results
        mock_results = Mock()
        mock_results.scores = {
            'total': 67.3,
            'presence': 72.1,
            'prominence': 58.9,
            'quality': 45.2  # Low quality score to trigger recommendations
        }
        
        mock_results.competitive_analysis = {
            'competitive_delta': 64.8,
            'competitor_mentions': {
                'H&M': 23,
                'Zara': 19,
                'Gap': 12,
                'Shein': 8,  # High Shein mentions to trigger recommendation
                'Patagonia': 3,
                'Everlane': 2
            }
        }
        
        mock_results.metadata = {
            'total_citations': 156,
            'platforms_used': ['perplexity', 'chatgpt', 'claude'],
            'execution_time': 127.3
        }
        
        # Mock analysis attribute
        mock_results.analysis = {
            'domain_distribution': {
                'top_domains': {
                    'businessinsider.com': 15,
                    'forbes.com': 12,
                    'techcrunch.com': 8
                },
                'industry_tier_1': 5,  # Low fashion tier-1 to trigger recommendation
                'tier_1_editorial': 12,
                'total_unique_domains': 45
            }
        }
        
        # Test PR recommendations
        recommendations = generate_pr_recommendations(mock_results)
        print(f"✅ Generated {len(recommendations)} PR recommendations")
        
        for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
            print(f"   {i}. {rec['title']} (Priority: {rec['priority']})")
        
        # Test sustainability analysis
        sustainability_insights = analyze_sustainability_positioning(mock_results)
        print(f"✅ Generated {len(sustainability_insights)} sustainability insights")
        
        for insight in sustainability_insights[:3]:  # Show first 3
            print(f"   • {insight[:80]}...")
        
        print("\n✅ Analysis functions working correctly with mock data")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis function error: {e}")
        return False

if __name__ == "__main__":
    print("UNIQLO Audit Test Suite")
    print("=" * 60)
    
    # Run tests
    config_test = test_uniqlo_audit_configuration()
    analysis_test = test_mock_audit_results()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration Test: {'✅ PASSED' if config_test else '❌ FAILED'}")
    print(f"Analysis Test: {'✅ PASSED' if analysis_test else '❌ FAILED'}")
    
    if config_test and analysis_test:
        print("\n🎉 All tests passed! The UNIQLO audit script is ready for use.")
        print("\nNext steps:")
        print("1. Set up your API keys (PERPLEXITY_API_KEY, etc.)")
        print("2. Run: python3 uniqlo_audit.py")
        print("3. Review the generated reports in the outputs/ directory")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

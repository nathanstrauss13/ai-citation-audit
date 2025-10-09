#!/usr/bin/env python3
"""
Test script for HoneyBaked Ham V2 Audit
Validates setup and runs a single test query
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_keys():
    """Verify all required API keys are present"""
    print("\n" + "="*80)
    print("STEP 1: Verifying API Keys")
    print("="*80 + "\n")
    
    required_keys = {
        'OPENAI_API_KEY': 'ChatGPT',
        'ANTHROPIC_API_KEY': 'Claude',
        'PERPLEXITY_API_KEY': 'Perplexity',
        'GOOGLE_API_KEY': 'Gemini'
    }
    
    all_present = True
    for key, platform in required_keys.items():
        value = os.getenv(key)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✓ {platform:12} ({key}): {masked_value}")
        else:
            print(f"✗ {platform:12} ({key}): MISSING")
            all_present = False
    
    if not all_present:
        print("\n❌ ERROR: Missing API keys. Please set them in your .env file.")
        return False
    
    print("\n✅ All API keys present!")
    return True


def test_platform_connections():
    """Test connectivity to each platform"""
    print("\n" + "="*80)
    print("STEP 2: Testing Platform Connections")
    print("="*80 + "\n")
    
    from platforms.chatgpt import ChatGPTPlatform
    from platforms.claude import ClaudePlatform
    from platforms.perplexity import PerplexityPlatform
    from platforms.gemini import GeminiPlatform
    
    platforms = {
        'ChatGPT': ChatGPTPlatform(),
        'Claude': ClaudePlatform(),
        'Perplexity': PerplexityPlatform(),
        'Gemini': GeminiPlatform()
    }
    
    test_query = "What is 2+2?"
    
    for name, platform in platforms.items():
        print(f"Testing {name}...", end=" ")
        try:
            citations = platform.get_citations(test_query)
            print(f"✓ Connected (returned {len(citations)} citations)")
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    print("\n✅ All platforms connected successfully!")
    return True


def test_single_query():
    """Run a single test query through the audit system"""
    print("\n" + "="*80)
    print("STEP 3: Running Single Query Test")
    print("="*80 + "\n")
    
    from honeybaked_ham_v2_audit import HoneyBakedAuditor
    
    print("Creating auditor...")
    auditor = HoneyBakedAuditor()
    
    # Test with one query on ChatGPT only
    test_query_info = {
        "text": "What is the best ham for Thanksgiving dinner?",
        "type": "brand_agnostic",
        "category": "holiday_ham"
    }
    
    print(f"\nQuery: \"{test_query_info['text']}\"")
    print(f"Type: {test_query_info['type']}")
    print(f"Testing on: ChatGPT\n")
    
    try:
        # Get response
        result = auditor._query_platform(
            auditor.platforms['chatgpt'],
            'chatgpt',
            test_query_info['text']
        )
        
        if not result:
            print("✗ No result returned")
            return False
        
        print(f"✓ Response received: {len(result['response_text'])} characters")
        print(f"✓ Citations found: {len(result['citations'])}")
        
        # Analyze response
        analysis = auditor._analyze_response(
            result['response_text'],
            result['citations'],
            test_query_info['text'],
            test_query_info['type'],
            'chatgpt'
        )
        
        print(f"\n--- Analysis Results ---")
        print(f"Brand mentioned in response: {analysis['query_matrix_row']['brand_mentioned_in_response']}")
        print(f"Total citations: {analysis['query_matrix_row']['total_citations']}")
        print(f"Citations mentioning brand: {analysis['query_matrix_row']['citations_mentioning_brand']}")
        print(f"Response prominence: {analysis['query_matrix_row']['response_prominence']}")
        print(f"Chef Tim mentioned: {analysis['query_matrix_row']['chef_tim_mentioned']}")
        
        if len(analysis['citation_details']) > 0:
            print(f"\n--- Sample Citation ---")
            citation = analysis['citation_details'][0]
            print(f"URL: {citation['citation_url']}")
            print(f"Domain: {citation['domain']}")
            print(f"Classification: {citation['domain_classification']}")
            print(f"HoneyBaked in source: {citation['honeybaked_mentioned_in_source']}")
        
        if len(analysis['competitive_mentions']) > 0:
            print(f"\n--- Competitors Mentioned ---")
            for comp in analysis['competitive_mentions'][:5]:  # Show first 5
                print(f"  • {comp['competitor_mentioned']}: {comp['mentioned_in_response']}")
        
        print("\n✅ Single query test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("HoneyBaked Ham V2 Audit - System Test")
    print("="*80)
    
    # Step 1: Check API keys
    if not test_api_keys():
        sys.exit(1)
    
    # Step 2: Test platform connections
    if not test_platform_connections():
        sys.exit(1)
    
    # Step 3: Run single query test
    if not test_single_query():
        sys.exit(1)
    
    # All tests passed
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    print("Your system is ready to run the full audit.")
    print("Execute: python run_honeybaked_v2_audit.py")
    print("")


if __name__ == "__main__":
    main()

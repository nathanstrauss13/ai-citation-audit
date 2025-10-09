#!/usr/bin/env python3
"""
Test all 4 LLM platforms individually to debug citation extraction
"""

from load_env import load_env
import logging

# Load environment variables
load_env()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_platform(platform_name, platform_class):
    """Test a single platform"""
    print(f"\n{'='*50}")
    print(f"TESTING {platform_name.upper()}")
    print(f"{'='*50}")
    
    try:
        # Initialize platform
        platform = platform_class()
        print(f"✅ {platform_name} initialized successfully")
        
        # Test with a simple prompt
        test_prompt = "UNIQLO vs H&M sustainability comparison"
        print(f"📝 Testing prompt: {test_prompt}")
        
        # Get citations
        citations = platform.get_citations(test_prompt)
        print(f"📊 Result: {len(citations)} citations extracted")
        
        # Show first few citations
        for i, citation in enumerate(citations[:3]):
            print(f"   {i+1}. {citation.get('url', 'No URL')} ({citation.get('type', 'unknown')})")
        
        if len(citations) > 3:
            print(f"   ... and {len(citations) - 3} more citations")
            
        return len(citations)
        
    except Exception as e:
        print(f"❌ {platform_name} failed: {e}")
        return 0

def main():
    """Test all platforms"""
    print("🚀 TESTING ALL 4 LLM PLATFORMS")
    print("This will help debug citation extraction issues")
    
    results = {}
    
    # Test Perplexity
    try:
        from platforms.perplexity import PerplexityPlatform
        results['perplexity'] = test_platform('Perplexity', PerplexityPlatform)
    except Exception as e:
        print(f"❌ Perplexity import failed: {e}")
        results['perplexity'] = 0
    
    # Test ChatGPT
    try:
        from platforms.chatgpt import ChatGPTPlatform
        results['chatgpt'] = test_platform('ChatGPT', ChatGPTPlatform)
    except Exception as e:
        print(f"❌ ChatGPT import failed: {e}")
        results['chatgpt'] = 0
    
    # Test Claude
    try:
        from platforms.claude import ClaudePlatform
        results['claude'] = test_platform('Claude', ClaudePlatform)
    except Exception as e:
        print(f"❌ Claude import failed: {e}")
        results['claude'] = 0
    
    # Test Gemini
    try:
        from platforms.gemini import GeminiPlatform
        results['gemini'] = test_platform('Gemini', GeminiPlatform)
    except Exception as e:
        print(f"❌ Gemini import failed: {e}")
        results['gemini'] = 0
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY RESULTS")
    print(f"{'='*50}")
    
    total_citations = 0
    working_platforms = 0
    
    for platform, count in results.items():
        status = "✅ WORKING" if count > 0 else "❌ FAILED"
        print(f"{platform.capitalize()}: {count} citations - {status}")
        total_citations += count
        if count > 0:
            working_platforms += 1
    
    print(f"\n🎯 TOTAL: {total_citations} citations from {working_platforms}/4 platforms")
    
    if working_platforms == 4:
        print("🎉 ALL PLATFORMS WORKING! Ready for full audit.")
    elif working_platforms > 0:
        print(f"⚠️  {4 - working_platforms} platforms need debugging.")
    else:
        print("🚨 NO PLATFORMS WORKING! Check API keys and configurations.")

if __name__ == "__main__":
    main()

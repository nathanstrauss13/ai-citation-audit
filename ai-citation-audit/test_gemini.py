#!/usr/bin/env python3
"""Test Gemini integration"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gemini():
    """Test Gemini platform"""
    print("Testing Gemini Integration...")
    print("-" * 50)
    
    # Check API key
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize platform
        print("\nInitializing Gemini platform...")
        from platforms.gemini import GeminiPlatform
        platform = GeminiPlatform()
        print("✅ Platform initialized")
        
        # Test connection
        print("\nTesting connection...")
        if platform.test_connection():
            print("✅ Connection successful")
        else:
            print("❌ Connection test failed")
            return
        
        # Test citation extraction
        print("\nTesting citation extraction...")
        test_prompt = "Tell me about HoneyBaked Ham. Respond in English."
        citations = platform.get_citations(test_prompt)
        
        print(f"\n✅ Extracted {len(citations)} citations:")
        for i, citation in enumerate(citations, 1):
            print(f"  {i}. {citation['url']} (type: {citation['type']})")
        
        print("\n✅ Gemini integration test complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini()

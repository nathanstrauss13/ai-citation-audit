#!/usr/bin/env python3
"""List available Gemini models"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_models():
    """List available Gemini models"""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        
        print("\nListing available models...")
        print("-" * 50)
        
        models = genai.list_models()
        for model in models:
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supported Methods: {model.supported_generation_methods}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_models()

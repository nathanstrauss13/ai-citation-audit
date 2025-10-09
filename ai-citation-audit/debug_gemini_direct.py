#!/usr/bin/env python3
"""Debug Gemini API routing with direct REST calls"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_direct_gemini_api():
    """Test Gemini API with direct REST calls to bypass library routing"""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test different endpoints and models
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest', 
        'gemini-1.5-pro',
        'gemini-pro-latest',
        'gemini-2.5-flash'
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        print("-" * 50)
        
        # Direct REST API call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hello, please respond with 'OK' and include a source URL if possible."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        }
        
        try:
            # Make the request with API key as query parameter
            response = requests.post(
                f"{url}?key={api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCCESS! Response: {text[:100]}...")
                    print(f"✅ Model {model} is working!")
                    return model  # Return the working model
                else:
                    print(f"❌ No candidates in response: {result}")
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Error {response.status_code}: {error_data}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n❌ No models worked with direct API calls")
    return None

def test_model_listing():
    """Test model listing with direct API"""
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    print("\n🔍 Testing model listing with direct API...")
    print("-" * 50)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            models = result.get('models', [])
            print(f"✅ Found {len(models)} models")
            
            # Show first few models that support generateContent
            generate_models = [
                m for m in models 
                if 'generateContent' in m.get('supportedGenerationMethods', [])
            ][:5]
            
            print("\n📋 First 5 models supporting generateContent:")
            for model in generate_models:
                name = model['name']
                display_name = model.get('displayName', 'N/A')
                print(f"  - {name} ({display_name})")
            
            return generate_models
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return []

if __name__ == "__main__":
    print("🔧 GEMINI API ROUTING DEBUG")
    print("=" * 60)
    
    # First test model listing
    models = test_model_listing()
    
    # Then test direct API calls
    working_model = test_direct_gemini_api()
    
    if working_model:
        print(f"\n🎉 SUCCESS: Model '{working_model}' works with direct API!")
        print("✅ This confirms the API key is valid for Google AI Studio")
        print("❌ The issue is with the google-generativeai library routing")
    else:
        print("\n❌ FAILURE: No models work with direct API")
        print("🔍 This suggests an API key or account configuration issue")

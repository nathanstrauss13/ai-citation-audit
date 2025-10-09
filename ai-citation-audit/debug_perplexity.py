#!/usr/bin/env python3
"""
Debug Perplexity API integration and find correct model names
"""

import os
import requests
import json
from load_env import load_env

# Load environment
load_env()

def test_perplexity_models():
    """Test different Perplexity model names to find working ones"""
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found")
        return
    
    print("🔍 PERPLEXITY MODEL DEBUGGING")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...{api_key[-5:]} ({len(api_key)} chars)")
    print()
    
    # Test different model names based on Perplexity docs
    test_models = [
        # Current models (2024)
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online", 
        "llama-3.1-sonar-huge-128k-online",
        
        # Alternative naming patterns
        "sonar-small-online",
        "sonar-medium-online", 
        "sonar-large-online",
        
        # Offline models
        "llama-3.1-sonar-small-128k-chat",
        "llama-3.1-sonar-large-128k-chat",
        
        # Legacy models
        "sonar-small-chat",
        "sonar-medium-chat",
        "mixtral-8x7b-instruct",
        "codellama-34b-instruct",
        
        # Newer models (if available)
        "llama-3.1-8b-instruct",
        "llama-3.1-70b-instruct",
    ]
    
    base_url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    working_models = []
    failed_models = []
    
    for model in test_models:
        print(f"Testing: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, respond with 'OK'"
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS: {model}")
                working_models.append(model)
                
                # Show response structure
                data = response.json()
                if 'choices' in data and data['choices']:
                    content = data['choices'][0].get('message', {}).get('content', '')
                    print(f"     Response: {content[:50]}")
                
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"  ❌ FAILED: {model}")
                print(f"     Error: {error_msg[:100]}")
                failed_models.append((model, error_msg))
                
        except Exception as e:
            print(f"  ❌ EXCEPTION: {model}")
            print(f"     Error: {str(e)[:100]}")
            failed_models.append((model, str(e)))
        
        print()
    
    # Summary
    print("=" * 50)
    print("SUMMARY RESULTS")
    print("=" * 50)
    
    if working_models:
        print(f"✅ WORKING MODELS ({len(working_models)}):")
        for model in working_models:
            print(f"   • {model}")
        
        print(f"\n🎯 RECOMMENDED MODEL: {working_models[0]}")
        
    else:
        print("❌ NO WORKING MODELS FOUND")
    
    if failed_models:
        print(f"\n❌ FAILED MODELS ({len(failed_models)}):")
        for model, error in failed_models[:5]:  # Show first 5
            print(f"   • {model}: {error[:50]}")
    
    return working_models

def get_perplexity_model_list():
    """Try to get official model list from Perplexity API"""
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        return None
    
    print("\n🔍 TRYING TO GET OFFICIAL MODEL LIST")
    print("-" * 40)
    
    # Try different endpoints that might list models
    endpoints = [
        "https://api.perplexity.ai/models",
        "https://api.perplexity.ai/v1/models", 
        "https://api.perplexity.ai/chat/models"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        try:
            print(f"Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Found model list")
                print(json.dumps(data, indent=2)[:500])
                return data
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("No official model list endpoint found")
    return None

def fix_perplexity_platform(working_model):
    """Update the Perplexity platform with working model"""
    
    if not working_model:
        print("❌ No working model to update")
        return
    
    print(f"\n🔧 UPDATING PERPLEXITY PLATFORM")
    print(f"New model: {working_model}")
    
    # Read current file
    platform_file = "platforms/perplexity.py"
    with open(platform_file, 'r') as f:
        content = f.read()
    
    # Find current model line and replace
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'self.model = ' in line and 'llama' in line:
            old_model = line.strip()
            lines[i] = f'        self.model = "{working_model}"'
            print(f"Replaced: {old_model}")
            print(f"With:     {lines[i]}")
            break
    
    # Write updated file
    with open(platform_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Perplexity platform updated!")

def main():
    """Main debug function"""
    
    print("🚀 PERPLEXITY COMPREHENSIVE DEBUG")
    print("This will find the correct model name and fix the platform")
    print()
    
    # Test models
    working_models = test_perplexity_models()
    
    # Try to get official list
    get_perplexity_model_list()
    
    # Fix platform if we found working models
    if working_models:
        fix_perplexity_platform(working_models[0])
        
        print("\n🎉 PERPLEXITY DEBUG COMPLETE!")
        print("✅ Platform updated with working model")
        print("🔄 Re-run your audit to test the fix")
    else:
        print("\n❌ PERPLEXITY DEBUG FAILED")
        print("No working models found - check API key or Perplexity service status")

if __name__ == "__main__":
    main()

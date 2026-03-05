#!/usr/bin/env python3
"""
Environment loader for AI Citation Audit system.
Loads API keys from .env file for secure credential management.
"""

import os
from pathlib import Path

def load_env(override: bool = False):
    """Load environment variables from .env file.
    If override is False (default), existing os.environ values are preserved and .env values only fill missing keys.
    If override is True, .env values overwrite existing environment variables.
    """
    env_path = Path('.env')
    if not env_path.exists():
        print("Warning: .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                k = key.strip()
                v = value.strip()
                if override or not os.environ.get(k):
                    os.environ[k] = v
    
    return True

def check_api_keys():
    """Check which API keys are configured"""
    keys = {
        'PERPLEXITY_API_KEY': 'Perplexity (Primary)',
        'OPENAI_API_KEY': 'OpenAI ChatGPT',
        'ANTHROPIC_API_KEY': 'Anthropic Claude',
        'GEMINI_API_KEY': 'Google Gemini',
        'XAI_API_KEY': 'xAI Grok',
        'DEEPSEEK_API_KEY': 'DeepSeek',
        'TOGETHER_API_KEY': 'Together.ai (Llama provider)',
        'LLAMA_API_KEY': 'Generic Llama endpoint',
        'BRAVE_API_KEY': 'Brave Search',
        'SERPAPI_API_KEY': 'SerpAPI (Google SGE)',
        'FLASK_SECRET_KEY': 'Flask Web App'
    }
    
    print("API Key Status:")
    print("-" * 40)
    
    for key, description in keys.items():
        status = "✅ SET" if os.environ.get(key) else "❌ NOT SET"
        print(f"{description:<20} {status}")
    
    print("-" * 40)
    
    # Count active engines
    active_engines = []
    if os.environ.get('PERPLEXITY_API_KEY'):
        active_engines.append('Perplexity')
    if os.environ.get('OPENAI_API_KEY'):
        active_engines.append('ChatGPT')
    if os.environ.get('ANTHROPIC_API_KEY'):
        active_engines.append('Claude')
    if os.environ.get('GEMINI_API_KEY'):
        active_engines.append('Gemini')
    if os.environ.get('XAI_API_KEY'):
        active_engines.append('Grok')
    if os.environ.get('DEEPSEEK_API_KEY'):
        active_engines.append('DeepSeek')
    if os.environ.get('TOGETHER_API_KEY') or os.environ.get('LLAMA_API_KEY'):
        active_engines.append('Meta (Llama)')
    if os.environ.get('BRAVE_API_KEY'):
        active_engines.append('Brave')
    if os.environ.get('SERPAPI_API_KEY'):
        active_engines.append('Google SGE')
    
    print(f"Active Engines: {', '.join(active_engines) if active_engines else 'None'}")
    print(f"Total: {len(active_engines)} engines configured")
    
    return len(active_engines) > 0

if __name__ == "__main__":
    if load_env():
        print("Environment loaded successfully!")
        check_api_keys()
    else:
        print("Failed to load environment")

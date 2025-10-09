#!/usr/bin/env python3
"""Auto-generated fixes for multi-platform citation extraction"""

import os
import fileinput
import sys

def fix_platform_models():
    """Fix model names in platform files"""
    
    fixes = {
        'platforms/perplexity.py': [
            ('sonar-small-chat', 'llama-3.1-sonar-large-128k-online'),
            ('sonar-small', 'llama-3.1-sonar-large-128k-online'),
        ],
        'platforms/claude.py': [
            ('claude-3-sonnet-20240229', 'claude-3-5-sonnet-20241022'),
            ('claude-2', 'claude-3-5-sonnet-20241022'),
        ]
    }
    
    for filepath, replacements in fixes.items():
        if os.path.exists(filepath):
            print(f"Fixing {filepath}...")
            with fileinput.FileInput(filepath, inplace=True) as file:
                for line in file:
                    for old, new in replacements:
                        line = line.replace(old, new)
                    sys.stdout.write(line)

def add_platform_field():
    """Ensure platform field is added to all citations"""
    
    template = """
    # Add to each platform's extract_citations method:
    for citation in citations:
        citation['platform'] = '{platform_name}'
    """
    print("Add platform field to citations in each platform adapter")
    print(template)

if __name__ == "__main__":
    fix_platform_models()
    add_platform_field()
    print("Fixes applied! Re-run your audit to test.")

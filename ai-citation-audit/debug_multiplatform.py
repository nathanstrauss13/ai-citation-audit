#!/usr/bin/env python3
"""
Debug script to fix multi-platform citation extraction
Problem: Only Gemini contributing to final results (ChatGPT, Claude, Perplexity showing 0)
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from load_env import load_env
load_env()

def debug_citation_pipeline():
    """Comprehensive debugging of the citation extraction pipeline"""
    
    print("=" * 70)
    print("MULTI-PLATFORM CITATION EXTRACTION DEBUGGING")
    print("=" * 70)
    print()
    
    # Track all findings
    debug_report = {
        'platform_status': {},
        'test_results': {},
        'aggregation_issues': [],
        'fixes_needed': []
    }
    
    # ========================================================================
    # STEP 1: CHECK PLATFORM CONFIGURATIONS
    # ========================================================================
    print("STEP 1: PLATFORM CONFIGURATION CHECK")
    print("-" * 50)
    
    platforms_config = {
        'perplexity': {
            'api_key_env': 'PERPLEXITY_API_KEY',
            'correct_model': 'llama-3.1-sonar-large-128k-online',
            'old_model': 'sonar-small-chat'  # Check if old model still exists
        },
        'chatgpt': {
            'api_key_env': 'OPENAI_API_KEY',
            'correct_model': 'gpt-4o-mini',
            'alternatives': ['gpt-4', 'gpt-3.5-turbo']
        },
        'claude': {
            'api_key_env': 'ANTHROPIC_API_KEY',
            'correct_model': 'claude-3-5-sonnet-20241022',
            'old_model': 'claude-3-sonnet-20240229'  # Check for old model
        },
        'gemini': {
            'api_key_env': 'GOOGLE_API_KEY',
            'correct_model': 'gemini-2.5-flash',
            'alternatives': ['gemini-1.5-flash', 'gemini-1.5-pro']
        }
    }
    
    for platform, config in platforms_config.items():
        api_key = os.environ.get(config['api_key_env'])
        status = {
            'has_api_key': bool(api_key),
            'api_key_length': len(api_key) if api_key else 0
        }
        
        if api_key:
            print(f"✓ {platform:12} API key present ({len(api_key)} chars)")
        else:
            print(f"✗ {platform:12} No API key found")
            debug_report['fixes_needed'].append(f"Set {config['api_key_env']} environment variable")
        
        debug_report['platform_status'][platform] = status
    
    # ========================================================================
    # STEP 2: CHECK PLATFORM FILES AND MODEL NAMES
    # ========================================================================
    print("\nSTEP 2: PLATFORM FILE AND MODEL CHECK")
    print("-" * 50)
    
    # Check if platform files exist and contain correct model names
    platform_files = {
        'perplexity': 'platforms/perplexity.py',
        'chatgpt': 'platforms/chatgpt.py',
        'claude': 'platforms/claude.py',
        'gemini': 'platforms/gemini.py'
    }
    
    for platform, filepath in platform_files.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Check for correct model name
            correct_model = platforms_config[platform]['correct_model']
            if correct_model in content:
                print(f"✓ {platform:12} Using correct model: {correct_model}")
            else:
                print(f"✗ {platform:12} Model mismatch - not finding: {correct_model}")
                
                # Check for old model
                if 'old_model' in platforms_config[platform]:
                    old_model = platforms_config[platform]['old_model']
                    if old_model in content:
                        print(f"  WARNING: Found old model '{old_model}' - needs update!")
                        debug_report['fixes_needed'].append(
                            f"Update {filepath}: Replace '{old_model}' with '{correct_model}'"
                        )
                
            # Check for citation extraction method
            if 'def extract_citations' in content or 'def get_citations' in content:
                print(f"  ✓ Citation extraction method found")
            else:
                print(f"  ✗ No citation extraction method found")
                debug_report['fixes_needed'].append(f"Add extract_citations method to {filepath}")
        else:
            print(f"✗ {platform:12} File not found: {filepath}")
            debug_report['fixes_needed'].append(f"Create {filepath}")
    
    # ========================================================================
    # STEP 3: TEST INDIVIDUAL PLATFORM CITATION EXTRACTION
    # ========================================================================
    print("\nSTEP 3: INDIVIDUAL PLATFORM TESTING")
    print("-" * 50)
    
    test_prompt = "Tell me about UNIQLO sustainability practices"
    
    try:
        from api import CitationAuditAPI, AuditConfig, Industry, PromptStrategy
        
        # Test each platform individually
        for platform_name in ['perplexity', 'chatgpt', 'claude', 'gemini']:
            print(f"\nTesting {platform_name}...")
            
            try:
                # Create minimal config for single platform
                test_config = AuditConfig(
                    brand="UNIQLO",
                    competitors=[],
                    industry=Industry.FASHION_RETAIL,
                    strategies=[PromptStrategy.BASELINE],
                    max_prompts=1,
                    engines=[platform_name],  # Test only this platform
                    custom_prompts=[test_prompt]
                )
                
                api = CitationAuditAPI()
                
                # Mock run to test platform
                # We'll check if platform can be initialized
                if hasattr(api, '_initialize_platforms'):
                    platforms = api._initialize_platforms()
                    if platform_name in platforms:
                        print(f"  ✓ Platform initialized successfully")
                    else:
                        print(f"  ✗ Platform failed to initialize")
                        debug_report['test_results'][platform_name] = 'initialization_failed'
                        
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:100]}")
                debug_report['test_results'][platform_name] = f'error: {str(e)[:50]}'
                
    except ImportError as e:
        print(f"Cannot import API modules: {e}")
        debug_report['fixes_needed'].append("Ensure api.py and platform modules are properly installed")
    
    # ========================================================================
    # STEP 4: CHECK CITATION AGGREGATION LOGIC
    # ========================================================================
    print("\nSTEP 4: CITATION AGGREGATION ANALYSIS")
    print("-" * 50)
    
    # Look for common aggregation issues
    aggregation_checks = [
        {
            'file': 'api.py',
            'patterns': [
                "if platform == 'gemini'",  # Filtering only Gemini?
                "if citation['platform'] == 'gemini'",  # Only keeping Gemini citations?
                "citations = []",  # Resetting citations array?
                "citations.clear()",  # Clearing citations?
            ]
        },
        {
            'file': 'run_audit.py',
            'patterns': [
                "platform_citations = []",  # Not extending main list?
                "return gemini_citations",  # Only returning Gemini?
            ]
        }
    ]
    
    for check in aggregation_checks:
        if os.path.exists(check['file']):
            with open(check['file'], 'r') as f:
                content = f.read()
                
            print(f"\nChecking {check['file']}:")
            for pattern in check['patterns']:
                if pattern in content:
                    print(f"  ⚠️  Found potential issue: '{pattern}'")
                    debug_report['aggregation_issues'].append(f"{check['file']}: {pattern}")
    
    # ========================================================================
    # STEP 5: PROVIDE SPECIFIC FIXES
    # ========================================================================
    print("\nSTEP 5: RECOMMENDED FIXES")
    print("-" * 50)
    
    # Add debug logging to trace citation flow
    debug_code = '''
# Add this to your main audit function to trace citations:

def run_audit_with_debug(config):
    all_citations = []
    platform_breakdown = {}
    
    for prompt in config.prompts:
        print(f"\\nProcessing: {prompt[:50]}...")
        
        for platform_name in config.engines:
            platform = initialize_platform(platform_name)
            if not platform:
                print(f"  {platform_name}: SKIPPED (not initialized)")
                continue
                
            # Get response and extract citations
            response = platform.get_response(prompt)
            citations = platform.extract_citations(response)
            
            # CRITICAL: Ensure platform is set on each citation
            for citation in citations:
                citation['platform'] = platform_name
                
            # Track and aggregate
            platform_breakdown[platform_name] = platform_breakdown.get(platform_name, 0) + len(citations)
            all_citations.extend(citations)
            
            print(f"  {platform_name}: {len(citations)} citations (Total: {len(all_citations)})")
    
    # Final verification
    print(f"\\nFINAL RESULTS:")
    print(f"Total citations: {len(all_citations)}")
    for platform, count in platform_breakdown.items():
        print(f"  {platform}: {count} citations")
    
    return all_citations
'''
    
    print("Add this debug code to trace citation flow:")
    print(debug_code)
    
    # ========================================================================
    # STEP 6: GENERATE FIX SCRIPT
    # ========================================================================
    print("\nSTEP 6: AUTOMATED FIX GENERATION")
    print("-" * 50)
    
    # Generate fix script
    fix_script = '''#!/usr/bin/env python3
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
'''
    
    # Save fix script
    fix_script_path = 'fix_multiplatform.py'
    with open(fix_script_path, 'w') as f:
        f.write(fix_script)
    
    print(f"Fix script saved to: {fix_script_path}")
    print("Run: python3 fix_multiplatform.py")
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print("\n" + "=" * 70)
    print("DEBUGGING COMPLETE - SUMMARY")
    print("=" * 70)
    
    if debug_report['fixes_needed']:
        print("\n🔧 FIXES REQUIRED:")
        for i, fix in enumerate(debug_report['fixes_needed'], 1):
            print(f"  {i}. {fix}")
    
    if debug_report['aggregation_issues']:
        print("\n⚠️  AGGREGATION ISSUES FOUND:")
        for issue in debug_report['aggregation_issues']:
            print(f"  - {issue}")
    
    print("\n📋 NEXT STEPS:")
    print("  1. Run: python3 fix_multiplatform.py")
    print("  2. Add debug logging to trace citation flow")
    print("  3. Ensure all platforms have 'platform' field set on citations")
    print("  4. Check that citations aren't filtered by platform")
    print("  5. Re-run audit and verify all platforms contribute")
    
    # Save debug report
    report_path = f'debug_report_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
    with open(report_path, 'w') as f:
        json.dump(debug_report, f, indent=2)
    
    print(f"\nDebug report saved to: {report_path}")
    
    return debug_report

if __name__ == "__main__":
    debug_report = debug_citation_pipeline()
    
    # Return exit code based on issues found
    if debug_report['fixes_needed'] or debug_report['aggregation_issues']:
        sys.exit(1)  # Issues found
    else:
        sys.exit(0)  # All good

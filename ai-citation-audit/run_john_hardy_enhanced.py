#!/usr/bin/env python3
"""
Runner script for John Hardy Enhanced AEO Citation Audit
Following NBA citation-focused best practices
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from john_hardy_enhanced_auditor import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("JOHN HARDY ENHANCED AEO CITATION ANALYSIS")
    print("Following NBA Citation-Focused Best Practices")
    print("="*80 + "\n")
    
    print("This enhanced audit will:")
    print("  • Test 25 queries across 4 AI platforms (100 total tests)")
    print("  • Capture every citation URL with explicit prompting")
    print("  • Track owned vs. earned media patterns")
    print("  • Map Tier-1 luxury media coverage")
    print("  • Analyze competitor content dominance")
    print("  • Measure sustainability narrative ownership")
    print("\nOutput Files:")
    print("  1. JOHN_HARDY_BRAND_ANALYSIS_MATRIX (comprehensive query performance)")
    print("  2. JOHN_HARDY_CITATION_DETAILS (every URL captured)")
    print("  3. JOHN_HARDY_COMPETITIVE_CONTEXT (brand-by-brand comparison)")
    print("  4. JOHN_HARDY_MEDIA_INFLUENCE (media outlet mapping)")
    print("  5. PLATFORM_RELIABILITY_REPORT (execution metrics)")
    print("\nEstimated time: ~2 hours")
    print("\nPress Ctrl+C at any time to stop the audit\n")
    
    input("Press Enter to begin the enhanced audit...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

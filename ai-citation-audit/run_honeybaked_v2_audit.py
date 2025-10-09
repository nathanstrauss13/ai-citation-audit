#!/usr/bin/env python3
"""
Runner script for HoneyBaked Ham V2 Audit
Executes the precision methodology audit across all platforms
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from honeybaked_ham_v2_audit import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("HoneyBaked Ham - Programmatic API Data Collection V2")
    print("Precision Methodology for AI Citation Analysis")
    print("="*80 + "\n")
    
    print("This audit will:")
    print("  • Test 15 queries across 4 AI platforms (60 total tests)")
    print("  • Distinguish brand mentions in responses vs citations")
    print("  • Analyze citation authority and source credibility")
    print("  • Track competitive landscape across platforms")
    print("  • Generate 3 CSV files + 1 JSON summary")
    print("\nEstimated runtime: 10-15 minutes")
    print("\n" + "="*80 + "\n")
    
    input("Press ENTER to start the audit...")
    
    try:
        output_files = main()
        print("\n" + "="*80)
        print("SUCCESS! Audit completed successfully.")
        print("="*80 + "\n")
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        sys.exit(1)

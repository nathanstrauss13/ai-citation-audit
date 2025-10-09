#!/usr/bin/env python3
"""
Runner script for John Hardy Sample AEO Citation Audit
Quick execution of the proof-of-concept analysis
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from john_hardy_sample_audit import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("JOHN HARDY JEWELRY - AEO CITATION ANALYSIS")
    print("Proof-of-Concept: 10 Queries × 4 Engines = 40 Tests")
    print("="*80 + "\n")
    
    print("This proof-of-concept will:")
    print("  • Test 10 strategic queries across 4 AI platforms")
    print("  • Track brand visibility and competitive positioning")
    print("  • Generate 3 CSV files for analysis")
    print("  • Provide summary statistics and insights")
    print("\nEstimated time: ~90 minutes")
    print("\nPress Ctrl+C at any time to stop the audit\n")
    
    input("Press Enter to begin the audit...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

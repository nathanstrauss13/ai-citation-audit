#!/usr/bin/env python3
"""
Runner for NBA Citation-Focused Audit
Executes 30 queries × 4 platforms = 120 tests
PRIMARY OBJECTIVE: Capture citation URLs
"""

import sys
from nba_citation_focused_auditor import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("NBA CITATION-FOCUSED AEO ANALYSIS")
    print("="*80)
    print("\nObjective: Capture citation URLs to identify media outlet patterns")
    print("Scope: 30 queries × 4 platforms = 120 tests")
    print("Output: 4 files (matrix, citations, competitive, report)")
    print("="*80 + "\n")
    
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

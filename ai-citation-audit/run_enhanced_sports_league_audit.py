#!/usr/bin/env python3
"""
Runner script for Enhanced Sports League AEO Analysis
Executes 24 queries + consistency tests across 4 AI platforms
"""

import sys
from enhanced_sports_league_auditor import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ENHANCED SPORTS LEAGUE AEO ANALYSIS")
    print("="*80)
    print("\nFeatures:")
    print("  • Multi-key Gemini load balancing (3 API keys)")
    print("  • Consistency testing (3 runs for critical queries)")
    print("  • Content fetching with sentiment analysis")
    print("  • GPT-4 enhanced citations")
    print("  • 24 queries + 6 competitive baseline")
    print("  • 5 comprehensive output files")
    print("="*80 + "\n")
    
    sys.exit(main())

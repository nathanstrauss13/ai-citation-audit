#!/usr/bin/env python3
"""
Runner script for NBA Fan Engagement AEO Analysis
Executes 18 queries across 4 AI platforms (72 total tests)
"""

import sys
from nba_fan_engagement_auditor import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("NBA FAN ENGAGEMENT AEO ANALYSIS")
    print("Analyzing consumer decision moments: streaming, tickets, fan recruitment")
    print("="*80 + "\n")
    
    sys.exit(main())

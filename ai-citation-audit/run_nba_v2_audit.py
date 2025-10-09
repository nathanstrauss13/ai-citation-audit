#!/usr/bin/env python3
"""
Runner script for NBA Sports League V2 Audit
Executes the precision methodology audit across all platforms
Tests NBA vs. NFL, MLB, NHL across 15 queries
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nba_sports_league_v2_audit import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("NBA vs. Major Sports Leagues - V2 Audit")
    print("Precision Methodology for AI Citation Analysis")
    print("="*80 + "\n")
    
    print("This audit will:")
    print("  • Test 15 queries across 4 AI platforms (60 total tests)")
    print("  • Track NBA, NFL, MLB, NHL mentions in responses vs citations")
    print("  • Analyze competitive positioning across leagues")
    print("  • Calculate revenue-adjusted visibility metrics")
    print("  • Generate 3 CSV files + 1 JSON summary")
    print("\nEstimated runtime: 8-12 minutes")
    print("\n" + "="*80 + "\n")
    
    input("Press ENTER to start the NBA audit...")
    
    try:
        output_files = main()
        print("\n" + "="*80)
        print("SUCCESS! NBA audit completed successfully.")
        print("="*80 + "\n")
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        sys.exit(1)

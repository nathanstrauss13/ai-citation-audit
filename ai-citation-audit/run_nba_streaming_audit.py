#!/usr/bin/env python3
"""
NBA Streaming Options Citation Analysis - Execution Script
Amazon Prime Competitive Intelligence

Runs the complete 40-prompt audit:
- 10 queries (6 service-agnostic + 4 service-specific)  
- 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini)
- 3 CSV outputs + JSON summary

Estimated Time: 2-3 hours for complete data collection
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nba_streaming_auditor import main

if __name__ == '__main__':
    print("\n" + "="*80)
    print("NBA STREAMING OPTIONS CITATION ANALYSIS")
    print("Amazon Prime Competitive Intelligence")
    print("="*80)
    print("\nProtocol:")
    print("  • 10 queries (6 service-agnostic + 4 service-specific)")
    print("  • 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini)")
    print("  • 40 total prompts")
    print("  • Estimated time: 2-3 hours")
    print("\nOutputs:")
    print("  • NBA_STREAMING_QUERY_MATRIX_[timestamp].csv")
    print("  • NBA_STREAMING_RAW_CITATIONS_[timestamp].csv")
    print("  • NBA_STREAMING_MEDIA_TRACKING_[timestamp].csv")
    print("  • NBA_STREAMING_AUDIT_SUMMARY_[timestamp].json")
    print("\n" + "="*80)
    
    confirm = input("\nProceed with full 40-prompt audit? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        print("\nStarting NBA Streaming Audit...\n")
        main()
    else:
        print("\nAudit cancelled.")
        sys.exit(0)

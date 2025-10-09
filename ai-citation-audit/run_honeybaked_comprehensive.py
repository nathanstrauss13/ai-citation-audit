#!/usr/bin/env python3
"""
Execution script for HoneyBaked Ham Comprehensive GEO Citation Analysis

This script runs the complete 35-query audit across 4 AI platforms
and generates all 4 required CSV files as specified in the methodology.

Usage:
    python run_honeybaked_comprehensive.py

Requirements:
    - At least one API key configured (.env file)
    - Internet connection
    - ~30-45 minutes for full execution (140 tests)
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from honeybaked_comprehensive_geo_auditor import main

if __name__ == "__main__":
    try:
        print("\n🚀 Starting HoneyBaked Ham Comprehensive GEO Audit")
        print("This will take approximately 30-45 minutes to complete.\n")
        
        result = main()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Audit completed successfully.")
        print("=" * 70)
        print(f"\nYou can now upload the CSV files to Claude for analysis.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user.")
        print("Partial results may be available in case_studies/honeybaked_ham/comprehensive_geo/")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        print("Please check your API keys and internet connection.")
        sys.exit(1)

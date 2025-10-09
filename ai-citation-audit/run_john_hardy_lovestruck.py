#!/usr/bin/env python3
"""
Runner script for John Hardy Lovestruck Collection Launch Analysis
35 queries focused on product launch visibility and competitive positioning
"""

import sys
from john_hardy_lovestruck_auditor import main

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print("JOHN HARDY LOVESTRUCK COLLECTION - LAUNCH ANALYSIS")
        print("Billie Eilish Partnership | Lab-Grown Diamonds | Sept 29, 2025")
        print("="*80 + "\n")
        
        output_files = main()
        
        print("\n" + "="*80)
        print("✓ LOVESTRUCK LAUNCH ANALYSIS COMPLETE")
        print("="*80)
        print("\nOutput files can be found in:")
        print("  case_studies/john_hardy_lovestruck/")
        print("\nKey Metrics Generated:")
        print("  • Launch awareness rate")
        print("  • Billie Eilish partnership visibility")
        print("  • Lab-grown diamond category entry")
        print("  • Competitive positioning vs Brilliant Earth & Vrai")
        print("  • Media coverage analysis")
        print("="*80 + "\n")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Runner script for John Hardy Supplemental AEO Citation Analysis
15 queries focused on social media and trade publications
"""

import sys
from john_hardy_supplemental_auditor import main

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print("JOHN HARDY SUPPLEMENTAL AUDIT - RUNNER")
        print("15 Queries: Social Media & Trade Publications")
        print("="*80 + "\n")
        
        output_files = main()
        
        print("\n" + "="*80)
        print("✓ SUPPLEMENTAL AUDIT COMPLETE")
        print("="*80)
        print("\nOutput files can be found in:")
        print("  case_studies/john_hardy_supplemental/")
        print("\nTo supplement existing analysis, combine these files with:")
        print("  case_studies/john_hardy_enhanced/")
        print("="*80 + "\n")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)

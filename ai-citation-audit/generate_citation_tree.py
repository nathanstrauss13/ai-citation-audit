#!/usr/bin/env python3
"""
Generate Citation Explorer from CSV data.

Produces an interactive transit-map-style HTML visualization that lets users
drill from queries → platforms → presence → citation types → domains → URLs.

Usage:
    # From existing collection CSV
    python generate_citation_tree.py output/LULULEMON_CITATIONS_20260305.csv "Lululemon"

    # With custom output path
    python generate_citation_tree.py data.csv "Brand" -o explorer.html

    # Force persona/intent columns (auto-detected by default)
    python generate_citation_tree.py data.csv "Brand" --persona
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables (API keys for Claude classification)
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass

from engines.citation_tree_engine import CitationTreeEngine


def load_csv(csv_path: str) -> list:
    """Load CSV and return list of row dicts."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def detect_persona_columns(rows: list) -> bool:
    """Check if CSV has persona and intent columns with actual data."""
    if not rows:
        return False
    fieldnames = rows[0].keys()
    has_cols = 'persona' in fieldnames and 'intent' in fieldnames
    if not has_cols:
        return False
    # Check if at least some rows have non-empty values
    filled = sum(1 for r in rows if r.get('persona', '').strip())
    return filled > len(rows) * 0.1  # At least 10% have data


def main():
    parser = argparse.ArgumentParser(
        description='Generate Citation Explorer from CSV data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate_citation_tree.py output/BRAND_CITATIONS.csv "Brand Name"
  python generate_citation_tree.py data.csv "Lululemon" -o lululemon_explorer.html
  python generate_citation_tree.py data.csv "Lululemon" --persona
        '''
    )
    parser.add_argument('csv_file', help='Path to collection CSV file')
    parser.add_argument('brand_name', help='Brand name for analysis')
    parser.add_argument('-o', '--output', help='Output HTML file path (default: auto-generated)')
    parser.add_argument('-c', '--competitors', default=None,
                        help='Comma-separated competitor brand names (improves classification)')
    parser.add_argument('--persona', action='store_true',
                        help='Force persona/intent hierarchy (auto-detected by default)')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    # Load data
    print(f"Loading CSV: {args.csv_file}")
    rows = load_csv(args.csv_file)
    if not rows:
        print("Error: CSV file is empty or has no data rows")
        sys.exit(1)

    print(f"  Loaded {len(rows)} rows")
    print(f"  Columns: {', '.join(rows[0].keys())}")

    # Detect persona/intent
    has_persona = args.persona or detect_persona_columns(rows)
    if has_persona:
        print("  Persona/Intent columns detected — using full hierarchy")
    else:
        print("  No persona/intent columns — starting at prompt level")

    # Count basic stats
    queries = set(r.get('query', '') for r in rows)
    engines = set(r.get('engine', '') for r in rows)
    def _split_urls(raw):
        """Split URLs supporting both pipe-separated (legacy) and newline-separated."""
        if not raw:
            return []
        if '|' in raw:
            return [u.strip() for u in raw.split('|') if u.strip()]
        return [u.strip() for u in raw.split('\n') if u.strip()]

    total_urls = sum(
        len(_split_urls(r.get('citation_urls', '') or ''))
        for r in rows
    )
    print(f"  Queries: {len(queries)}")
    print(f"  Platforms: {', '.join(sorted(engines))}")
    print(f"  Total citation URLs: {total_urls}")

    # Parse competitors
    competitors = None
    if args.competitors:
        competitors = [c.strip() for c in args.competitors.split(',') if c.strip()]
        print(f"  Competitors: {', '.join(competitors)}")

    # Generate HTML
    print(f"\nGenerating Citation Explorer for {args.brand_name}...")
    engine = CitationTreeEngine()
    html = engine.generate(rows, args.brand_name, has_persona=has_persona,
                           competitors=competitors)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        brand_slug = args.brand_name.upper().replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_dir = Path(args.csv_file).parent
        output_path = str(output_dir / f"{brand_slug}_CITATION_EXPLORER_{timestamp}.html")

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    file_size = os.path.getsize(output_path)
    print(f"\nCitation Explorer generated successfully!")
    print(f"  Output: {output_path}")
    print(f"  Size: {file_size / 1024:.1f} KB")
    print(f"  Open in browser to explore citation paths.")

    return output_path


if __name__ == '__main__':
    main()

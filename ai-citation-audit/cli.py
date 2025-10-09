#!/usr/bin/env python3
"""
AI Citation Audit CLI - Command Line Interface
Provides easy command-line access to the programmatic API
"""

import argparse
import json
import sys
from typing import List
from api import (
    CitationAuditAPI, AuditConfig, Industry, PromptStrategy,
    quick_audit, competitive_audit, media_presence_audit
)

def parse_industry(industry_str: str) -> Industry:
    """Parse industry string to Industry enum"""
    industry_map = {
        'food': Industry.FOOD_BEVERAGE,
        'food_beverage': Industry.FOOD_BEVERAGE,
        'fashion': Industry.FASHION_RETAIL,
        'fashion_retail': Industry.FASHION_RETAIL,
        'robotics': Industry.ROBOTICS,
        'b2b_tech': Industry.B2B_TECH,
        'tech': Industry.B2B_TECH,
        'consumer_goods': Industry.CONSUMER_GOODS,
        'consumer': Industry.CONSUMER_GOODS,
        'automotive': Industry.AUTOMOTIVE,
        'cars': Industry.AUTOMOTIVE,
        'healthcare': Industry.HEALTHCARE,
        'financial': Industry.FINANCIAL_SERVICES,
        'entertainment': Industry.ENTERTAINMENT,
        'travel': Industry.TRAVEL_HOSPITALITY
    }
    
    industry_lower = industry_str.lower()
    if industry_lower in industry_map:
        return industry_map[industry_lower]
    
    # Try exact enum match
    try:
        return Industry(industry_lower)
    except ValueError:
        available = list(industry_map.keys())
        raise ValueError(f"Unknown industry '{industry_str}'. Available: {', '.join(available)}")

def parse_strategies(strategies_str: str) -> List[PromptStrategy]:
    """Parse comma-separated strategies string to PromptStrategy list"""
    strategy_map = {
        'baseline': PromptStrategy.BASELINE,
        'competitive': PromptStrategy.COMPETITIVE,
        'category': PromptStrategy.CATEGORY_DOMINANCE,
        'category_dominance': PromptStrategy.CATEGORY_DOMINANCE,
        'media': PromptStrategy.MEDIA_PRESENCE,
        'media_presence': PromptStrategy.MEDIA_PRESENCE,
        'purchase': PromptStrategy.PURCHASE_JOURNEY,
        'purchase_journey': PromptStrategy.PURCHASE_JOURNEY,
        'sentiment': PromptStrategy.SENTIMENT,
        'temporal': PromptStrategy.TEMPORAL,
        'innovation': PromptStrategy.INNOVATION,
        'sustainability': PromptStrategy.SUSTAINABILITY,
        'customer': PromptStrategy.CUSTOMER_EXPERIENCE,
        'customer_experience': PromptStrategy.CUSTOMER_EXPERIENCE
    }
    
    strategies = []
    for strategy_str in strategies_str.split(','):
        strategy_str = strategy_str.strip().lower()
        if strategy_str in strategy_map:
            strategies.append(strategy_map[strategy_str])
        else:
            try:
                strategies.append(PromptStrategy(strategy_str))
            except ValueError:
                available = list(strategy_map.keys())
                raise ValueError(f"Unknown strategy '{strategy_str}'. Available: {', '.join(available)}")
    
    return strategies

def main():
    parser = argparse.ArgumentParser(
        description="AI Citation Audit - Programmatic brand visibility analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick audit
  python cli.py --brand "PacSun" --competitors "Urban Outfitters,American Eagle" --industry fashion

  # Competitive analysis
  python cli.py --brand "Tesla" --competitors "Ford,GM,BMW" --industry automotive --strategies competitive,category,purchase --max-prompts 24

  # Media presence audit
  python cli.py --brand "Pickle Robot" --industry robotics --strategies media,temporal,sentiment --max-prompts 18

  # Custom configuration
  python cli.py --brand "HoneyBaked Ham" --industry food --strategies baseline,competitive,media --engines perplexity,chatgpt,claude --parallel --output json,csv

Industries: food, fashion, robotics, tech, consumer, automotive, healthcare, financial, entertainment, travel
Strategies: baseline, competitive, category, media, purchase, sentiment, temporal, innovation, sustainability, customer
Engines: perplexity, chatgpt, claude, gemini
        """
    )
    
    # Required arguments
    parser.add_argument('--brand', required=True, help='Brand name to audit')
    
    # Optional arguments
    parser.add_argument('--competitors', help='Comma-separated list of competitors')
    parser.add_argument('--industry', default='consumer', help='Industry category (default: consumer)')
    parser.add_argument('--strategies', default='baseline,competitive', help='Comma-separated prompt strategies (default: baseline,competitive)')
    parser.add_argument('--max-prompts', type=int, default=12, help='Maximum number of prompts to generate (default: 12)')
    parser.add_argument('--engines', default='perplexity,chatgpt,claude,gemini', help='Comma-separated list of engines to use')
    parser.add_argument('--output', default='json,csv', help='Output formats: json,csv (default: json,csv)')
    parser.add_argument('--output-dir', default='outputs', help='Output directory (default: outputs)')
    parser.add_argument('--region', default='US', help='Region for analysis (default: US)')
    parser.add_argument('--language', default='English', help='Language for prompts (default: English)')
    parser.add_argument('--time-hint', default='recent', help='Time context for queries (default: recent)')
    
    # Execution options
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution (faster)')
    parser.add_argument('--sequential', action='store_true', help='Force sequential execution (slower but more reliable)')
    parser.add_argument('--custom-prompts', help='Path to file containing custom prompts (one per line)')
    
    # Preset modes
    parser.add_argument('--quick', action='store_true', help='Quick audit mode (baseline + competitive, 12 prompts)')
    parser.add_argument('--competitive-mode', action='store_true', help='Competitive analysis mode (24 prompts)')
    parser.add_argument('--media-mode', action='store_true', help='Media presence mode (18 prompts)')
    
    # Output options
    parser.add_argument('--quiet', action='store_true', help='Suppress progress output')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--json-only', action='store_true', help='Output only JSON results to stdout')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Parse competitors
        competitors = []
        if args.competitors:
            competitors = [c.strip() for c in args.competitors.split(',')]
        
        # Parse industry
        industry = parse_industry(args.industry)
        
        # Parse strategies
        strategies = parse_strategies(args.strategies)
        
        # Parse engines
        engines = [e.strip() for e in args.engines.split(',')]
        
        # Parse output formats
        output_formats = [f.strip() for f in args.output.split(',')]
        
        # Load custom prompts if provided
        custom_prompts = []
        if args.custom_prompts:
            try:
                with open(args.custom_prompts, 'r') as f:
                    custom_prompts = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"Error: Custom prompts file '{args.custom_prompts}' not found")
                sys.exit(1)
        
        # Handle preset modes
        if args.quick:
            if not args.quiet:
                print(f"🚀 Running quick audit for {args.brand}")
            results = quick_audit(args.brand, competitors, industry)
        elif args.competitive_mode:
            if not args.quiet:
                print(f"🥊 Running competitive analysis for {args.brand}")
            results = competitive_audit(args.brand, competitors, industry)
        elif args.media_mode:
            if not args.quiet:
                print(f"📰 Running media presence audit for {args.brand}")
            results = media_presence_audit(args.brand, industry)
        else:
            # Custom configuration
            parallel_execution = True
            if args.sequential:
                parallel_execution = False
            elif args.parallel:
                parallel_execution = True
            
            config = AuditConfig(
                brand=args.brand,
                competitors=competitors,
                industry=industry,
                strategies=strategies,
                max_prompts=args.max_prompts,
                region=args.region,
                language=args.language,
                time_hint=args.time_hint,
                engines=engines,
                output_formats=output_formats,
                parallel_execution=parallel_execution,
                custom_prompts=custom_prompts
            )
            
            if not args.quiet:
                print(f"🔍 Running custom audit for {args.brand}")
                print(f"   Industry: {industry.value}")
                print(f"   Strategies: {', '.join(s.value for s in strategies)}")
                print(f"   Max prompts: {args.max_prompts}")
                print(f"   Engines: {', '.join(engines)}")
                print(f"   Execution: {'parallel' if parallel_execution else 'sequential'}")
            
            api = CitationAuditAPI()
            results = api.run_audit(config)
        
        # Export results
        if not args.json_only:
            api = CitationAuditAPI()
            output_files = api.export_results(results, args.output_dir)
            
            if not args.quiet:
                print(f"\n✅ Audit completed in {results.execution_time:.1f} seconds")
                print(f"📊 Results:")
                print(f"   Total Score: {results.scores['total']}/100")
                print(f"   Presence: {results.scores['presence']}/100")
                print(f"   Prominence: {results.scores['prominence']}/100")
                print(f"   Quality: {results.scores['quality']}/100")
                print(f"   Citations: {len(results.citations)}")
                print(f"   Platforms: {', '.join(results.metadata['platforms_used'])}")
                
                if results.competitive_analysis['competitor_mentions']:
                    print(f"   Competitive Delta: {results.competitive_analysis['competitive_delta']}%")
                
                print(f"\n📁 Output files:")
                for format_type, file_path in output_files.items():
                    print(f"   {format_type.upper()}: {file_path}")
                
                if results.recommendations:
                    print(f"\n💡 Recommendations:")
                    for i, rec in enumerate(results.recommendations, 1):
                        print(f"   {i}. {rec}")
        
        # JSON-only output for programmatic consumption
        if args.json_only:
            output_data = {
                "brand": results.brand,
                "scores": results.scores,
                "competitive_analysis": results.competitive_analysis,
                "recommendations": results.recommendations,
                "metadata": results.metadata,
                "execution_time": results.execution_time
            }
            print(json.dumps(output_data, indent=2))
    
    except KeyboardInterrupt:
        print("\n❌ Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

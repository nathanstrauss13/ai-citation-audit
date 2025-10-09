#!/usr/bin/env python3
"""
AI Citation Audit API - Usage Examples
Demonstrates various ways to use the programmatic API
"""

from api import (
    CitationAuditAPI, AuditConfig, Industry, PromptStrategy,
    quick_audit, competitive_audit, media_presence_audit
)

def example_1_quick_audit():
    """Example 1: Quick audit with minimal configuration"""
    print("🚀 Example 1: Quick Audit")
    print("-" * 50)
    
    # Simple quick audit
    results = quick_audit(
        brand="PacSun",
        competitors=["Urban Outfitters", "American Eagle"],
        industry=Industry.FASHION_RETAIL
    )
    
    print(f"Brand: {results.brand}")
    print(f"Total Score: {results.scores['total']}/100")
    print(f"Citations Found: {len(results.citations)}")
    print(f"Execution Time: {results.execution_time:.1f}s")
    print()

def example_2_competitive_analysis():
    """Example 2: Comprehensive competitive analysis"""
    print("🥊 Example 2: Competitive Analysis")
    print("-" * 50)
    
    results = competitive_audit(
        brand="Tesla",
        competitors=["Ford", "GM", "BMW", "Mercedes"],
        industry=Industry.AUTOMOTIVE
    )
    
    print(f"Brand: {results.brand}")
    print(f"Competitive Delta: {results.competitive_analysis['competitive_delta']}%")
    print(f"Competitor Mentions: {results.competitive_analysis['competitor_mentions']}")
    print(f"Total Score: {results.scores['total']}/100")
    print()

def example_3_media_presence():
    """Example 3: Media presence focused audit"""
    print("📰 Example 3: Media Presence Audit")
    print("-" * 50)
    
    results = media_presence_audit(
        brand="Pickle Robot",
        industry=Industry.ROBOTICS
    )
    
    print(f"Brand: {results.brand}")
    print(f"Media Quality Score: {results.scores['quality']}/100")
    print(f"Recommendations: {len(results.recommendations)}")
    for i, rec in enumerate(results.recommendations, 1):
        print(f"  {i}. {rec}")
    print()

def example_4_custom_configuration():
    """Example 4: Custom configuration with specific strategies"""
    print("⚙️ Example 4: Custom Configuration")
    print("-" * 50)
    
    config = AuditConfig(
        brand="HoneyBaked Ham",
        competitors=["Spiral Ham Store", "Glazed Ham Co"],
        industry=Industry.FOOD_BEVERAGE,
        strategies=[
            PromptStrategy.BASELINE,
            PromptStrategy.COMPETITIVE,
            PromptStrategy.PURCHASE_JOURNEY,
            PromptStrategy.SENTIMENT
        ],
        max_prompts=20,
        engines=["perplexity", "chatgpt", "claude"],  # Exclude gemini for faster testing
        parallel_execution=True,
        custom_prompts=[
            "Best holiday ham brands with sources",
            "Where to buy quality spiral ham with reviews"
        ]
    )
    
    api = CitationAuditAPI()
    results = api.run_audit(config)
    
    print(f"Brand: {results.brand}")
    print(f"Industry: {config.industry.value}")
    print(f"Strategies Used: {', '.join(s.value for s in config.strategies)}")
    print(f"Custom Prompts: {len(config.custom_prompts)}")
    print(f"Total Prompts Generated: {results.metadata['prompts_executed']}")
    print(f"Platforms Used: {', '.join(results.metadata['platforms_used'])}")
    print(f"Total Score: {results.scores['total']}/100")
    print()

def example_5_batch_processing():
    """Example 5: Batch processing multiple brands"""
    print("📦 Example 5: Batch Processing")
    print("-" * 50)
    
    brands_to_audit = [
        {"brand": "Nike", "industry": Industry.FASHION_RETAIL, "competitors": ["Adidas", "Puma"]},
        {"brand": "McDonald's", "industry": Industry.FOOD_BEVERAGE, "competitors": ["Burger King", "KFC"]},
        {"brand": "Apple", "industry": Industry.B2B_TECH, "competitors": ["Samsung", "Google"]}
    ]
    
    api = CitationAuditAPI()
    batch_results = []
    
    for brand_config in brands_to_audit:
        config = AuditConfig(
            brand=brand_config["brand"],
            competitors=brand_config["competitors"],
            industry=brand_config["industry"],
            strategies=[PromptStrategy.BASELINE, PromptStrategy.COMPETITIVE],
            max_prompts=6,  # Smaller for demo
            engines=["perplexity", "chatgpt"]  # Faster subset
        )
        
        results = api.run_audit(config)
        batch_results.append(results)
        
        print(f"✅ {results.brand}: {results.scores['total']}/100 ({len(results.citations)} citations)")
    
    # Summary
    avg_score = sum(r.scores['total'] for r in batch_results) / len(batch_results)
    total_citations = sum(len(r.citations) for r in batch_results)
    
    print(f"\n📊 Batch Summary:")
    print(f"   Brands Audited: {len(batch_results)}")
    print(f"   Average Score: {avg_score:.1f}/100")
    print(f"   Total Citations: {total_citations}")
    print()

def example_6_export_formats():
    """Example 6: Different export formats"""
    print("💾 Example 6: Export Formats")
    print("-" * 50)
    
    config = AuditConfig(
        brand="Starbucks",
        competitors=["Dunkin'", "Costa Coffee"],
        industry=Industry.FOOD_BEVERAGE,
        strategies=[PromptStrategy.BASELINE],
        max_prompts=3,  # Small for demo
        output_formats=["json", "csv"]
    )
    
    api = CitationAuditAPI()
    results = api.run_audit(config)
    
    # Export results
    output_files = api.export_results(results, "example_outputs")
    
    print(f"Brand: {results.brand}")
    print(f"Export Files Created:")
    for format_type, file_path in output_files.items():
        print(f"  {format_type.upper()}: {file_path}")
    print()

def example_7_industry_specific_analysis():
    """Example 7: Industry-specific tier-1 source analysis"""
    print("🏭 Example 7: Industry-Specific Analysis")
    print("-" * 50)
    
    # Fashion brand - should prioritize WWD, Hypebeast, Vogue
    fashion_results = quick_audit("Zara", ["H&M", "Uniqlo"], Industry.FASHION_RETAIL)
    
    # Food brand - should prioritize Food & Wine, Bon Appetit, Eater
    food_results = quick_audit("Chipotle", ["Qdoba", "Moe's"], Industry.FOOD_BEVERAGE)
    
    # Tech brand - should prioritize TechCrunch, VentureBeat, Wired
    tech_results = quick_audit("Slack", ["Microsoft Teams", "Discord"], Industry.B2B_TECH)
    
    print("Industry-Specific Quality Scores:")
    print(f"  Fashion (Zara): {fashion_results.scores['quality']}/100")
    print(f"  Food (Chipotle): {food_results.scores['quality']}/100")
    print(f"  Tech (Slack): {tech_results.scores['quality']}/100")
    print()
    
    print("This demonstrates how different industries get different quality scoring")
    print("based on their respective tier-1 publications.")
    print()

def main():
    """Run all examples"""
    print("🎯 AI Citation Audit API - Usage Examples")
    print("=" * 60)
    print()
    
    try:
        # Run examples (comment out slow ones for quick testing)
        example_1_quick_audit()
        # example_2_competitive_analysis()  # Slower - more prompts
        # example_3_media_presence()        # Slower - more prompts
        example_4_custom_configuration()
        # example_5_batch_processing()      # Slower - multiple brands
        example_6_export_formats()
        example_7_industry_specific_analysis()
        
        print("✅ All examples completed successfully!")
        print()
        print("💡 Next Steps:")
        print("1. Try the CLI: python cli.py --brand 'YourBrand' --industry fashion")
        print("2. Customize strategies: --strategies competitive,media,purchase")
        print("3. Use parallel execution: --parallel")
        print("4. Export formats: --output json,csv")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

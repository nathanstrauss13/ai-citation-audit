#!/usr/bin/env python3
"""
AI Citation Audit API - Programmatic Interface
Transforms web-based system into command-line and automated workflow tool
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple
import logging
import json
import os
import asyncio
import concurrent.futures
from datetime import datetime
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Industry(Enum):
    """Industry categories with specific media tier definitions"""
    FOOD_BEVERAGE = "food_beverage"
    FASHION_RETAIL = "fashion_retail" 
    ROBOTICS = "robotics"
    B2B_TECH = "b2b_tech"
    CONSUMER_GOODS = "consumer_goods"
    AUTOMOTIVE = "automotive"
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    ENTERTAINMENT = "entertainment"
    TRAVEL_HOSPITALITY = "travel_hospitality"

class PromptStrategy(Enum):
    """Prompt generation strategies for different analysis focuses"""
    BASELINE = "baseline"                    # Basic brand mentions
    COMPETITIVE = "competitive"              # vs competitors
    CATEGORY_DOMINANCE = "category_dominance" # market leadership
    MEDIA_PRESENCE = "media_presence"        # news coverage
    PURCHASE_JOURNEY = "purchase_journey"    # buying decisions
    SENTIMENT = "sentiment"                  # brand perception
    TEMPORAL = "temporal"                    # recent developments
    INNOVATION = "innovation"                # product/tech focus
    SUSTAINABILITY = "sustainability"        # ESG focus
    CUSTOMER_EXPERIENCE = "customer_experience" # service quality

@dataclass
class AuditConfig:
    """Configuration for citation audit execution"""
    brand: str
    competitors: List[str] = field(default_factory=list)
    industry: Industry = Industry.CONSUMER_GOODS
    strategies: List[PromptStrategy] = field(default_factory=lambda: [PromptStrategy.BASELINE, PromptStrategy.COMPETITIVE])
    max_prompts: int = 12
    region: str = "US"
    language: str = "English"
    time_hint: str = "recent"
    engines: List[str] = field(default_factory=lambda: ["perplexity", "chatgpt", "claude", "gemini"])
    output_formats: List[str] = field(default_factory=lambda: ["json", "csv"])
    include_analysis: bool = True
    parallel_execution: bool = True
    custom_prompts: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.brand:
            raise ValueError("Brand name is required")
        if self.max_prompts < 1 or self.max_prompts > 50:
            raise ValueError("max_prompts must be between 1 and 50")
        if len(self.competitors) > 10:
            raise ValueError("Maximum 10 competitors supported")

@dataclass
class AuditResults:
    """Results from citation audit execution"""
    brand: str
    config: AuditConfig
    citations: List[Dict[str, Any]]
    scores: Dict[str, float]
    competitive_analysis: Dict[str, Any]
    recommendations: List[str]
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class SmartPromptGenerator:
    """Industry-aware prompt generation with strategic focus"""
    
    def __init__(self, industry: Industry):
        self.industry = industry
        self.industry_contexts = self._load_industry_contexts()
    
    def _load_industry_contexts(self) -> Dict[Industry, Dict[str, Any]]:
        """Load industry-specific contexts and templates"""
        return {
            Industry.FASHION_RETAIL: {
                "keywords": ["fashion", "style", "apparel", "clothing", "trends", "runway", "designer"],
                "contexts": ["shopping", "style guide", "fashion week", "celebrity fashion", "street style"],
                "tier1_sources": ["WWD", "Hypebeast", "Vogue", "Harper's Bazaar", "Elle"],
                "competitors_context": "fashion retailers and clothing brands"
            },
            Industry.FOOD_BEVERAGE: {
                "keywords": ["food", "restaurant", "dining", "cuisine", "recipe", "chef", "culinary"],
                "contexts": ["dining out", "cooking", "food trends", "restaurant reviews", "recipes"],
                "tier1_sources": ["Food & Wine", "Bon Appetit", "Eater", "Serious Eats", "Food Network"],
                "competitors_context": "food and beverage brands"
            },
            Industry.ROBOTICS: {
                "keywords": ["robotics", "automation", "AI", "machine learning", "industrial", "manufacturing"],
                "contexts": ["industrial automation", "AI applications", "manufacturing efficiency", "robotics innovation"],
                "tier1_sources": ["The Robot Report", "IEEE Spectrum", "Robotics Business Review", "TechCrunch"],
                "competitors_context": "robotics and automation companies"
            },
            Industry.B2B_TECH: {
                "keywords": ["enterprise", "software", "SaaS", "technology", "business solutions", "productivity"],
                "contexts": ["business efficiency", "enterprise software", "digital transformation", "productivity tools"],
                "tier1_sources": ["TechCrunch", "VentureBeat", "The Information", "IEEE", "Wired"],
                "competitors_context": "B2B technology companies"
            },
            Industry.AUTOMOTIVE: {
                "keywords": ["automotive", "cars", "vehicles", "electric", "autonomous", "mobility"],
                "contexts": ["car buying", "automotive technology", "electric vehicles", "car reviews"],
                "tier1_sources": ["Car and Driver", "Motor Trend", "Automotive News", "Electrek", "The Verge"],
                "competitors_context": "automotive manufacturers"
            },
            Industry.CONSUMER_GOODS: {
                "keywords": ["consumer", "products", "retail", "shopping", "brands", "lifestyle"],
                "contexts": ["shopping", "product reviews", "consumer trends", "brand comparison"],
                "tier1_sources": ["Forbes", "Business Insider", "Wall Street Journal", "Consumer Reports", "Fast Company"],
                "competitors_context": "consumer goods companies"
            }
        }
    
    def generate_prompts(self, config: AuditConfig) -> List[str]:
        """Generate strategic prompts based on configuration"""
        prompts = []
        context = self.industry_contexts.get(config.industry, self.industry_contexts[Industry.CONSUMER_GOODS])
        
        # Add custom prompts first
        prompts.extend(config.custom_prompts)
        
        # Generate strategy-based prompts
        for strategy in config.strategies:
            strategy_prompts = self._generate_strategy_prompts(strategy, config, context)
            prompts.extend(strategy_prompts)
        
        # Limit to max_prompts
        return prompts[:config.max_prompts]
    
    def _generate_strategy_prompts(self, strategy: PromptStrategy, config: AuditConfig, context: Dict[str, Any]) -> List[str]:
        """Generate prompts for specific strategy"""
        prompts = []
        brand = config.brand
        competitors = config.competitors
        keywords = context["keywords"]
        contexts = context["contexts"]
        
        if strategy == PromptStrategy.BASELINE:
            prompts.extend([
                f"Tell me about {brand}. Include sources and references.",
                f"What is {brand} known for? Provide authoritative sources.",
                f"Describe {brand}'s products and services with citations."
            ])
        
        elif strategy == PromptStrategy.COMPETITIVE:
            for competitor in competitors[:3]:  # Limit to top 3 for prompt generation
                prompts.extend([
                    f"Compare {brand} vs {competitor}. Include sources.",
                    f"How does {brand} differentiate from {competitor}? Cite sources.",
                    f"Which is better, {brand} or {competitor}? Provide evidence."
                ])
        
        elif strategy == PromptStrategy.MEDIA_PRESENCE:
            prompts.extend([
                f"Recent news about {brand}. Include publication sources.",
                f"What are journalists saying about {brand}? Cite articles.",
                f"{brand} in the media. Provide news sources and links."
            ])
        
        elif strategy == PromptStrategy.CATEGORY_DOMINANCE:
            category = context.get("competitors_context", "companies in this industry")
            prompts.extend([
                f"Is {brand} a leader among {category}? Cite sources.",
                f"Top {category} - where does {brand} rank? Include references.",
                f"{brand}'s market position in {keywords[0]}. Provide sources."
            ])
        
        elif strategy == PromptStrategy.PURCHASE_JOURNEY:
            prompts.extend([
                f"Should I buy from {brand}? Include expert opinions and sources.",
                f"Best {keywords[0]} brands - how does {brand} compare? Cite sources.",
                f"Reviews of {brand}. Include review sources and ratings."
            ])
        
        return prompts

class CitationAuditAPI:
    """Main API class for programmatic citation audits"""
    
    def __init__(self):
        self.platforms = self._initialize_platforms()
        logger.info(f"CitationAuditAPI initialized with {len(self.platforms)} platforms")
    
    def _initialize_platforms(self) -> Dict[str, Any]:
        """Initialize available platforms"""
        platforms = {}
        
        try:
            from platforms.perplexity import PerplexityPlatform
            platforms['perplexity'] = PerplexityPlatform()
            logger.info("✅ Perplexity platform loaded")
        except Exception as e:
            logger.warning(f"❌ Perplexity platform failed: {e}")
        
        try:
            from platforms.chatgpt import ChatGPTPlatform
            platforms['chatgpt'] = ChatGPTPlatform()
            logger.info("✅ ChatGPT platform loaded")
        except Exception as e:
            logger.warning(f"❌ ChatGPT platform failed: {e}")
        
        try:
            from platforms.claude import ClaudePlatform
            platforms['claude'] = ClaudePlatform()
            logger.info("✅ Claude platform loaded")
        except Exception as e:
            logger.warning(f"❌ Claude platform failed: {e}")
        
        try:
            from platforms.gemini import GeminiPlatform
            platforms['gemini'] = GeminiPlatform()
            logger.info("✅ Gemini platform loaded")
        except Exception as e:
            logger.warning(f"❌ Gemini platform failed: {e}")
        
        # If no platforms loaded, create a fallback mock platform for testing
        if not platforms:
            logger.warning("No platforms loaded, creating fallback mock platform")
            platforms['mock'] = self._create_mock_platform()
        
        return platforms
    
    def _create_mock_platform(self):
        """Create a mock platform for testing when no real platforms are available"""
        class MockPlatform:
            def get_citations(self, prompt):
                return [
                    {
                        'url': 'https://example.com/mock-citation-1',
                        'type': 'mock',
                        'domain': 'example.com'
                    },
                    {
                        'url': 'https://test.com/mock-citation-2', 
                        'type': 'mock',
                        'domain': 'test.com'
                    }
                ]
        return MockPlatform()
    
    def run_audit(self, config: AuditConfig) -> AuditResults:
        """Execute citation audit with given configuration"""
        start_time = datetime.now()
        logger.info(f"Starting audit for {config.brand} with {len(config.strategies)} strategies")
        
        # Generate prompts
        prompt_generator = SmartPromptGenerator(config.industry)
        prompts = prompt_generator.generate_prompts(config)
        logger.info(f"Generated {len(prompts)} prompts")
        
        # Execute audit across platforms
        all_citations = []
        available_platforms = {k: v for k, v in self.platforms.items() if k in config.engines or k == 'mock'}
        
        # If no platforms available after filtering, use all available platforms
        if not available_platforms:
            available_platforms = self.platforms
        
        if config.parallel_execution and len(available_platforms) > 0:
            all_citations = self._run_parallel_audit(prompts, available_platforms)
        else:
            all_citations = self._run_sequential_audit(prompts, available_platforms)
        
        # Analyze results
        scores = self._calculate_scores(all_citations, config)
        competitive_analysis = self._analyze_competitive_landscape(all_citations, config)
        recommendations = self._generate_recommendations(all_citations, scores, config)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return AuditResults(
            brand=config.brand,
            config=config,
            citations=all_citations,
            scores=scores,
            competitive_analysis=competitive_analysis,
            recommendations=recommendations,
            execution_time=execution_time,
            timestamp=start_time,
            metadata={
                "total_citations": len(all_citations),
                "platforms_used": list(available_platforms.keys()),
                "prompts_executed": len(prompts)
            }
        )
    
    def _run_parallel_audit(self, prompts: List[str], platforms: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute audit in parallel across platforms"""
        all_citations = []
        platform_citation_counts = {name: 0 for name in platforms.keys()}
        
        logger.info(f"🚀 Starting parallel audit with {len(platforms)} platforms: {list(platforms.keys())}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            for i, prompt in enumerate(prompts):
                logger.info(f"📝 Processing prompt {i+1}/{len(prompts)}: {prompt[:50]}...")
                futures = []
                
                for platform_name, platform in platforms.items():
                    future = executor.submit(self._execute_platform_query, platform, prompt, platform_name)
                    futures.append((future, platform_name))
                
                # Collect results with detailed logging
                for future, platform_name in futures:
                    try:
                        citations = future.result(timeout=60)
                        citation_count = len(citations)
                        platform_citation_counts[platform_name] += citation_count
                        all_citations.extend(citations)
                        logger.info(f"✅ {platform_name}: {citation_count} citations (total: {platform_citation_counts[platform_name]})")
                    except Exception as e:
                        logger.error(f"❌ {platform_name} query failed: {e}")
        
        logger.info(f"🎯 FINAL CITATION COUNTS BY PLATFORM:")
        for platform_name, count in platform_citation_counts.items():
            logger.info(f"   {platform_name}: {count} citations")
        logger.info(f"📊 TOTAL CITATIONS COLLECTED: {len(all_citations)}")
        
        return all_citations
    
    def _run_sequential_audit(self, prompts: List[str], platforms: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute audit sequentially across platforms"""
        all_citations = []
        
        for prompt in prompts:
            for platform_name, platform in platforms.items():
                try:
                    citations = self._execute_platform_query(platform, prompt, platform_name)
                    all_citations.extend(citations)
                except Exception as e:
                    logger.error(f"Platform {platform_name} query failed: {e}")
        
        return all_citations
    
    def _execute_platform_query(self, platform: Any, prompt: str, platform_name: str) -> List[Dict[str, Any]]:
        """Execute query on specific platform"""
        try:
            citations = platform.get_citations(prompt)
            # Add platform metadata
            for citation in citations:
                citation['platform'] = platform_name
                citation['prompt'] = prompt
            return citations
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {e}")
            return []
    
    def _calculate_scores(self, citations: List[Dict[str, Any]], config: AuditConfig) -> Dict[str, float]:
        """Calculate audit scores"""
        if not citations:
            return {"total": 0.0, "presence": 0.0, "prominence": 0.0, "quality": 0.0}
        
        # Basic scoring - can be enhanced with industry-specific logic
        total_citations = len(citations)
        unique_domains = len(set(self._extract_domain(c.get('url', '')) for c in citations))
        
        presence_score = min(100.0, total_citations * 5)  # 5 points per citation, max 100
        prominence_score = min(100.0, unique_domains * 10)  # 10 points per unique domain
        quality_score = self._calculate_quality_score(citations, config)
        
        total_score = (presence_score + prominence_score + quality_score) / 3
        
        return {
            "total": round(total_score, 1),
            "presence": round(presence_score, 1),
            "prominence": round(prominence_score, 1),
            "quality": round(quality_score, 1)
        }
    
    def _calculate_quality_score(self, citations: List[Dict[str, Any]], config: AuditConfig) -> float:
        """Calculate quality score based on source authority"""
        if not citations:
            return 0.0
        
        # Get industry-specific tier-1 sources
        prompt_generator = SmartPromptGenerator(config.industry)
        context = prompt_generator.industry_contexts.get(config.industry, {})
        tier1_sources = context.get("tier1_sources", [])
        
        tier1_count = 0
        for citation in citations:
            url = citation.get('url', '')
            domain = self._extract_domain(url)
            if any(source.lower() in domain.lower() for source in tier1_sources):
                tier1_count += 1
        
        # Quality score based on tier-1 source percentage
        if tier1_count > 0:
            tier1_percentage = tier1_count / len(citations)
            return min(100.0, tier1_percentage * 100 + 20)  # Bonus for having tier-1 sources
        
        return 50.0  # Base score for having citations
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return ""
    
    def _analyze_competitive_landscape(self, citations: List[Dict[str, Any]], config: AuditConfig) -> Dict[str, Any]:
        """Analyze competitive mentions in citations"""
        competitor_mentions = {}
        brand_mentions = 0
        
        brand_lower = config.brand.lower()
        
        for citation in citations:
            prompt = citation.get('prompt', '').lower()
            url = citation.get('url', '').lower()
            
            # Count brand mentions
            if brand_lower in prompt or brand_lower in url:
                brand_mentions += 1
            
            # Count competitor mentions
            for competitor in config.competitors:
                competitor_lower = competitor.lower()
                if competitor_lower in prompt or competitor_lower in url:
                    competitor_mentions[competitor] = competitor_mentions.get(competitor, 0) + 1
        
        return {
            "brand_mentions": brand_mentions,
            "competitor_mentions": competitor_mentions,
            "competitive_delta": self._calculate_competitive_delta(brand_mentions, competitor_mentions)
        }
    
    def _calculate_competitive_delta(self, brand_mentions: int, competitor_mentions: Dict[str, int]) -> float:
        """Calculate competitive positioning delta"""
        if not competitor_mentions:
            return 100.0
        
        total_competitor_mentions = sum(competitor_mentions.values())
        if total_competitor_mentions == 0:
            return 100.0
        
        # Calculate relative positioning
        brand_share = brand_mentions / (brand_mentions + total_competitor_mentions)
        return round(brand_share * 100, 1)
    
    def _generate_recommendations(self, citations: List[Dict[str, Any]], scores: Dict[str, float], config: AuditConfig) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if scores["presence"] < 50:
            recommendations.append("Increase brand visibility through content marketing and PR initiatives")
        
        if scores["prominence"] < 50:
            recommendations.append("Diversify media coverage across more authoritative publications")
        
        if scores["quality"] < 70:
            recommendations.append("Focus on securing coverage in industry-leading publications")
        
        if len(citations) < 10:
            recommendations.append("Expand content strategy to generate more brand mentions")
        
        return recommendations
    
    def export_results(self, results: AuditResults, output_dir: str = "outputs") -> Dict[str, str]:
        """Export results in multiple formats"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = results.timestamp.strftime("%Y%m%d_%H%M")
        brand_safe = results.brand.replace(" ", "_")
        
        outputs = {}
        
        # JSON export
        if "json" in results.config.output_formats:
            json_path = os.path.join(output_dir, f"{brand_safe}_{timestamp}.json")
            with open(json_path, 'w') as f:
                json.dump({
                    "brand": results.brand,
                    "scores": results.scores,
                    "competitive_analysis": results.competitive_analysis,
                    "recommendations": results.recommendations,
                    "citations": results.citations,
                    "metadata": results.metadata
                }, f, indent=2, default=str)
            outputs["json"] = json_path
        
        # CSV export
        if "csv" in results.config.output_formats:
            csv_path = os.path.join(output_dir, f"{brand_safe}_{timestamp}_citations.csv")
            if HAS_PANDAS:
                df = pd.DataFrame(results.citations)
                df.to_csv(csv_path, index=False)
            else:
                # Fallback CSV export without pandas
                self._export_csv_fallback(results.citations, csv_path)
            outputs["csv"] = csv_path
        
        return outputs
    
    def _export_csv_fallback(self, citations: List[Dict[str, Any]], csv_path: str):
        """Fallback CSV export without pandas"""
        import csv
        
        if not citations:
            # Create empty CSV with headers
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['url', 'type', 'engine', 'platform', 'prompt'])
            return
        
        # Get all unique keys from citations
        all_keys = set()
        for citation in citations:
            all_keys.update(citation.keys())
        
        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for citation in citations:
                # Handle missing keys by providing empty strings
                row = {key: citation.get(key, '') for key in fieldnames}
                writer.writerow(row)

# Convenience functions for common use cases
def quick_audit(brand: str, competitors: List[str] = None, industry: Industry = Industry.CONSUMER_GOODS) -> AuditResults:
    """Quick audit with default settings"""
    config = AuditConfig(
        brand=brand,
        competitors=competitors or [],
        industry=industry,
        strategies=[PromptStrategy.BASELINE, PromptStrategy.COMPETITIVE],
        max_prompts=12
    )
    
    api = CitationAuditAPI()
    return api.run_audit(config)

def competitive_audit(brand: str, competitors: List[str], industry: Industry = Industry.CONSUMER_GOODS) -> AuditResults:
    """Competitive-focused audit"""
    config = AuditConfig(
        brand=brand,
        competitors=competitors,
        industry=industry,
        strategies=[PromptStrategy.COMPETITIVE, PromptStrategy.CATEGORY_DOMINANCE, PromptStrategy.PURCHASE_JOURNEY],
        max_prompts=24
    )
    
    api = CitationAuditAPI()
    return api.run_audit(config)

def media_presence_audit(brand: str, industry: Industry = Industry.CONSUMER_GOODS) -> AuditResults:
    """Media presence focused audit"""
    config = AuditConfig(
        brand=brand,
        industry=industry,
        strategies=[PromptStrategy.MEDIA_PRESENCE, PromptStrategy.TEMPORAL, PromptStrategy.SENTIMENT],
        max_prompts=18
    )
    
    api = CitationAuditAPI()
    return api.run_audit(config)

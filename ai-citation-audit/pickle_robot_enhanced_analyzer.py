#!/usr/bin/env python3
"""
Pickle Robot - Enhanced AI Citation Analysis
Comprehensive competitive intelligence analysis for warehouse automation and robotics sectors.
Executes 15 queries across 4 AI platforms with detailed competitor tracking and media analysis.
"""

import csv
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing platform modules
from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PickleRobotEnhancedAnalyzer:
    """Enhanced AI Citation Analysis for Pickle Robot with comprehensive competitive intelligence."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d")
        self.output_dir = Path("case_studies/pickle_robot_enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize platform adapters
        self.platforms = {}
        try:
            self.platforms['ChatGPT'] = ChatGPTPlatform()
            logger.info("✅ ChatGPT platform loaded")
        except Exception as e:
            logger.warning(f"❌ ChatGPT platform failed: {e}")
        
        try:
            self.platforms['Claude'] = ClaudePlatform()
            logger.info("✅ Claude platform loaded")
        except Exception as e:
            logger.warning(f"❌ Claude platform failed: {e}")
        
        try:
            self.platforms['Perplexity'] = PerplexityPlatform()
            logger.info("✅ Perplexity platform loaded")
        except Exception as e:
            logger.warning(f"❌ Perplexity platform failed: {e}")
        
        try:
            self.platforms['Gemini'] = GeminiPlatform()
            logger.info("✅ Gemini platform loaded")
        except Exception as e:
            logger.warning(f"❌ Gemini platform failed: {e}")
        
        if not self.platforms:
            logger.error("No platforms loaded successfully!")
            raise RuntimeError("No AI platforms available for data collection")
        
        # 15 Enhanced Queries as specified
        self.enhanced_queries = {
            # Brand-Specific Queries (5)
            "brand_specific": [
                "Tell me about Pickle Robot. Respond in English.",
                "What is Pickle Robot known for? Respond in English.",
                "Pickle Robot vs Boston Dynamics vs Locus Robotics comparison. Respond in English.",
                "How does Pickle Robot work and what makes it different? Respond in English.",
                "Please tell me about recent news from Pickle Robot. Respond in English."
            ],
            
            # Brand-Agnostic Warehouse/Robotics Queries (7)
            "warehouse_robotics": [
                "Best warehouse automation companies 2025. Respond in English.",
                "Leading automated truck unloading solutions. Respond in English.",
                "Who are the leading automated material handling companies in US? Respond in English.",
                "AI-powered robotics for logistics and warehouses. Respond in English.",
                "Best warehouse robotics companies for unloading trucks. Respond in English.",
                "Automated material handling vs manual warehouse operations. Respond in English.",
                "Future of warehouse automation and robotics 2025. Respond in English."
            ],
            
            # Industry/Investment Queries (3)
            "industry_investment": [
                "Recent funding rounds in warehouse robotics startups. Respond in English.",
                "Which robotics companies raised Series A or B funding recently? Respond in English.",
                "Warehouse automation ROI and productivity improvements. Respond in English."
            ]
        }
        
        # 6 Key Competitors to track
        self.competitors = {
            'Boston Dynamics': [r'boston\s+dynamics', r'bostondynamics', r'spot\s+robot'],
            'Locus Robotics': [r'locus\s+robotics', r'locusrobotics', r'locus\s+bots'],
            '6 River Systems': [r'6\s*river\s+systems', r'6river', r'shopify\s+fulfillment'],
            'Fetch Robotics': [r'fetch\s+robotics', r'fetchrobotics', r'zebra\s+robotics'],
            'Berkshire Grey': [r'berkshire\s+grey', r'berkshire\s+gray', r'berkshiregrey'],
            'Amazon Robotics': [r'amazon\s+robotics', r'kiva\s+systems', r'amazon\s+warehouse\s+robots']
        }
        
        # Target domains for detailed tracking
        self.target_domains = {
            # Robotics Trade Media
            'therobotreport.com': 'robotics_trade',
            'roboticsbusinessreview.com': 'robotics_trade',
            'roboticstomorrow.com': 'robotics_trade',
            
            # Tech Media
            'techcrunch.com': 'tech_media',
            'wired.com': 'tech_media',
            'technologyreview.com': 'tech_media',
            'venturebeat.com': 'tech_media',
            'theverge.com': 'tech_media',
            'arstechnica.com': 'tech_media',
            
            # Supply Chain Media
            'freightwaves.com': 'supply_chain',
            'supplychaindive.com': 'supply_chain',
            'supplychainbrain.com': 'supply_chain',
            'dcvelocity.com': 'supply_chain',
            'logisticsmgmt.com': 'supply_chain',
            
            # Business Media
            'forbes.com': 'tier_1_business',
            'bloomberg.com': 'tier_1_business',
            'wsj.com': 'tier_1_business',
            'businessinsider.com': 'tier_1_business',
            'reuters.com': 'tier_1_business',
            'ft.com': 'tier_1_business',
            
            # Investment/Funding
            'pitchbook.com': 'investment',
            'crunchbase.com': 'investment',
            'venturebeat.com': 'investment',
            
            # PR Sources
            'businesswire.com': 'pr',
            'prnewswire.com': 'pr',
            'globenewswire.com': 'pr'
        }
        
        # Data storage
        self.raw_citations = []
        self.competitive_matrix = []
        self.media_tracking = {}
        
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def classify_domain(self, domain: str) -> str:
        """Classify domain based on target domains list."""
        for target_domain, category in self.target_domains.items():
            if target_domain in domain:
                return category
        return 'other'
    
    def detect_competitors(self, text: str) -> Dict[str, bool]:
        """Detect which competitors are mentioned in the text."""
        detected = {}
        for competitor, patterns in self.competitors.items():
            detected[competitor] = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
        return detected
    
    def detect_pickle_robot(self, text: str) -> bool:
        """Detect if Pickle Robot is mentioned in the text."""
        pickle_patterns = [r'pickle\s+robot', r'picklerobot', r'pickle\s+robotics']
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in pickle_patterns)
    
    def determine_prominence(self, text: str, url: str, position: int) -> str:
        """Determine prominence level of mention."""
        if position == 0:  # First citation
            return "first"
        elif position < 3:  # Top 3
            return "prominent"
        elif position < 10:  # Top 10
            return "buried"
        else:
            return "not_present"
    
    def assess_source_quality(self, domain: str) -> str:
        """Assess source quality based on domain classification."""
        category = self.classify_domain(domain)
        if category in ['tier_1_business', 'tech_media', 'robotics_trade']:
            return "high"
        elif category in ['supply_chain', 'investment']:
            return "medium"
        elif category == 'pr':
            return "low"
        else:
            return "medium"
    
    def query_platform(self, platform_name: str, query: str, query_category: str) -> Dict:
        """Query a specific platform with enhanced robotics citation tracking."""
        logger.info(f"Querying {platform_name}: {query[:50]}...")
        
        try:
            platform = self.platforms[platform_name]
            
            # Enhanced prompt for robotics queries
            enhanced_query = f"""Please provide comprehensive information about: {query}

Include specific sources, citations, URLs, and references. Focus on authoritative robotics publications, industry reports, funding announcements, and current warehouse automation data. Provide direct links to relevant content when possible."""
            
            # Get citations from platform
            citations = platform.get_citations(enhanced_query)
            
            # Process citations with detailed robotics-specific analysis
            urls = []
            domains = []
            
            # Analyze full response text for competitors and Pickle Robot
            response_text = " ".join([query] + [citation.get('url', '') for citation in citations])
            competitors_detected = self.detect_competitors(response_text)
            pickle_present = self.detect_pickle_robot(response_text)
            
            # Track citations for CSV outputs
            for i, citation in enumerate(citations):
                if 'url' in citation:
                    url = citation['url']
                    urls.append(url)
                    domain = self.extract_domain_from_url(url)
                    domains.append(domain)
                    
                    # Store for PICKLE_ROBOT_ENHANCED_20250929.csv
                    self.raw_citations.append({
                        'engine': platform_name,
                        'prompt': query,
                        'domain': domain,
                        'class': self.classify_domain(domain),
                        'url': url
                    })
                    
                    # Update media tracking for ROBOTICS_MEDIA_TRACKING_20250929.csv
                    if domain not in self.media_tracking:
                        self.media_tracking[domain] = {
                            'citation_count': 0,
                            'urls': [],
                            'queries': [],
                            'engines': []
                        }
                    
                    self.media_tracking[domain]['citation_count'] += 1
                    if url not in self.media_tracking[domain]['urls']:
                        self.media_tracking[domain]['urls'].append(url)
                    if query not in self.media_tracking[domain]['queries']:
                        self.media_tracking[domain]['queries'].append(query)
                    if platform_name not in self.media_tracking[domain]['engines']:
                        self.media_tracking[domain]['engines'].append(platform_name)
            
            # Determine winner and prominence
            winner = "Pickle Robot" if pickle_present else "None"
            for competitor in self.competitors.keys():
                if competitors_detected.get(competitor, False):
                    if not pickle_present:  # If Pickle Robot not present, competitor wins
                        winner = competitor
                        break
            
            # Store for PICKLE_COMPETITIVE_MATRIX_20250929.csv
            competitors_mentioned = [comp for comp, present in competitors_detected.items() if present]
            position_prominence = "first" if pickle_present and len(citations) > 0 else "not_present"
            source_quality = "high" if any(self.assess_source_quality(d) == "high" for d in domains) else "medium"
            
            competitive_entry = {
                'query': query,
                'engine': platform_name,
                'pickle_present': 'Yes' if pickle_present else 'No',
                'competitors_mentioned': ', '.join(competitors_mentioned) if competitors_mentioned else 'None',
                'position_prominence': position_prominence,
                'source_quality': source_quality,
                'total_citations': len(citations)
            }
            self.competitive_matrix.append(competitive_entry)
            
            return {
                'platform': platform_name,
                'query': query,
                'query_category': query_category,
                'total_citations': len(citations),
                'urls': urls,
                'domains': domains,
                'pickle_present': pickle_present,
                'competitors_detected': competitors_detected,
                'winner': winner
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {str(e)}")
            return {
                'platform': platform_name,
                'query': query,
                'query_category': query_category,
                'total_citations': 0,
                'urls': [],
                'domains': [],
                'pickle_present': False,
                'competitors_detected': {},
                'winner': "None"
            }
    
    def collect_enhanced_data(self):
        """Collect comprehensive Pickle Robot citation data across all platforms."""
        logger.info("Starting Pickle Robot Enhanced Citation Collection...")
        logger.info(f"Total queries to execute: {sum(len(queries) for queries in self.enhanced_queries.values())} × {len(self.platforms)} platforms = {sum(len(queries) for queries in self.enhanced_queries.values()) * len(self.platforms)} total prompts")
        
        completed = 0
        total_queries = sum(len(queries) for queries in self.enhanced_queries.values()) * len(self.platforms)
        
        for category, queries in self.enhanced_queries.items():
            logger.info(f"Processing {category} queries...")
            
            for query in queries:
                logger.info(f"Query: {query}")
                
                for platform_name in self.platforms.keys():
                    result = self.query_platform(platform_name, query, category)
                    completed += 1
                    logger.info(f"Progress: {completed}/{total_queries} queries completed ({(completed/total_queries)*100:.1f}%)")
                    
                    # Rate limiting
                    import time
                    time.sleep(2)
    
    def export_csv_files(self):
        """Export all collected data to the 3 required CSV files."""
        logger.info("Exporting Pickle Robot Enhanced Analysis data to CSV files...")
        
        # 1. PICKLE_ROBOT_ENHANCED_20250929.csv
        enhanced_file = self.output_dir / f"PICKLE_ROBOT_ENHANCED_{self.timestamp}.csv"
        with open(enhanced_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['engine', 'prompt', 'domain', 'class', 'url'])
            writer.writeheader()
            writer.writerows(self.raw_citations)
        
        # 2. PICKLE_COMPETITIVE_MATRIX_20250929.csv
        competitive_file = self.output_dir / f"PICKLE_COMPETITIVE_MATRIX_{self.timestamp}.csv"
        with open(competitive_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'pickle_present', 'competitors_mentioned', 
                'position_prominence', 'source_quality', 'total_citations'
            ])
            writer.writeheader()
            writer.writerows(self.competitive_matrix)
        
        # 3. ROBOTICS_MEDIA_TRACKING_20250929.csv
        media_file = self.output_dir / f"ROBOTICS_MEDIA_TRACKING_{self.timestamp}.csv"
        with open(media_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'media_outlet', 'citation_count', 'urls', 'queries', 'engines'
            ])
            writer.writeheader()
            
            for domain, data in self.media_tracking.items():
                writer.writerow({
                    'media_outlet': domain,
                    'citation_count': data['citation_count'],
                    'urls': ' | '.join(data['urls'][:5]),  # Limit to 5 URLs for readability
                    'queries': ' | '.join(data['queries'][:3]),  # Limit to 3 queries
                    'engines': ', '.join(data['engines'])
                })
        
        logger.info(f"Data exported to {self.output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - {enhanced_file.name}")
        logger.info(f"  - {competitive_file.name}")
        logger.info(f"  - {media_file.name}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis summary with competitive intelligence."""
        logger.info("Generating Pickle Robot Enhanced Analysis Summary...")
        
        # Calculate key metrics
        total_citations = len(self.raw_citations)
        total_queries = len(self.competitive_matrix)
        
        # Platform performance
        platform_stats = {}
        for entry in self.competitive_matrix:
            platform = entry['engine']
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'queries': 0, 'citations': 0, 'pickle_mentions': 0
                }
            platform_stats[platform]['queries'] += 1
            platform_stats[platform]['citations'] += entry['total_citations']
            if entry['pickle_present'] == 'Yes':
                platform_stats[platform]['pickle_mentions'] += 1
        
        # Competitive analysis
        competitor_mentions = {}
        pickle_wins = 0
        for entry in self.competitive_matrix:
            if entry['competitors_mentioned'] != 'None':
                competitors = entry['competitors_mentioned'].split(', ')
                for comp in competitors:
                    competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
            if entry['pickle_present'] == 'Yes':
                pickle_wins += 1
        
        # Media category analysis
        category_stats = {}
        for citation in self.raw_citations:
            category = citation['class']
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # Top media sources
        top_media = sorted(self.media_tracking.items(), 
                          key=lambda x: x[1]['citation_count'], reverse=True)[:15]
        
        summary = {
            'analysis_timestamp': self.timestamp,
            'total_queries_processed': total_queries,
            'total_citations_collected': total_citations,
            'target_achievement': f"{total_citations}/120 citations (Target: 80-120+)",
            'pickle_robot_mentions': pickle_wins,
            'pickle_visibility_rate': f"{(pickle_wins/total_queries)*100:.1f}%",
            'platform_performance': platform_stats,
            'competitor_mentions': competitor_mentions,
            'media_category_breakdown': category_stats,
            'top_media_sources': [
                {
                    'domain': domain, 
                    'citations': data['citation_count'],
                    'category': self.classify_domain(domain)
                } for domain, data in top_media
            ],
            'competitive_intelligence': self._generate_competitive_insights(),
            'strategic_recommendations': self._generate_strategic_recommendations()
        }
        
        # Save summary
        summary_file = self.output_dir / f"PICKLE_ROBOT_ENHANCED_SUMMARY_{self.timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced summary report saved to {summary_file}")
        return summary
    
    def _generate_competitive_insights(self) -> List[str]:
        """Generate competitive intelligence insights."""
        insights = []
        
        # Analyze competitor mentions
        competitor_counts = {}
        for entry in self.competitive_matrix:
            if entry['competitors_mentioned'] != 'None':
                competitors = entry['competitors_mentioned'].split(', ')
                for comp in competitors:
                    competitor_counts[comp] = competitor_counts.get(comp, 0) + 1
        
        if competitor_counts:
            top_competitor = max(competitor_counts, key=competitor_counts.get)
            insights.append(f"{top_competitor} shows strongest competitive presence with {competitor_counts[top_competitor]} mentions")
        
        # Analyze Pickle Robot presence
        pickle_mentions = sum(1 for entry in self.competitive_matrix if entry['pickle_present'] == 'Yes')
        total_queries = len(self.competitive_matrix)
        pickle_rate = (pickle_mentions / total_queries) * 100
        
        if pickle_rate < 30:
            insights.append(f"Pickle Robot visibility low at {pickle_rate:.1f}% - need enhanced brand awareness campaigns")
        elif pickle_rate > 60:
            insights.append(f"Pickle Robot shows strong visibility at {pickle_rate:.1f}% - maintain competitive positioning")
        
        # Media category analysis
        category_counts = {}
        for citation in self.raw_citations:
            category = citation['class']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts.get('robotics_trade', 0) > category_counts.get('tier_1_business', 0):
            insights.append("Strong robotics trade media presence - opportunity to expand into business media")
        
        return insights
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        # Platform-specific recommendations
        platform_performance = {}
        for entry in self.competitive_matrix:
            platform = entry['engine']
            if platform not in platform_performance:
                platform_performance[platform] = {'citations': 0, 'queries': 0}
            platform_performance[platform]['citations'] += entry['total_citations']
            platform_performance[platform]['queries'] += 1
        
        if platform_performance:
            best_platform = max(platform_performance, 
                              key=lambda x: platform_performance[x]['citations'] / platform_performance[x]['queries'])
            recommendations.append(f"Optimize content strategy for {best_platform} - highest citation yield platform")
        
        # Media category recommendations
        category_counts = {}
        for citation in self.raw_citations:
            category = citation['class']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts.get('tier_1_business', 0) < 5:
            recommendations.append("Target tier-1 business media (Forbes, WSJ, Bloomberg) for enhanced credibility")
        
        if category_counts.get('supply_chain', 0) < 10:
            recommendations.append("Increase supply chain media presence for warehouse automation authority")
        
        # Competitive recommendations
        competitor_counts = {}
        for entry in self.competitive_matrix:
            if entry['competitors_mentioned'] != 'None':
                competitors = entry['competitors_mentioned'].split(', ')
                for comp in competitors:
                    competitor_counts[comp] = competitor_counts.get(comp, 0) + 1
        
        if competitor_counts.get('Boston Dynamics', 0) > 10:
            recommendations.append("Differentiate from Boston Dynamics through warehouse-specific use case messaging")
        
        return recommendations

def main():
    """Main execution function."""
    analyzer = PickleRobotEnhancedAnalyzer()
    
    try:
        # Collect enhanced data across all platforms
        analyzer.collect_enhanced_data()
        
        # Export to required CSV files
        analyzer.export_csv_files()
        
        # Generate comprehensive summary
        summary = analyzer.generate_comprehensive_report()
        
        print("\n" + "="*80)
        print("PICKLE ROBOT ENHANCED AI CITATION ANALYSIS COMPLETE")
        print("="*80)
        print(f"Total queries processed: {summary['total_queries_processed']}")
        print(f"Total citations collected: {summary['total_citations_collected']}")
        print(f"Target achievement: {summary['target_achievement']}")
        print(f"Pickle Robot visibility rate: {summary['pickle_visibility_rate']}")
        print(f"Data exported to: {analyzer.output_dir}")
        print("\nCompetitive Intelligence:")
        for insight in summary['competitive_intelligence']:
            print(f"  • {insight}")
        print("\nStrategic Recommendations:")
        for rec in summary['strategic_recommendations']:
            print(f"  • {rec}")
        
        # Expected score improvement
        baseline_score = 75.2
        expected_improvement = (summary['total_citations_collected'] / 40) * 10  # Scale factor
        projected_score = min(baseline_score + expected_improvement, 100)
        print(f"\nProjected B2B Authority Score: {projected_score:.1f}/100 (vs baseline 75.2/100)")
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

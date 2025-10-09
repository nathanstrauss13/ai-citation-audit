#!/usr/bin/env python3
"""
Hims & Hers AI Citation Analysis - Telehealth Media Influence Study
Focuses on Hims & Hers visibility in telehealth and direct-to-consumer healthcare
across AI platforms, including regulatory and competitive analysis.
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

class HimsHersHealthcareAnalyzer:
    """Analyzes Hims & Hers citation visibility and media influence in telehealth space."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.output_dir = Path("case_studies/hims_hers_analysis")
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
        
        # Hims & Hers telehealth queries (15 total)
        self.telehealth_queries = [
            # Telehealth & Service Queries (8)
            "Best online doctor consultation platforms",
            "How to get prescription medication online",
            "Hims vs Roman vs Lemonaid comparison",
            "Telehealth for men's health issues",
            "Online therapy and mental health services",
            "How does Hims and Hers work?",
            "Cost of telehealth consultations",
            "Is online prescription medication safe?",
            
            # Condition-Specific Queries (4)
            "Online treatment for hair loss",
            "Telehealth for anxiety and depression",
            "Online ED treatment options",
            "Birth control online prescription",
            
            # Brand & Business Queries (3)
            "Hims and Hers reviews and ratings",
            "Who owns Hims and Hers?",
            "Hims and Hers vs traditional healthcare"
        ]
        
        # Target media domains for detailed tracking
        self.target_domains = {
            'hims.com': 'official_hims_hers',
            'forhims.com': 'official_hims_hers',
            'forhers.com': 'official_hims_hers',
            'healthline.com': 'medical_authority',
            'webmd.com': 'medical_authority',
            'mayoclinic.org': 'medical_authority',
            'forbes.com': 'consumer_media',
            'techcrunch.com': 'tech_media',
            'businessinsider.com': 'consumer_media',
            'reddit.com': 'social_community',
            'trustpilot.com': 'review_platform',
            'consumerreports.org': 'review_platform',
            'fda.gov': 'regulatory',
            'nytimes.com': 'consumer_media',
            'wsj.com': 'consumer_media',
            'medicalnewstoday.com': 'medical_authority',
            'goodrx.com': 'healthcare_platform',
            'roman.co': 'competitor',
            'lemonaidhealth.com': 'competitor',
            'ro.co': 'competitor',
            'keeps.com': 'competitor',
            'curology.com': 'competitor'
        }
        
        # Competitor patterns for tracking
        self.competitor_patterns = {
            'Roman': [r'\broman\b', r'ro\.co', r'getroman'],
            'Lemonaid': [r'lemonaid', r'lemonaidhealth'],
            'Keeps': [r'\bkeeps\b', r'keeps\.com'],
            'Curology': [r'curology', r'curology\.com'],
            'Teladoc': [r'teladoc', r'teladoc\.com'],
            'Amwell': [r'amwell', r'amwell\.com']
        }
        
        # Sentiment patterns for analysis
        self.sentiment_patterns = {
            'positive': [r'effective', r'convenient', r'affordable', r'recommended', r'trusted', r'reliable'],
            'negative': [r'scam', r'dangerous', r'unsafe', r'overpriced', r'ineffective', r'warning'],
            'cautionary': [r'consult.*doctor', r'side effects', r'risks', r'fda.*warning', r'not.*substitute']
        }
        
        # Data storage
        self.visibility_data = []
        self.media_influence_data = {}
        self.competitor_data = []
        
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
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
        for competitor, patterns in self.competitor_patterns.items():
            detected[competitor] = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
        return detected
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the text regarding telehealth/Hims & Hers."""
        text_lower = text.lower()
        
        positive_count = sum(1 for pattern in self.sentiment_patterns['positive'] 
                           if re.search(pattern, text_lower))
        negative_count = sum(1 for pattern in self.sentiment_patterns['negative'] 
                           if re.search(pattern, text_lower))
        cautionary_count = sum(1 for pattern in self.sentiment_patterns['cautionary'] 
                             if re.search(pattern, text_lower))
        
        if cautionary_count > 0:
            return 'cautionary'
        elif negative_count > positive_count:
            return 'negative'
        elif positive_count > 0:
            return 'positive'
        else:
            return 'neutral'
    
    def detect_regulatory_mentions(self, text: str) -> bool:
        """Detect if regulatory concerns or FDA mentions are present."""
        regulatory_patterns = [r'fda', r'regulation', r'prescription.*required', r'licensed.*doctor', r'medical.*board']
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in regulatory_patterns)
    
    def determine_winner(self, competitors_present: Dict[str, bool]) -> str:
        """Determine which competitor is presented most favorably."""
        # Simple heuristic: first mentioned competitor
        for competitor in ['Hims', 'Roman', 'Lemonaid', 'Keeps', 'Curology']:
            if competitors_present.get(competitor, False):
                return competitor
        return "None"
    
    def query_platform(self, platform_name: str, query: str) -> Dict:
        """Query a specific platform with enhanced telehealth citation tracking."""
        logger.info(f"Querying {platform_name}: {query[:50]}...")
        
        try:
            platform = self.platforms[platform_name]
            
            # Enhanced prompt for telehealth queries
            enhanced_query = f"""Please provide comprehensive information about: {query}

Include specific sources, citations, URLs, and references. Focus on authoritative medical sources, telehealth platforms, regulatory information, and current healthcare data. Provide direct links to relevant content when possible."""
            
            # Get citations from platform
            citations = platform.get_citations(enhanced_query)
            
            # Process citations with detailed telehealth-specific analysis
            urls = []
            domains = []
            top_3_domains = []
            
            # Track specific domain presence
            domain_presence = {
                'hims_com_present': False,
                'forhims_present': False,
                'forhers_present': False,
                'roman_present': False,
                'lemonaid_present': False,
                'healthline_present': False,
                'webmd_present': False
            }
            
            # Category counters
            category_counts = {
                'medical_journal_count': 0,
                'consumer_media_count': 0,
                'tech_media_count': 0,
                'reddit_count': 0
            }
            
            # Analyze full response text for sentiment and competitors
            response_text = " ".join([query] + [citation.get('url', '') for citation in citations])
            competitors_detected = self.detect_competitors(response_text)
            overall_sentiment = self.analyze_sentiment(response_text)
            regulatory_mentioned = self.detect_regulatory_mentions(response_text)
            
            for i, citation in enumerate(citations):
                if 'url' in citation:
                    url = citation['url']
                    urls.append(url)
                    domain = self.extract_domain_from_url(url)
                    domains.append(domain)
                    
                    # Track top 3 domains
                    if i < 3:
                        top_3_domains.append(domain)
                    
                    # Check for specific domain presence
                    if 'hims.com' in domain:
                        domain_presence['hims_com_present'] = True
                    elif 'forhims.com' in domain:
                        domain_presence['forhims_present'] = True
                    elif 'forhers.com' in domain:
                        domain_presence['forhers_present'] = True
                    elif 'roman.co' in domain or 'getroman' in domain:
                        domain_presence['roman_present'] = True
                    elif 'lemonaid' in domain:
                        domain_presence['lemonaid_present'] = True
                    elif 'healthline.com' in domain:
                        domain_presence['healthline_present'] = True
                    elif 'webmd.com' in domain:
                        domain_presence['webmd_present'] = True
                    
                    # Classify by category
                    domain_category = self.classify_domain(domain)
                    if domain_category == 'medical_authority':
                        category_counts['medical_journal_count'] += 1
                    elif domain_category == 'consumer_media':
                        category_counts['consumer_media_count'] += 1
                    elif domain_category == 'tech_media':
                        category_counts['tech_media_count'] += 1
                    elif 'reddit.com' in domain:
                        category_counts['reddit_count'] += 1
                    
                    # Update media influence tracking
                    if domain not in self.media_influence_data:
                        self.media_influence_data[domain] = {
                            'total_citations': 0,
                            'content_category': self.classify_domain(domain),
                            'sentiment_scores': {'positive': 0, 'negative': 0, 'neutral': 0, 'cautionary': 0},
                            'primary_topics': [],
                            'regulatory_mentioned': False,
                            'sample_urls': []
                        }
                    
                    self.media_influence_data[domain]['total_citations'] += 1
                    self.media_influence_data[domain]['sentiment_scores'][overall_sentiment] += 1
                    
                    if regulatory_mentioned:
                        self.media_influence_data[domain]['regulatory_mentioned'] = True
                    
                    # Store sample URLs (max 3 per domain)
                    if len(self.media_influence_data[domain]['sample_urls']) < 3:
                        self.media_influence_data[domain]['sample_urls'].append(url)
                    
                    # Add query as topic context
                    if query not in self.media_influence_data[domain]['primary_topics']:
                        self.media_influence_data[domain]['primary_topics'].append(query)
            
            # Store competitor analysis
            winner = self.determine_winner(competitors_detected)
            competitor_result = {
                'query': query,
                'engine': platform_name,
                'hims_hers_present': 'Yes' if any(['hims' in response_text.lower(), 'forhims' in response_text.lower(), 'forhers' in response_text.lower()]) else 'No',
                'roman_present': 'Yes' if competitors_detected.get('Roman', False) else 'No',
                'lemonaid_present': 'Yes' if competitors_detected.get('Lemonaid', False) else 'No',
                'keeps_present': 'Yes' if competitors_detected.get('Keeps', False) else 'No',
                'curology_present': 'Yes' if competitors_detected.get('Curology', False) else 'No',
                'winner': winner,
                'citation_tone': overall_sentiment
            }
            self.competitor_data.append(competitor_result)
            
            return {
                'platform': platform_name,
                'query': query,
                'total_citations': len(citations),
                'urls': urls,
                'domains': domains,
                'top_3_domains': top_3_domains[:3],
                **domain_presence,
                **category_counts
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {str(e)}")
            return {
                'platform': platform_name,
                'query': query,
                'total_citations': 0,
                'urls': [],
                'domains': [],
                'top_3_domains': [],
                'hims_com_present': False,
                'forhims_present': False,
                'forhers_present': False,
                'roman_present': False,
                'lemonaid_present': False,
                'healthline_present': False,
                'webmd_present': False,
                'medical_journal_count': 0,
                'consumer_media_count': 0,
                'tech_media_count': 0,
                'reddit_count': 0
            }
    
    def collect_telehealth_data(self):
        """Collect Hims & Hers telehealth citation data across all platforms."""
        logger.info("Starting Hims & Hers telehealth citation collection...")
        
        total_queries = len(self.telehealth_queries) * len(self.platforms)
        completed = 0
        
        for query in self.telehealth_queries:
            logger.info(f"Processing telehealth query: {query}")
            
            for platform_name in self.platforms.keys():
                result = self.query_platform(platform_name, query)
                self.visibility_data.append(result)
                completed += 1
                logger.info(f"Telehealth Progress: {completed}/{total_queries} queries completed")
                
                # Rate limiting
                import time
                time.sleep(3)
    
    def export_csv_files(self):
        """Export all collected data to CSV files."""
        logger.info("Exporting Hims & Hers analysis data to CSV files...")
        
        # 1. Hims & Hers Visibility Matrix
        visibility_file = self.output_dir / f"HIMS_HERS_VISIBILITY_MATRIX_{self.timestamp}.csv"
        with open(visibility_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'total_citations', 'top_3_domains',
                'hims_com_present', 'forhims_present', 'forhers_present', 
                'roman_present', 'lemonaid_present', 'healthline_present', 'webmd_present',
                'medical_journal_count', 'consumer_media_count', 'tech_media_count', 
                'reddit_count', 'urls'
            ])
            writer.writeheader()
            
            for row in self.visibility_data:
                writer.writerow({
                    'query': row['query'],
                    'engine': row['platform'],
                    'total_citations': row['total_citations'],
                    'top_3_domains': ', '.join(row['top_3_domains']),
                    'hims_com_present': 'Yes' if row['hims_com_present'] else 'No',
                    'forhims_present': 'Yes' if row['forhims_present'] else 'No',
                    'forhers_present': 'Yes' if row['forhers_present'] else 'No',
                    'roman_present': 'Yes' if row['roman_present'] else 'No',
                    'lemonaid_present': 'Yes' if row['lemonaid_present'] else 'No',
                    'healthline_present': 'Yes' if row['healthline_present'] else 'No',
                    'webmd_present': 'Yes' if row['webmd_present'] else 'No',
                    'medical_journal_count': row['medical_journal_count'],
                    'consumer_media_count': row['consumer_media_count'],
                    'tech_media_count': row['tech_media_count'],
                    'reddit_count': row['reddit_count'],
                    'urls': ' | '.join(row['urls'])
                })
        
        # 2. Media Influence Analysis
        influence_file = self.output_dir / f"MEDIA_INFLUENCE_{self.timestamp}.csv"
        with open(influence_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'media_outlet', 'total_citations', 'content_category', 
                'sentiment_lean', 'primary_topics', 'regulatory_mentioned', 'sample_urls'
            ])
            writer.writeheader()
            
            for domain, data in self.media_influence_data.items():
                # Determine dominant sentiment
                sentiment_scores = data['sentiment_scores']
                dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
                
                writer.writerow({
                    'media_outlet': domain,
                    'total_citations': data['total_citations'],
                    'content_category': data['content_category'],
                    'sentiment_lean': dominant_sentiment,
                    'primary_topics': ' | '.join(data['primary_topics'][:3]),  # Top 3 topics
                    'regulatory_mentioned': 'Yes' if data['regulatory_mentioned'] else 'No',
                    'sample_urls': ' | '.join(data['sample_urls'])
                })
        
        # 3. Competitor Analysis
        competitor_file = self.output_dir / f"COMPETITOR_ANALYSIS_{self.timestamp}.csv"
        with open(competitor_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'hims_hers_present', 'roman_present', 'lemonaid_present', 
                'keeps_present', 'curology_present', 'winner', 'citation_tone'
            ])
            writer.writeheader()
            writer.writerows(self.competitor_data)
        
        logger.info(f"Data exported to {self.output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - {visibility_file.name}")
        logger.info(f"  - {influence_file.name}")
        logger.info(f"  - {competitor_file.name}")
    
    def generate_summary_report(self):
        """Generate comprehensive Hims & Hers analysis summary."""
        logger.info("Generating Hims & Hers analysis summary...")
        
        # Calculate key metrics
        total_queries = len(self.visibility_data)
        total_citations = sum(d['total_citations'] for d in self.visibility_data)
        hims_official_citations = sum(1 for d in self.visibility_data if d['hims_com_present'] or d['forhims_present'] or d['forhers_present'])
        medical_authority_citations = sum(d['medical_journal_count'] for d in self.visibility_data)
        
        # Top media sources
        top_media = sorted(self.media_influence_data.items(), 
                          key=lambda x: x[1]['total_citations'], reverse=True)[:10]
        
        # Platform performance
        platform_stats = {}
        for data in self.visibility_data:
            platform = data['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'queries': 0, 'citations': 0, 'hims_mentions': 0}
            platform_stats[platform]['queries'] += 1
            platform_stats[platform]['citations'] += data['total_citations']
            if data['hims_com_present'] or data['forhims_present'] or data['forhers_present']:
                platform_stats[platform]['hims_mentions'] += 1
        
        # Competitor analysis
        competitor_wins = {}
        for data in self.competitor_data:
            winner = data['winner']
            competitor_wins[winner] = competitor_wins.get(winner, 0) + 1
        
        summary = {
            'analysis_timestamp': self.timestamp,
            'total_queries_processed': total_queries,
            'total_citations_collected': total_citations,
            'hims_official_percentage': f"{(hims_official_citations/total_queries)*100:.1f}%",
            'medical_authority_percentage': f"{(medical_authority_citations/total_citations)*100:.1f}%" if total_citations > 0 else "0%",
            'top_media_sources': [{'domain': domain, 'citations': data['total_citations'], 'category': data['content_category']} for domain, data in top_media],
            'platform_performance': platform_stats,
            'competitor_wins': competitor_wins,
            'key_insights': self._generate_insights()
        }
        
        # Save summary
        summary_file = self.output_dir / f"HIMS_HERS_ANALYSIS_SUMMARY_{self.timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report saved to {summary_file}")
        return summary
    
    def _generate_insights(self) -> List[str]:
        """Generate strategic insights from the Hims & Hers data."""
        insights = []
        
        # Analyze medical authority vs consumer media balance
        medical_total = sum(d['medical_journal_count'] for d in self.visibility_data)
        consumer_total = sum(d['consumer_media_count'] for d in self.visibility_data)
        
        if medical_total > consumer_total:
            insights.append("Medical authority sources dominate Hims & Hers citations - strong credibility positioning")
        else:
            insights.append("Consumer media coverage opportunity - need stronger medical authority presence")
        
        # Analyze competitor positioning
        competitor_wins = {}
        for data in self.competitor_data:
            winner = data['winner']
            competitor_wins[winner] = competitor_wins.get(winner, 0) + 1
        
        if competitor_wins.get('Roman', 0) > competitor_wins.get('Hims', 0):
            insights.append("Roman shows stronger competitive positioning - need enhanced brand visibility")
        
        # Platform-specific insights
        platform_citations = {}
        for data in self.visibility_data:
            platform = data['platform']
            platform_citations[platform] = platform_citations.get(platform, 0) + data['total_citations']
        
        if platform_citations:
            best_platform = max(platform_citations, key=platform_citations.get)
            insights.append(f"{best_platform} provides the most telehealth citations - prioritize content optimization for this platform")
        
        # Official content analysis
        official_presence = sum(1 for d in self.visibility_data if d['hims_com_present'] or d['forhims_present'] or d['forhers_present'])
        if official_presence < len(self.visibility_data) * 0.3:
            insights.append("Hims & Hers official content has low citation visibility - content strategy optimization needed")
        
        return insights

def main():
    """Main execution function."""
    analyzer = HimsHersHealthcareAnalyzer()
    
    try:
        # Collect telehealth data
        analyzer.collect_telehealth_data()
        
        # Export to CSV files
        analyzer.export_csv_files()
        
        # Generate summary
        summary = analyzer.generate_summary_report()
        
        print("\n" + "="*60)
        print("HIMS & HERS AI CITATION ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total queries processed: {summary['total_queries_processed']}")
        print(f"Total citations collected: {summary['total_citations_collected']}")
        print(f"Hims official percentage: {summary['hims_official_percentage']}")
        print(f"Medical authority percentage: {summary['medical_authority_percentage']}")
        print(f"Data exported to: {analyzer.output_dir}")
        print("\nKey Insights:")
        for insight in summary['key_insights']:
            print(f"  • {insight}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

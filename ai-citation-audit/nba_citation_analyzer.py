#!/usr/bin/env python3
"""
NBA AI Citation Analysis - Media Influence & Visibility Study
Focuses specifically on NBA content visibility across AI platforms
and identifies key media sources driving NBA narrative.
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

class NBAMediaInfluenceAnalyzer:
    """Analyzes NBA citation visibility and media influence across AI platforms."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.output_dir = Path("case_studies/nba_analysis")
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
        
        # NBA-specific queries (Set A)
        self.nba_queries = [
            "How do I watch NBA games online?",
            "Best NBA teams to follow as a new fan",
            "NBA playoff format and schedule",
            "Most exciting NBA players to watch right now",
            "Current NBA championship favorites",
            "NBA MVP candidates this season",
            "How does the NBA draft work?",
            "NBA streaming and League Pass options",
            "NBA trade rumors and news",
            "Best NBA podcasts and media coverage"
        ]
        
        # League-agnostic queries (Set B) for competitive context
        self.competitive_queries = [
            "Most popular professional sports league globally",
            "Which sports league has the best playoffs?",
            "Most innovative professional sports league",
            "Best sports league for international fans",
            "Most watched sports league in America"
        ]
        
        # Target media domains for detailed tracking
        self.target_domains = {
            'nba.com': 'official',
            'espn.com': 'premium_media',
            'theathletic.com': 'premium_media',
            'bleacherreport.com': 'premium_media',
            'sportingnews.com': 'premium_media',
            'cbssports.com': 'premium_media',
            'foxsports.com': 'premium_media',
            'sports.yahoo.com': 'premium_media',
            'reddit.com': 'social_community',
            'youtube.com': 'social_community',
            'twitter.com': 'social_community',
            'x.com': 'social_community',
            'instagram.com': 'social_community',
            'wikipedia.org': 'reference',
            'lakers.com': 'team_official',
            'celtics.com': 'team_official',
            'warriors.com': 'team_official',
            'bulls.com': 'team_official',
            'heat.com': 'team_official',
            'nets.com': 'team_official',
            'knicks.com': 'team_official'
        }
        
        # League patterns for competitive analysis
        self.league_patterns = {
            'NBA': [r'\bNBA\b', r'\bNational Basketball Association\b', r'\bbasketball league\b'],
            'NFL': [r'\bNFL\b', r'\bNational Football League\b', r'\bfootball league\b'],
            'MLB': [r'\bMLB\b', r'\bMajor League Baseball\b', r'\bbaseball league\b'],
            'NHL': [r'\bNHL\b', r'\bNational Hockey League\b', r'\bhockey league\b']
        }
        
        # Data storage
        self.visibility_data = []
        self.media_influence_data = {}
        self.competitive_data = []
        
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
    
    def detect_leagues_in_text(self, text: str) -> Dict[str, bool]:
        """Detect which leagues are mentioned in the text."""
        detected = {}
        for league, patterns in self.league_patterns.items():
            detected[league] = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
        return detected
    
    def determine_winner(self, text: str, leagues_present: Dict[str, bool]) -> str:
        """Determine which league is presented most favorably."""
        text_lower = text.lower()
        positive_indicators = ['most', 'best', 'top', 'leading', 'highest', 'largest', 'biggest', 'popular']
        
        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
            if leagues_present[league]:
                league_pos = text_lower.find(league.lower())
                if league_pos != -1:
                    context_start = max(0, league_pos - 100)
                    context_end = min(len(text), league_pos + 100)
                    context = text_lower[context_start:context_end]
                    
                    if any(indicator in context for indicator in positive_indicators):
                        return league
        
        # Fallback: return first mentioned league
        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
            if leagues_present[league]:
                return league
        return "None"
    
    def query_platform(self, platform_name: str, query: str, query_type: str) -> Dict:
        """Query a specific platform with enhanced citation tracking."""
        logger.info(f"Querying {platform_name}: {query[:50]}...")
        
        try:
            platform = self.platforms[platform_name]
            
            # Enhanced prompt for NBA-specific queries
            if query_type == "nba_specific":
                enhanced_query = f"""Please provide comprehensive information about: {query}

Include specific sources, citations, URLs, and references. Focus on authoritative NBA sources, official content, sports media outlets, and current information. Provide direct links to relevant content when possible."""
            else:
                enhanced_query = f"""Please provide a comprehensive comparison addressing: {query}

Include specific sources, citations, URLs, and references comparing different professional sports leagues. Provide authoritative sources and current information."""
            
            # Get citations from platform
            citations = platform.get_citations(enhanced_query)
            
            # Process citations with detailed analysis
            urls = []
            domains = []
            top_3_domains = []
            official_count = 0
            third_party_count = 0
            
            # Track specific domain presence
            domain_presence = {
                'nba_com_present': False,
                'espn_present': False,
                'athletic_present': False,
                'bleacher_report_present': False
            }
            
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
                    if 'nba.com' in domain:
                        domain_presence['nba_com_present'] = True
                        official_count += 1
                    elif 'espn.com' in domain:
                        domain_presence['espn_present'] = True
                        third_party_count += 1
                    elif 'theathletic.com' in domain:
                        domain_presence['athletic_present'] = True
                        third_party_count += 1
                    elif 'bleacherreport.com' in domain:
                        domain_presence['bleacher_report_present'] = True
                        third_party_count += 1
                    else:
                        # Check if it's any team official site
                        if any(team_domain in domain for team_domain in ['lakers.com', 'celtics.com', 'warriors.com', 'bulls.com', 'heat.com', 'nets.com', 'knicks.com']):
                            official_count += 1
                        else:
                            third_party_count += 1
                    
                    # Update media influence tracking
                    if domain not in self.media_influence_data:
                        self.media_influence_data[domain] = {
                            'total_citations': 0,
                            'nba_specific_citations': 0,
                            'league_agnostic_citations': 0,
                            'positions': [],
                            'primary_content_type': self.classify_domain(domain),
                            'sample_urls': []
                        }
                    
                    self.media_influence_data[domain]['total_citations'] += 1
                    self.media_influence_data[domain]['positions'].append(i + 1)
                    
                    if query_type == "nba_specific":
                        self.media_influence_data[domain]['nba_specific_citations'] += 1
                    else:
                        self.media_influence_data[domain]['league_agnostic_citations'] += 1
                    
                    # Store sample URLs (max 3 per domain)
                    if len(self.media_influence_data[domain]['sample_urls']) < 3:
                        self.media_influence_data[domain]['sample_urls'].append(url)
            
            return {
                'platform': platform_name,
                'query': query,
                'query_type': query_type,
                'total_citations': len(citations),
                'urls': urls,
                'domains': domains,
                'top_3_domains': top_3_domains[:3],
                'official_count': official_count,
                'third_party_count': third_party_count,
                **domain_presence
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {str(e)}")
            return {
                'platform': platform_name,
                'query': query,
                'query_type': query_type,
                'total_citations': 0,
                'urls': [],
                'domains': [],
                'top_3_domains': [],
                'official_count': 0,
                'third_party_count': 0,
                'nba_com_present': False,
                'espn_present': False,
                'athletic_present': False,
                'bleacher_report_present': False
            }
    
    def collect_nba_data(self):
        """Collect NBA-specific citation data."""
        logger.info("Starting NBA-specific citation collection...")
        
        total_queries = len(self.nba_queries) * len(self.platforms)
        completed = 0
        
        for query in self.nba_queries:
            logger.info(f"Processing NBA query: {query}")
            
            for platform_name in self.platforms.keys():
                result = self.query_platform(platform_name, query, "nba_specific")
                self.visibility_data.append(result)
                completed += 1
                logger.info(f"NBA Progress: {completed}/{total_queries} queries completed")
                
                # Rate limiting
                import time
                time.sleep(3)
    
    def collect_competitive_data(self):
        """Collect competitive context data."""
        logger.info("Starting competitive context collection...")
        
        total_queries = len(self.competitive_queries) * len(self.platforms)
        completed = 0
        
        for query in self.competitive_queries:
            logger.info(f"Processing competitive query: {query}")
            
            for platform_name in self.platforms.keys():
                result = self.query_platform(platform_name, query, "league_agnostic")
                
                # For competitive queries, also analyze league presence
                response_text = " ".join([url for url in result['urls']])  # Simple text from URLs
                leagues_present = self.detect_leagues_in_text(query + " " + response_text)
                winner = self.determine_winner(query + " " + response_text, leagues_present)
                
                competitive_result = {
                    'query': query,
                    'engine': platform_name,
                    'nba_present': 'Yes' if leagues_present['NBA'] else 'No',
                    'nfl_present': 'Yes' if leagues_present['NFL'] else 'No',
                    'mlb_present': 'Yes' if leagues_present['MLB'] else 'No',
                    'nhl_present': 'Yes' if leagues_present['NHL'] else 'No',
                    'winner': winner,
                    'nba_citation_count': result['total_citations'] if 'nba' in query.lower() else 0
                }
                
                self.competitive_data.append(competitive_result)
                completed += 1
                logger.info(f"Competitive Progress: {completed}/{total_queries} queries completed")
                
                # Rate limiting
                import time
                time.sleep(3)
    
    def export_csv_files(self):
        """Export all collected data to CSV files."""
        logger.info("Exporting NBA analysis data to CSV files...")
        
        # 1. NBA Visibility Matrix
        visibility_file = self.output_dir / f"NBA_VISIBILITY_MATRIX_{self.timestamp}.csv"
        with open(visibility_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'query_type', 'engine', 'total_citations', 'top_3_domains',
                'nba_com_present', 'espn_present', 'athletic_present', 'bleacher_report_present',
                'official_content_count', 'third_party_count', 'urls'
            ])
            writer.writeheader()
            
            for row in self.visibility_data:
                writer.writerow({
                    'query': row['query'],
                    'query_type': row['query_type'],
                    'engine': row['platform'],
                    'total_citations': row['total_citations'],
                    'top_3_domains': ', '.join(row['top_3_domains']),
                    'nba_com_present': 'Yes' if row['nba_com_present'] else 'No',
                    'espn_present': 'Yes' if row['espn_present'] else 'No',
                    'athletic_present': 'Yes' if row['athletic_present'] else 'No',
                    'bleacher_report_present': 'Yes' if row['bleacher_report_present'] else 'No',
                    'official_content_count': row['official_count'],
                    'third_party_count': row['third_party_count'],
                    'urls': ' | '.join(row['urls'])
                })
        
        # 2. Media Influence Analysis
        influence_file = self.output_dir / f"MEDIA_INFLUENCE_{self.timestamp}.csv"
        with open(influence_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'media_outlet', 'total_citations', 'nba_specific_citations', 
                'league_agnostic_citations', 'avg_position', 'primary_content_type', 'sample_urls'
            ])
            writer.writeheader()
            
            for domain, data in self.media_influence_data.items():
                avg_position = sum(data['positions']) / len(data['positions']) if data['positions'] else 0
                
                writer.writerow({
                    'media_outlet': domain,
                    'total_citations': data['total_citations'],
                    'nba_specific_citations': data['nba_specific_citations'],
                    'league_agnostic_citations': data['league_agnostic_citations'],
                    'avg_position': round(avg_position, 2),
                    'primary_content_type': data['primary_content_type'],
                    'sample_urls': ' | '.join(data['sample_urls'])
                })
        
        # 3. Competitive Context
        competitive_file = self.output_dir / f"COMPETITIVE_CONTEXT_{self.timestamp}.csv"
        with open(competitive_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'nba_present', 'nfl_present', 'mlb_present', 
                'nhl_present', 'winner', 'nba_citation_count'
            ])
            writer.writeheader()
            writer.writerows(self.competitive_data)
        
        logger.info(f"Data exported to {self.output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - {visibility_file.name}")
        logger.info(f"  - {influence_file.name}")
        logger.info(f"  - {competitive_file.name}")
    
    def generate_summary_report(self):
        """Generate comprehensive NBA analysis summary."""
        logger.info("Generating NBA analysis summary...")
        
        # Calculate key metrics
        total_nba_queries = len([d for d in self.visibility_data if d['query_type'] == 'nba_specific'])
        total_citations = sum(d['total_citations'] for d in self.visibility_data)
        official_citations = sum(d['official_count'] for d in self.visibility_data)
        
        # Top media sources
        top_media = sorted(self.media_influence_data.items(), 
                          key=lambda x: x[1]['total_citations'], reverse=True)[:10]
        
        # Platform performance
        platform_stats = {}
        for data in self.visibility_data:
            platform = data['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'queries': 0, 'citations': 0}
            platform_stats[platform]['queries'] += 1
            platform_stats[platform]['citations'] += data['total_citations']
        
        summary = {
            'analysis_timestamp': self.timestamp,
            'total_nba_queries_processed': total_nba_queries,
            'total_citations_collected': total_citations,
            'official_content_percentage': f"{(official_citations/total_citations)*100:.1f}%" if total_citations > 0 else "0%",
            'top_media_sources': [{'domain': domain, 'citations': data['total_citations']} for domain, data in top_media],
            'platform_performance': platform_stats,
            'key_insights': self._generate_insights()
        }
        
        # Save summary
        summary_file = self.output_dir / f"NBA_ANALYSIS_SUMMARY_{self.timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report saved to {summary_file}")
        return summary
    
    def _generate_insights(self) -> List[str]:
        """Generate strategic insights from the data."""
        insights = []
        
        # Analyze official vs third-party content ratio
        total_official = sum(d['official_count'] for d in self.visibility_data)
        total_third_party = sum(d['third_party_count'] for d in self.visibility_data)
        
        if total_official < total_third_party:
            insights.append("Third-party content dominates NBA citations - opportunity to increase official NBA.com presence")
        
        # Analyze top media sources
        if 'espn.com' in self.media_influence_data and self.media_influence_data['espn.com']['total_citations'] > 10:
            insights.append("ESPN is a dominant source for NBA content - strong media partnership")
        
        if 'nba.com' not in self.media_influence_data or self.media_influence_data.get('nba.com', {}).get('total_citations', 0) < 5:
            insights.append("NBA.com has low citation visibility - content strategy optimization needed")
        
        # Platform-specific insights
        platform_citations = {}
        for data in self.visibility_data:
            platform = data['platform']
            platform_citations[platform] = platform_citations.get(platform, 0) + data['total_citations']
        
        best_platform = max(platform_citations, key=platform_citations.get)
        insights.append(f"{best_platform} provides the most NBA citations - prioritize content optimization for this platform")
        
        return insights

def main():
    """Main execution function."""
    analyzer = NBAMediaInfluenceAnalyzer()
    
    try:
        # Collect NBA-specific data
        analyzer.collect_nba_data()
        
        # Collect competitive context data
        analyzer.collect_competitive_data()
        
        # Export to CSV files
        analyzer.export_csv_files()
        
        # Generate summary
        summary = analyzer.generate_summary_report()
        
        print("\n" + "="*60)
        print("NBA AI CITATION ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total NBA queries processed: {summary['total_nba_queries_processed']}")
        print(f"Total citations collected: {summary['total_citations_collected']}")
        print(f"Official content percentage: {summary['official_content_percentage']}")
        print(f"Data exported to: {analyzer.output_dir}")
        print("\nKey Insights:")
        for insight in summary['key_insights']:
            print(f"  • {insight}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

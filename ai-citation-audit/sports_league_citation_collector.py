#!/usr/bin/env python3
"""
Sports League AI Citation Data Collector
Systematically tests 20 league-agnostic queries across 4 AI platforms
to analyze NBA vs NFL, MLB, NHL citation visibility.
"""

import asyncio
import csv
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
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

class SportsLeagueCitationCollector:
    """Collects and analyzes sports league citations across AI platforms."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.output_dir = Path("case_studies/sports_leagues")
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
        
        # Sports league queries
        self.queries = [
            "What is the most popular professional sports league in America?",
            "Which sports league has the highest average player salaries?",
            "Best professional sports league to watch for beginners",
            "Which sports league has the most international reach?",
            "Most profitable sports league in the world",
            "Which sports league has the best playoffs format?",
            "Most exciting professional sports league to watch",
            "Which sports league has the most parity and competitive balance?",
            "Best sports league for family entertainment",
            "Which professional sports league has the longest season?",
            "Most athlete-friendly professional sports league",
            "Which sports league has the best fan experience?",
            "Most innovative professional sports league",
            "Which sports league has the best social media presence?",
            "Most watched sports league globally",
            "Which sports league sells the most merchandise?",
            "Most valuable sports league franchises",
            "Best sports league for player marketing and endorsements",
            "Most technologically advanced sports league",
            "Which sports league has the best streaming and digital experience?"
        ]
        
        # Target media domains to track
        self.target_domains = [
            'espn.com', 'bleacherreport.com', 'si.com', 'theathletic.com',
            'foxsports.com', 'cbssports.com', 'nbcsports.com', 'sportingnews.com',
            'sports.yahoo.com', 'reddit.com', 'nba.com', 'nfl.com', 'mlb.com', 'nhl.com',
            'forbes.com', 'cnn.com', 'reuters.com', 'ap.org', 'usatoday.com'
        ]
        
        # League patterns for detection
        self.league_patterns = {
            'NBA': [r'\bNBA\b', r'\bNational Basketball Association\b', r'\bbasketball league\b'],
            'NFL': [r'\bNFL\b', r'\bNational Football League\b', r'\bfootball league\b'],
            'MLB': [r'\bMLB\b', r'\bMajor League Baseball\b', r'\bbaseball league\b'],
            'NHL': [r'\bNHL\b', r'\bNational Hockey League\b', r'\bhockey league\b']
        }
        
        # Data storage
        self.query_matrix_data = []
        self.raw_citations_data = []
        self.media_tracking_data = {}
        self.head_to_head_data = []
        
    def extract_urls_from_response(self, response_text: str) -> List[str]:
        """Extract URLs from AI response text."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
        urls = re.findall(url_pattern, response_text)
        return [url.strip() for url in urls]
    
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
    
    def detect_leagues_in_text(self, text: str) -> Dict[str, bool]:
        """Detect which leagues are mentioned in the text."""
        text_lower = text.lower()
        detected = {}
        
        for league, patterns in self.league_patterns.items():
            detected[league] = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
            
        return detected
    
    def analyze_position_prominence(self, text: str, league: str) -> str:
        """Analyze how prominently a league is positioned in the response."""
        if not self.detect_leagues_in_text(text)[league]:
            return "Not Present"
            
        text_lower = text.lower()
        league_lower = league.lower()
        
        # Find first mention position
        first_mention = text_lower.find(league_lower)
        text_length = len(text)
        
        if first_mention < text_length * 0.2:  # First 20% of text
            return "High"
        elif first_mention < text_length * 0.6:  # First 60% of text
            return "Medium"
        else:
            return "Low"
    
    def determine_winner(self, text: str, leagues_present: Dict[str, bool]) -> str:
        """Determine which league is presented most favorably."""
        # Simple heuristic: first mentioned league with positive context
        text_lower = text.lower()
        
        # Look for superlative indicators
        positive_indicators = ['most', 'best', 'top', 'leading', 'highest', 'largest', 'biggest']
        
        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
            if leagues_present[league]:
                league_pos = text_lower.find(league.lower())
                if league_pos != -1:
                    # Check for positive indicators near the league mention
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
    
    def query_platform(self, platform_name: str, query: str) -> Dict:
        """Query a specific platform with a sports league question."""
        logger.info(f"Querying {platform_name}: {query[:50]}...")
        
        try:
            platform = self.platforms[platform_name]
            
            # Enhanced prompt to encourage citation-rich responses
            enhanced_query = f"""Please provide a comprehensive response about: {query}

Include specific sources, citations, URLs, and references where possible. Mention publication names, websites, and authoritative sources when discussing sports leagues.

Focus on providing factual information with clear references to support your statements."""
            
            # Get citations from platform
            citations = platform.get_citations(enhanced_query)
            
            # Extract response text from citations (if available) or create synthetic response
            response_text = ""
            urls = []
            
            for citation in citations:
                if 'url' in citation:
                    urls.append(citation['url'])
                # Some platforms might include response text in citations
                if 'content' in citation:
                    response_text += citation['content'] + " "
                elif 'text' in citation:
                    response_text += citation['text'] + " "
            
            # If no response text from citations, make a simple query to get text
            if not response_text:
                # For platforms that don't provide response text in citations,
                # we'll analyze based on the query and citation URLs
                response_text = f"Analysis of {query} with citations from: " + ", ".join([self.extract_domain_from_url(url) for url in urls])
            
            # Analyze leagues mentioned
            leagues_present = self.detect_leagues_in_text(response_text + " " + query)
            winner = self.determine_winner(response_text + " " + query, leagues_present)
            
            # Analyze NBA prominence specifically
            nba_prominence = self.analyze_position_prominence(response_text + " " + query, 'NBA')
            
            # Count media sources
            media_sources = []
            for url in urls:
                domain = self.extract_domain_from_url(url)
                if any(target in domain for target in self.target_domains):
                    media_sources.append(domain)
            
            return {
                'platform': platform_name,
                'query': query,
                'response_text': response_text,
                'urls': urls,
                'leagues_present': leagues_present,
                'winner': winner,
                'nba_prominence': nba_prominence,
                'media_sources': media_sources,
                'total_citations': len(urls)
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {str(e)}")
            return {
                'platform': platform_name,
                'query': query,
                'response_text': '',
                'urls': [],
                'leagues_present': {'NBA': False, 'NFL': False, 'MLB': False, 'NHL': False},
                'winner': 'Error',
                'nba_prominence': 'Not Present',
                'media_sources': [],
                'total_citations': 0
            }
    
    def collect_all_data(self):
        """Collect data from all platforms for all queries."""
        logger.info("Starting comprehensive sports league citation collection...")
        
        total_queries = len(self.queries) * len(self.platforms)
        completed = 0
        
        for query in self.queries:
            logger.info(f"Processing query: {query}")
            query_results = []
            
            # Query all platforms for this question
            for platform_name in self.platforms.keys():
                result = self.query_platform(platform_name, query)
                query_results.append(result)
                completed += 1
                logger.info(f"Progress: {completed}/{total_queries} queries completed")
                
                # Add delay to respect rate limits
                import time
                time.sleep(3)
            
            # Process results for this query
            self.process_query_results(query, query_results)
    
    def process_query_results(self, query: str, results: List[Dict]):
        """Process results from all platforms for a single query."""
        # Aggregate data for query matrix
        platforms_data = {}
        for result in results:
            platforms_data[result['platform']] = result
        
        # Determine overall winner for this query
        winners = [r['winner'] for r in results if r['winner'] != 'Error' and r['winner'] != 'None']
        overall_winner = max(set(winners), key=winners.count) if winners else 'None'
        
        # Add to query matrix
        for platform_name, data in platforms_data.items():
            self.query_matrix_data.append({
                'query': query,
                'engine': platform_name,
                'nba_present': 'Yes' if data['leagues_present']['NBA'] else 'No',
                'nfl_present': 'Yes' if data['leagues_present']['NFL'] else 'No',
                'mlb_present': 'Yes' if data['leagues_present']['MLB'] else 'No',
                'nhl_present': 'Yes' if data['leagues_present']['NHL'] else 'No',
                'winner': data['winner'],
                'position_prominence': data['nba_prominence'],
                'media_sources_count': len(data['media_sources']),
                'total_citations': data['total_citations']
            })
            
            # Add raw citations
            for url in data['urls']:
                domain = self.extract_domain_from_url(url)
                leagues_in_response = [league for league, present in data['leagues_present'].items() if present]
                
                self.raw_citations_data.append({
                    'engine': platform_name,
                    'query': query,
                    'domain': domain,
                    'url': url,
                    'league_mentioned': ', '.join(leagues_in_response),
                    'classification': self.classify_domain(domain)
                })
                
                # Update media tracking
                if domain not in self.media_tracking_data:
                    self.media_tracking_data[domain] = {
                        'nba_citations': 0,
                        'nfl_citations': 0,
                        'mlb_citations': 0,
                        'nhl_citations': 0,
                        'total_citations': 0
                    }
                
                for league in leagues_in_response:
                    if league in ['NBA', 'NFL', 'MLB', 'NHL']:
                        self.media_tracking_data[domain][f'{league.lower()}_citations'] += 1
                
                self.media_tracking_data[domain]['total_citations'] += 1
        
        # Add head-to-head comparison
        nba_wins = sum(1 for r in results if r['winner'] == 'NBA')
        nfl_wins = sum(1 for r in results if r['winner'] == 'NFL')
        mlb_wins = sum(1 for r in results if r['winner'] == 'MLB')
        nhl_wins = sum(1 for r in results if r['winner'] == 'NHL')
        
        self.head_to_head_data.append({
            'query': query,
            'nba_vs_nfl': 'NBA' if nba_wins > nfl_wins else 'NFL' if nfl_wins > nba_wins else 'Tie',
            'nba_vs_mlb': 'NBA' if nba_wins > mlb_wins else 'MLB' if mlb_wins > nba_wins else 'Tie',
            'nba_vs_nhl': 'NBA' if nba_wins > nhl_wins else 'NHL' if nhl_wins > nba_wins else 'Tie',
            'overall_winner': overall_winner
        })
    
    def classify_domain(self, domain: str) -> str:
        """Classify domain type."""
        if any(news in domain for news in ['espn', 'cnn', 'reuters', 'ap.org', 'usatoday']):
            return 'news'
        elif any(social in domain for social in ['reddit', 'twitter', 'facebook']):
            return 'social'
        elif any(sports in domain for sports in ['bleacher', 'athletic', 'si.com', 'foxsports', 'cbssports']):
            return 'editorial'
        else:
            return 'other'
    
    def export_csv_files(self):
        """Export all collected data to CSV files."""
        logger.info("Exporting data to CSV files...")
        
        # 1. Sports League Query Matrix
        matrix_file = self.output_dir / f"SPORTS_LEAGUE_QUERY_MATRIX_{self.timestamp}.csv"
        with open(matrix_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'nba_present', 'nfl_present', 'mlb_present', 
                'nhl_present', 'winner', 'position_prominence', 'media_sources_count', 'total_citations'
            ])
            writer.writeheader()
            writer.writerows(self.query_matrix_data)
        
        # 2. Raw Citations
        citations_file = self.output_dir / f"RAW_CITATIONS_{self.timestamp}.csv"
        with open(citations_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'engine', 'query', 'domain', 'url', 'league_mentioned', 'classification'
            ])
            writer.writeheader()
            writer.writerows(self.raw_citations_data)
        
        # 3. Media Tracking
        media_file = self.output_dir / f"MEDIA_TRACKING_{self.timestamp}.csv"
        with open(media_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['media_outlet', 'nba_citations', 'nfl_citations', 'mlb_citations', 'nhl_citations', 'total_citations', 'dominant_league']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for domain, data in self.media_tracking_data.items():
                # Determine dominant league
                league_counts = {
                    'NBA': data['nba_citations'],
                    'NFL': data['nfl_citations'],
                    'MLB': data['mlb_citations'],
                    'NHL': data['nhl_citations']
                }
                dominant_league = max(league_counts, key=league_counts.get) if max(league_counts.values()) > 0 else 'None'
                
                writer.writerow({
                    'media_outlet': domain,
                    'nba_citations': data['nba_citations'],
                    'nfl_citations': data['nfl_citations'],
                    'mlb_citations': data['mlb_citations'],
                    'nhl_citations': data['nhl_citations'],
                    'total_citations': data['total_citations'],
                    'dominant_league': dominant_league
                })
        
        # 4. Head-to-Head Results
        h2h_file = self.output_dir / f"HEAD_TO_HEAD_RESULTS_{self.timestamp}.csv"
        with open(h2h_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'nba_vs_nfl', 'nba_vs_mlb', 'nba_vs_nhl', 'overall_winner'
            ])
            writer.writeheader()
            writer.writerows(self.head_to_head_data)
        
        logger.info(f"Data exported to {self.output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - {matrix_file.name}")
        logger.info(f"  - {citations_file.name}")
        logger.info(f"  - {media_file.name}")
        logger.info(f"  - {h2h_file.name}")
    
    def generate_summary_report(self):
        """Generate a summary analysis report."""
        logger.info("Generating summary report...")
        
        # Calculate key metrics
        total_queries = len(self.query_matrix_data)
        nba_mentions = sum(1 for row in self.query_matrix_data if row['nba_present'] == 'Yes')
        nba_wins = sum(1 for row in self.query_matrix_data if row['winner'] == 'NBA')
        
        summary = {
            'collection_timestamp': self.timestamp,
            'total_queries_processed': total_queries,
            'nba_mention_rate': f"{(nba_mentions/total_queries)*100:.1f}%",
            'nba_win_rate': f"{(nba_wins/total_queries)*100:.1f}%",
            'top_media_sources': sorted(self.media_tracking_data.items(), 
                                      key=lambda x: x[1]['total_citations'], reverse=True)[:10]
        }
        
        # Save summary
        summary_file = self.output_dir / f"COLLECTION_SUMMARY_{self.timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report saved to {summary_file}")
        return summary

def main():
    """Main execution function."""
    collector = SportsLeagueCitationCollector()
    
    try:
        # Collect all data
        collector.collect_all_data()
        
        # Export to CSV files
        collector.export_csv_files()
        
        # Generate summary
        summary = collector.generate_summary_report()
        
        print("\n" + "="*60)
        print("SPORTS LEAGUE CITATION COLLECTION COMPLETE")
        print("="*60)
        print(f"Total queries processed: {summary['total_queries_processed']}")
        print(f"NBA mention rate: {summary['nba_mention_rate']}")
        print(f"NBA win rate: {summary['nba_win_rate']}")
        print(f"Data exported to: {collector.output_dir}")
        
    except Exception as e:
        logger.error(f"Collection failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

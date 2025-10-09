#!/usr/bin/env python3
"""
Vevo AI Citation Analysis - Media Sources & Content Types Study
Focuses on Vevo's visibility across AI platforms and identifies key media sources
driving Vevo's narrative, including YouTube attribution analysis.
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

class VevoMediaAnalyzer:
    """Analyzes Vevo citation visibility and media influence across AI platforms."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.output_dir = Path("case_studies/vevo_analysis")
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
        
        # Vevo-specific queries (15 total)
        self.vevo_queries = [
            # Music Video & Platform Queries (8)
            "How do I watch official music videos online?",
            "What is Vevo and how does it work?",
            "Vevo vs YouTube for music videos",
            "Best platforms for high-quality music videos",
            "How do artists get on Vevo?",
            "Vevo subscription and pricing",
            "Most watched music videos on Vevo",
            "How to watch Vevo on smart TV",
            
            # Artist & Content Queries (4)
            "Vevo DSCVR artists to watch",
            "Vevo live performances and sessions",
            "Vevo Originals exclusive content",
            "New music video releases today",
            
            # Industry & Business Queries (3)
            "Who owns Vevo?",
            "How does Vevo make money?",
            "Vevo's role in the music industry"
        ]
        
        # Target media domains for detailed tracking
        self.target_domains = {
            'vevo.com': 'official_vevo',
            'youtube.com': 'platform_content',
            'billboard.com': 'music_media',
            'rollingstone.com': 'music_media',
            'pitchfork.com': 'music_media',
            'nme.com': 'music_media',
            'variety.com': 'music_media',
            'theverge.com': 'tech_media',
            'techcrunch.com': 'tech_media',
            'engadget.com': 'tech_media',
            'musicbusinessworldwide.com': 'music_media',
            'wikipedia.org': 'reference',
            'reddit.com': 'social_media',
            'twitter.com': 'social_media',
            'x.com': 'social_media',
            'instagram.com': 'social_media',
            'tiktok.com': 'social_media',
            'spotify.com': 'platform_content',
            'applemusic.com': 'platform_content'
        }
        
        # Content type patterns for classification
        self.content_patterns = {
            'video': [r'youtube\.com/watch', r'vevo\.com/watch', r'video', r'embed'],
            'article': [r'article', r'news', r'story', r'report'],
            'social': [r'twitter\.com', r'instagram\.com', r'tiktok\.com', r'reddit\.com'],
            'wiki': [r'wikipedia\.org', r'wiki'],
            'forum': [r'reddit\.com/r/', r'forum', r'discussion'],
            'official': [r'vevo\.com', r'official']
        }
        
        # Data storage
        self.visibility_data = []
        self.media_influence_data = {}
        self.content_type_data = []
        
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
    
    def classify_content_type(self, url: str) -> str:
        """Classify content type based on URL patterns."""
        url_lower = url.lower()
        
        for content_type, patterns in self.content_patterns.items():
            if any(re.search(pattern, url_lower) for pattern in patterns):
                return content_type
        
        return 'other'
    
    def analyze_vevo_attribution(self, url: str, domain: str) -> Dict[str, bool]:
        """Analyze if Vevo gets proper attribution vs YouTube."""
        attribution = {
            'vevo_attributed': False,
            'youtube_attributed': False,
            'vevo_channel_mentioned': False
        }
        
        url_lower = url.lower()
        
        if 'vevo.com' in domain:
            attribution['vevo_attributed'] = True
        elif 'youtube.com' in domain:
            attribution['youtube_attributed'] = True
            # Check if it's specifically a Vevo channel on YouTube
            if 'vevo' in url_lower:
                attribution['vevo_channel_mentioned'] = True
        
        return attribution
    
    def query_platform(self, platform_name: str, query: str) -> Dict:
        """Query a specific platform with enhanced Vevo citation tracking."""
        logger.info(f"Querying {platform_name}: {query[:50]}...")
        
        try:
            platform = self.platforms[platform_name]
            
            # Enhanced prompt for Vevo queries
            enhanced_query = f"""Please provide comprehensive information about: {query}

Include specific sources, citations, URLs, and references. Focus on authoritative music industry sources, official Vevo content, platform information, and current data. Provide direct links to relevant content when possible."""
            
            # Get citations from platform
            citations = platform.get_citations(enhanced_query)
            
            # Process citations with detailed Vevo-specific analysis
            urls = []
            domains = []
            top_3_domains = []
            
            # Content type counters
            content_counts = {
                'video_citations': 0,
                'article_citations': 0,
                'social_citations': 0,
                'official_citations': 0,
                'wiki_citations': 0,
                'forum_citations': 0
            }
            
            # Track specific domain presence
            domain_presence = {
                'vevo_com_present': False,
                'youtube_present': False,
                'billboard_present': False,
                'rolling_stone_present': False,
                'pitchfork_present': False
            }
            
            # Media category counters
            media_counts = {
                'official_vevo_count': 0,
                'music_media_count': 0,
                'tech_media_count': 0,
                'social_media_count': 0
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
                    
                    # Classify content type
                    content_type = self.classify_content_type(url)
                    if content_type in content_counts:
                        content_counts[f'{content_type}_citations'] += 1
                    
                    # Check for specific domain presence
                    if 'vevo.com' in domain:
                        domain_presence['vevo_com_present'] = True
                        media_counts['official_vevo_count'] += 1
                    elif 'youtube.com' in domain:
                        domain_presence['youtube_present'] = True
                    elif 'billboard.com' in domain:
                        domain_presence['billboard_present'] = True
                        media_counts['music_media_count'] += 1
                    elif 'rollingstone.com' in domain:
                        domain_presence['rolling_stone_present'] = True
                        media_counts['music_media_count'] += 1
                    elif 'pitchfork.com' in domain:
                        domain_presence['pitchfork_present'] = True
                        media_counts['music_media_count'] += 1
                    
                    # Classify by media category
                    domain_category = self.classify_domain(domain)
                    if domain_category == 'music_media':
                        media_counts['music_media_count'] += 1
                    elif domain_category == 'tech_media':
                        media_counts['tech_media_count'] += 1
                    elif domain_category == 'social_media':
                        media_counts['social_media_count'] += 1
                    
                    # Update media influence tracking
                    if domain not in self.media_influence_data:
                        self.media_influence_data[domain] = {
                            'total_citations': 0,
                            'content_category': self.classify_domain(domain),
                            'positions': [],
                            'primary_topics': [],
                            'sample_urls': []
                        }
                    
                    self.media_influence_data[domain]['total_citations'] += 1
                    self.media_influence_data[domain]['positions'].append(i + 1)
                    
                    # Store sample URLs (max 3 per domain)
                    if len(self.media_influence_data[domain]['sample_urls']) < 3:
                        self.media_influence_data[domain]['sample_urls'].append(url)
                    
                    # Add query as topic context
                    if query not in self.media_influence_data[domain]['primary_topics']:
                        self.media_influence_data[domain]['primary_topics'].append(query)
            
            # Store content type analysis
            content_result = {
                'query': query,
                'engine': platform_name,
                **content_counts
            }
            self.content_type_data.append(content_result)
            
            return {
                'platform': platform_name,
                'query': query,
                'total_citations': len(citations),
                'urls': urls,
                'domains': domains,
                'top_3_domains': top_3_domains[:3],
                **domain_presence,
                **media_counts
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
                'vevo_com_present': False,
                'youtube_present': False,
                'billboard_present': False,
                'rolling_stone_present': False,
                'pitchfork_present': False,
                'official_vevo_count': 0,
                'music_media_count': 0,
                'tech_media_count': 0,
                'social_media_count': 0
            }
    
    def collect_vevo_data(self):
        """Collect Vevo citation data across all platforms."""
        logger.info("Starting Vevo citation collection...")
        
        total_queries = len(self.vevo_queries) * len(self.platforms)
        completed = 0
        
        for query in self.vevo_queries:
            logger.info(f"Processing Vevo query: {query}")
            
            for platform_name in self.platforms.keys():
                result = self.query_platform(platform_name, query)
                self.visibility_data.append(result)
                completed += 1
                logger.info(f"Vevo Progress: {completed}/{total_queries} queries completed")
                
                # Rate limiting
                import time
                time.sleep(3)
    
    def export_csv_files(self):
        """Export all collected data to CSV files."""
        logger.info("Exporting Vevo analysis data to CSV files...")
        
        # 1. Vevo Visibility Matrix
        visibility_file = self.output_dir / f"VEVO_VISIBILITY_MATRIX_{self.timestamp}.csv"
        with open(visibility_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'total_citations', 'top_3_domains',
                'vevo_com_present', 'youtube_present', 'billboard_present', 
                'rolling_stone_present', 'pitchfork_present',
                'official_vevo_count', 'music_media_count', 'tech_media_count', 
                'social_media_count', 'urls'
            ])
            writer.writeheader()
            
            for row in self.visibility_data:
                writer.writerow({
                    'query': row['query'],
                    'engine': row['platform'],
                    'total_citations': row['total_citations'],
                    'top_3_domains': ', '.join(row['top_3_domains']),
                    'vevo_com_present': 'Yes' if row['vevo_com_present'] else 'No',
                    'youtube_present': 'Yes' if row['youtube_present'] else 'No',
                    'billboard_present': 'Yes' if row['billboard_present'] else 'No',
                    'rolling_stone_present': 'Yes' if row['rolling_stone_present'] else 'No',
                    'pitchfork_present': 'Yes' if row['pitchfork_present'] else 'No',
                    'official_vevo_count': row['official_vevo_count'],
                    'music_media_count': row['music_media_count'],
                    'tech_media_count': row['tech_media_count'],
                    'social_media_count': row['social_media_count'],
                    'urls': ' | '.join(row['urls'])
                })
        
        # 2. Media Influence Analysis
        influence_file = self.output_dir / f"MEDIA_INFLUENCE_{self.timestamp}.csv"
        with open(influence_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'media_outlet', 'total_citations', 'content_category', 
                'avg_position', 'primary_topics', 'sample_urls'
            ])
            writer.writeheader()
            
            for domain, data in self.media_influence_data.items():
                avg_position = sum(data['positions']) / len(data['positions']) if data['positions'] else 0
                
                writer.writerow({
                    'media_outlet': domain,
                    'total_citations': data['total_citations'],
                    'content_category': data['content_category'],
                    'avg_position': round(avg_position, 2),
                    'primary_topics': ' | '.join(data['primary_topics'][:3]),  # Top 3 topics
                    'sample_urls': ' | '.join(data['sample_urls'])
                })
        
        # 3. Content Type Analysis
        content_file = self.output_dir / f"CONTENT_TYPE_ANALYSIS_{self.timestamp}.csv"
        with open(content_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query', 'engine', 'video_citations', 'article_citations', 
                'social_citations', 'official_citations', 'wiki_citations', 'forum_citations'
            ])
            writer.writeheader()
            writer.writerows(self.content_type_data)
        
        logger.info(f"Data exported to {self.output_dir}")
        logger.info(f"Files created:")
        logger.info(f"  - {visibility_file.name}")
        logger.info(f"  - {influence_file.name}")
        logger.info(f"  - {content_file.name}")
    
    def generate_summary_report(self):
        """Generate comprehensive Vevo analysis summary."""
        logger.info("Generating Vevo analysis summary...")
        
        # Calculate key metrics
        total_queries = len(self.visibility_data)
        total_citations = sum(d['total_citations'] for d in self.visibility_data)
        vevo_official_citations = sum(d['official_vevo_count'] for d in self.visibility_data)
        youtube_mentions = sum(1 for d in self.visibility_data if d['youtube_present'])
        
        # Top media sources
        top_media = sorted(self.media_influence_data.items(), 
                          key=lambda x: x[1]['total_citations'], reverse=True)[:10]
        
        # Platform performance
        platform_stats = {}
        for data in self.visibility_data:
            platform = data['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'queries': 0, 'citations': 0, 'vevo_mentions': 0}
            platform_stats[platform]['queries'] += 1
            platform_stats[platform]['citations'] += data['total_citations']
            if data['vevo_com_present']:
                platform_stats[platform]['vevo_mentions'] += 1
        
        # Content type analysis
        content_analysis = {}
        for data in self.content_type_data:
            for key, value in data.items():
                if key.endswith('_citations'):
                    content_analysis[key] = content_analysis.get(key, 0) + value
        
        summary = {
            'analysis_timestamp': self.timestamp,
            'total_queries_processed': total_queries,
            'total_citations_collected': total_citations,
            'vevo_official_percentage': f"{(vevo_official_citations/total_citations)*100:.1f}%" if total_citations > 0 else "0%",
            'youtube_mention_rate': f"{(youtube_mentions/total_queries)*100:.1f}%",
            'top_media_sources': [{'domain': domain, 'citations': data['total_citations'], 'category': data['content_category']} for domain, data in top_media],
            'platform_performance': platform_stats,
            'content_type_breakdown': content_analysis,
            'key_insights': self._generate_insights()
        }
        
        # Save summary
        summary_file = self.output_dir / f"VEVO_ANALYSIS_SUMMARY_{self.timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report saved to {summary_file}")
        return summary
    
    def _generate_insights(self) -> List[str]:
        """Generate strategic insights from the Vevo data."""
        insights = []
        
        # Analyze Vevo vs YouTube attribution
        vevo_direct = sum(d['official_vevo_count'] for d in self.visibility_data)
        youtube_mentions = sum(1 for d in self.visibility_data if d['youtube_present'])
        
        if youtube_mentions > vevo_direct * 2:
            insights.append("YouTube dominates Vevo content attribution - opportunity to strengthen Vevo brand identity")
        
        # Analyze music vs tech media coverage
        music_media_total = sum(d['music_media_count'] for d in self.visibility_data)
        tech_media_total = sum(d['tech_media_count'] for d in self.visibility_data)
        
        if music_media_total > tech_media_total:
            insights.append("Music media provides stronger Vevo coverage than tech media - leverage music industry partnerships")
        else:
            insights.append("Tech media coverage opportunity - Vevo's technology story underrepresented")
        
        # Platform-specific insights
        platform_citations = {}
        for data in self.visibility_data:
            platform = data['platform']
            platform_citations[platform] = platform_citations.get(platform, 0) + data['total_citations']
        
        if platform_citations:
            best_platform = max(platform_citations, key=platform_citations.get)
            insights.append(f"{best_platform} provides the most Vevo citations - prioritize content optimization for this platform")
        
        # Official content analysis
        if 'vevo.com' not in self.media_influence_data or self.media_influence_data.get('vevo.com', {}).get('total_citations', 0) < 10:
            insights.append("Vevo.com has low citation visibility - official content strategy optimization needed")
        
        return insights

def main():
    """Main execution function."""
    analyzer = VevoMediaAnalyzer()
    
    try:
        # Collect Vevo data
        analyzer.collect_vevo_data()
        
        # Export to CSV files
        analyzer.export_csv_files()
        
        # Generate summary
        summary = analyzer.generate_summary_report()
        
        print("\n" + "="*60)
        print("VEVO AI CITATION ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total queries processed: {summary['total_queries_processed']}")
        print(f"Total citations collected: {summary['total_citations_collected']}")
        print(f"Vevo official percentage: {summary['vevo_official_percentage']}")
        print(f"YouTube mention rate: {summary['youtube_mention_rate']}")
        print(f"Data exported to: {analyzer.output_dir}")
        print("\nKey Insights:")
        for insight in summary['key_insights']:
            print(f"  • {insight}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

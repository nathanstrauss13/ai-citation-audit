#!/usr/bin/env python3
"""
NBA vs. Major Sports Leagues - Programmatic API Data Collection V2
Precision Methodology for AI Citation Analysis with Competitive Context

Tests 15 queries across 4 AI platforms (60 total prompts)
Tracks NBA, NFL, MLB, NHL mentions in responses and citations
"""

import os
import sys
import json
import csv
import logging
import requests
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Import platform adapters
from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NBALeagueAuditor:
    """
    Comprehensive auditor for NBA visibility vs. competing sports leagues
    Follows V2 precision methodology with multi-league tracking
    """
    
    def __init__(self):
        # League definitions
        self.leagues = {
            'NBA': ['NBA', 'National Basketball Association', 'nba.com'],
            'NFL': ['NFL', 'National Football League', 'nfl.com'],
            'MLB': ['MLB', 'Major League Baseball', 'mlb.com'],
            'NHL': ['NHL', 'National Hockey League', 'nhl.com'],
            'MLS': ['MLS', 'Major League Soccer', 'mls.com']
        }
        
        # Revenue context for benchmarking (in billions)
        self.league_revenue = {
            'NBA': 11.0,
            'NFL': 19.0,
            'MLB': 11.5,
            'NHL': 6.0,
            'MLS': 1.5
        }
        
        # Initialize platforms
        self.platforms = {
            'chatgpt': ChatGPTPlatform(),
            'claude': ClaudePlatform(),
            'perplexity': PerplexityPlatform(),
            'gemini': GeminiPlatform()
        }
        
        # Query definitions
        self.queries = self._define_queries()
        
        # Storage for results
        self.league_response_data = []
        self.citation_details_data = []
        self.competitive_mentions_data = []
        
        logger.info("NBA League Auditor initialized")
    
    def _define_queries(self) -> List[Dict[str, str]]:
        """Define the 15 test queries"""
        queries = []
        
        # BRANDED QUERIES (4 queries - NBA explicitly mentioned)
        branded = [
            "Tell me about the NBA",
            "What makes the NBA different from other professional sports leagues?",
            "NBA game schedule tonight",
            "How can I watch NBA games?"
        ]
        for q in branded:
            queries.append({"text": q, "type": "branded", "category": "branded"})
        
        # LEAGUE-AGNOSTIC QUERIES (11 queries)
        
        # General Sports Entertainment (4)
        general = [
            "What's the most popular professional sports league in America?",
            "Best professional sports to watch",
            "Most exciting sports league",
            "Which sports league has the best athletes?"
        ]
        for q in general:
            queries.append({"text": q, "type": "league_agnostic", "category": "general_sports"})
        
        # Family Entertainment (3)
        family = [
            "Best professional sports for families",
            "Kid-friendly sporting events",
            "Sports games to take children to"
        ]
        for q in family:
            queries.append({"text": q, "type": "league_agnostic", "category": "family"})
        
        # Entertainment Value (3)
        entertainment = [
            "Most entertaining sports league",
            "Fast-paced sports to watch",
            "Best sports for casual fans"
        ]
        for q in entertainment:
            queries.append({"text": q, "type": "league_agnostic", "category": "entertainment"})
        
        # Cultural Impact (1)
        cultural = [
            "Which sports league has the biggest cultural impact?"
        ]
        for q in cultural:
            queries.append({"text": q, "type": "league_agnostic", "category": "cultural"})
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """
        Execute complete audit across all queries and platforms
        Returns paths to generated CSV files
        """
        logger.info(f"Starting NBA League Audit - {len(self.queries)} queries × {len(self.platforms)} platforms = {len(self.queries) * len(self.platforms)} total tests")
        
        total_tests = len(self.queries) * len(self.platforms)
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            query_type = query_info["type"]
            query_category = query_info["category"]
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Type: {query_type} | Category: {query_category}")
            logger.info(f"{'='*80}")
            
            for platform_name, platform in self.platforms.items():
                completed += 1
                logger.info(f"\n[{completed}/{total_tests}] Testing on {platform_name}...")
                
                try:
                    # Get response and citations from platform
                    result = self._query_platform(platform, platform_name, query_text)
                    
                    if result:
                        # Analyze response for league mentions
                        analysis = self._analyze_response(
                            result['response_text'],
                            result['citations'],
                            query_text,
                            query_type,
                            platform_name
                        )
                        
                        # Store in appropriate data structures
                        self.league_response_data.append(analysis['league_matrix_row'])
                        self.citation_details_data.extend(analysis['citation_details'])
                        self.competitive_mentions_data.extend(analysis['competitive_mentions'])
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error testing {query_text} on {platform_name}: {e}")
                    continue
        
        # Generate CSV files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_csv_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("NBA League Audit Complete!")
        logger.info(f"Generated files:")
        for key, path in output_files.items():
            logger.info(f"  - {key}: {path}")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _query_platform(self, platform, platform_name: str, query: str) -> Dict[str, Any]:
        """Query a platform and return structured results"""
        try:
            # Get citations from platform
            citations = platform.get_citations(query)
            
            # Get full response text
            response_text = self._get_full_response(platform, platform_name, query)
            
            return {
                'response_text': response_text,
                'citations': citations,
                'platform': platform_name
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {e}")
            return None
    
    def _get_full_response(self, platform, platform_name: str, query: str) -> str:
        """Get full response text from platform"""
        try:
            if platform_name == 'chatgpt':
                return self._get_chatgpt_response_text(query)
            elif platform_name == 'claude':
                return self._get_claude_response_text(query)
            elif platform_name == 'perplexity':
                return self._get_perplexity_response_text(query)
            elif platform_name == 'gemini':
                return self._get_gemini_response_text(query)
            else:
                return ""
        except Exception as e:
            logger.error(f"Error getting full response from {platform_name}: {e}")
            return ""
    
    def _get_chatgpt_response_text(self, query: str) -> str:
        """Get full ChatGPT response text"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 1500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return ""
        except Exception as e:
            logger.error(f"ChatGPT response error: {e}")
            return ""
    
    def _get_claude_response_text(self, query: str) -> str:
        """Get full Claude response text"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": query}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = ""
                for block in data.get('content', []):
                    if block.get('type') == 'text':
                        text += block.get('text', '')
                return text
            return ""
        except Exception as e:
            logger.error(f"Claude response error: {e}")
            return ""
    
    def _get_perplexity_response_text(self, query: str) -> str:
        """Get full Perplexity response text"""
        try:
            api_key = os.getenv('PERPLEXITY_API_KEY')
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return ""
        except Exception as e:
            logger.error(f"Perplexity response error: {e}")
            return ""
    
    def _get_gemini_response_text(self, query: str) -> str:
        """Get full Gemini response text"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": query}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text']
            return ""
        except Exception as e:
            logger.error(f"Gemini response error: {e}")
            return ""
    
    def _analyze_response(
        self,
        response_text: str,
        citations: List[Dict],
        query: str,
        query_type: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Analyze response and citations for league mentions
        Returns data for all three CSV files
        """
        
        # 1. Check which leagues are mentioned in response text
        leagues_in_response = self._check_leagues_in_text(response_text)
        
        # 2. Count total citations
        total_citations = len(citations)
        
        # 3. Check citations for league mentions
        citations_by_league = {league: 0 for league in self.leagues.keys()}
        citation_details = []
        
        for citation in citations:
            url = citation.get('url', '')
            
            # Check which leagues are mentioned in this citation's source
            leagues_in_source = self._check_leagues_in_url(url)
            
            for league in leagues_in_source:
                citations_by_league[league] += 1
            
            # Determine primary league focus of this citation
            primary_focus = self._determine_primary_league_focus(url, leagues_in_source)
            
            # Build citation detail row
            citation_details.append({
                'engine': platform,
                'query': query,
                'query_type': query_type,
                'citation_url': url,
                'domain': self._extract_domain(url),
                'domain_classification': self._classify_domain(url),
                'nba_mentioned_in_source': "Yes" if 'NBA' in leagues_in_source else "No",
                'nfl_mentioned_in_source': "Yes" if 'NFL' in leagues_in_source else "No",
                'mlb_mentioned_in_source': "Yes" if 'MLB' in leagues_in_source else "No",
                'nhl_mentioned_in_source': "Yes" if 'NHL' in leagues_in_source else "No",
                'content_type': self._classify_content_type(url),
                'primary_league_focus': primary_focus
            })
        
        # 4. Determine NBA response prominence
        nba_prominence = self._determine_nba_prominence(response_text, leagues_in_response)
        
        # 5. Detect other leagues mentioned
        other_leagues = self._detect_other_leagues(response_text)
        
        # 6. Track competitive mentions
        competitive_mentions = self._track_competitive_mentions(
            response_text, citations, query, query_type, platform, leagues_in_response
        )
        
        # Build league matrix row
        league_matrix_row = {
            'query': query,
            'query_type': query_type,
            'engine': platform,
            'nba_mentioned_in_response': "Yes" if 'NBA' in leagues_in_response else "No",
            'nfl_mentioned': "Yes" if 'NFL' in leagues_in_response else "No",
            'mlb_mentioned': "Yes" if 'MLB' in leagues_in_response else "No",
            'nhl_mentioned': "Yes" if 'NHL' in leagues_in_response else "No",
            'other_leagues_mentioned': ", ".join(other_leagues) if other_leagues else "None",
            'total_citations': total_citations,
            'citations_mentioning_nba': citations_by_league['NBA'],
            'citations_mentioning_nfl': citations_by_league['NFL'],
            'citations_mentioning_mlb': citations_by_league['MLB'],
            'citations_mentioning_nhl': citations_by_league['NHL'],
            'response_prominence_nba': nba_prominence
        }
        
        return {
            'league_matrix_row': league_matrix_row,
            'citation_details': citation_details,
            'competitive_mentions': competitive_mentions
        }
    
    def _check_leagues_in_text(self, text: str) -> Set[str]:
        """Check which major leagues are mentioned in text"""
        if not text:
            return set()
        
        text_lower = text.lower()
        mentioned_leagues = set()
        
        for league, patterns in self.leagues.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    mentioned_leagues.add(league)
                    break
        
        return mentioned_leagues
    
    def _check_leagues_in_url(self, url: str) -> Set[str]:
        """
        Check which leagues are mentioned in a URL's content
        FAST MODE: Only checks official sites, skips fetching other URLs
        """
        if not url:
            return set()
        
        mentioned_leagues = set()
        url_lower = url.lower()
        
        # Check for official league sites
        for league, patterns in self.leagues.items():
            for pattern in patterns:
                if pattern.lower() in url_lower:
                    mentioned_leagues.add(league)
                    break
        
        # FAST MODE: Skip fetching external URLs
        # In full mode, would fetch and parse content
        
        return mentioned_leagues
    
    def _determine_primary_league_focus(self, url: str, leagues_mentioned: Set[str]) -> str:
        """Determine which league is the primary focus of a citation"""
        if not leagues_mentioned:
            return "None"
        
        if len(leagues_mentioned) == 1:
            return list(leagues_mentioned)[0]
        
        if len(leagues_mentioned) > 1:
            # Check if URL is from an official league site
            url_lower = url.lower()
            for league, patterns in self.leagues.items():
                if any(p.lower() in url_lower for p in patterns):
                    return league
            
            # Multiple leagues mentioned, not an official site
            return "Comparative"
        
        return "General Sports"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _classify_domain(self, url: str) -> str:
        """Classify domain type"""
        domain = self._extract_domain(url).lower()
        
        # Sports Media
        sports_media = ['espn.com', 'bleacherreport.com', 'theathletic.com', 'si.com',
                       'cbssports.com', 'foxsports.com', 'nbcsports.com', 'yahoo.com/sports']
        if any(d in domain for d in sports_media):
            return 'sports_media'
        
        # League Official
        if any(league.lower() + '.com' in domain for league in ['nba', 'nfl', 'mlb', 'nhl', 'mls']):
            return 'league_official'
        
        # Social Media
        social = ['twitter.com', 'youtube.com', 'instagram.com', 'reddit.com', 'tiktok.com']
        if any(d in domain for d in social):
            return 'social_media'
        
        # News Media
        news = ['nytimes.com', 'washingtonpost.com', 'cnn.com', 'usatoday.com']
        if any(d in domain for d in news):
            return 'news_media'
        
        # Authority
        authority = ['nielsen.com', 'statista.com', 'pewresearch.org']
        if any(d in domain for d in authority):
            return 'authority'
        
        # Business Media
        business = ['forbes.com', 'bloomberg.com', 'cnbc.com', 'businessinsider.com']
        if any(d in domain for d in business):
            return 'business_media'
        
        # Entertainment Media
        entertainment = ['ew.com', 'variety.com', 'hollywoodreporter.com']
        if any(d in domain for d in entertainment):
            return 'entertainment_media'
        
        return 'other'
    
    def _classify_content_type(self, url: str) -> str:
        """Classify content type based on URL"""
        url_lower = url.lower()
        
        if any(word in url_lower for word in ['schedule', 'calendar', 'game', 'tonight']):
            return 'schedule'
        elif any(word in url_lower for word in ['stats', 'statistics', 'ratings', 'viewership', 'data']):
            return 'statistics'
        elif any(word in url_lower for word in ['video', 'watch', 'youtube', 'highlights']):
            return 'video'
        elif any(word in url_lower for word in ['news', 'story', 'article']):
            return 'news_article'
        elif any(word in url_lower for word in ['opinion', 'editorial', 'analysis']):
            return 'opinion'
        elif any(word in url_lower for word in ['how', 'guide', 'tips']):
            return 'how_to'
        elif any(word in url_lower for word in ['about', 'official', 'league']):
            return 'company_page'
        elif any(word in url_lower for word in ['reddit', 'forum', 'discussion']):
            return 'forum_discussion'
        else:
            return 'other'
    
    def _determine_nba_prominence(self, text: str, leagues_mentioned: Set[str]) -> str:
        """Determine how prominently NBA was mentioned"""
        if 'NBA' not in leagues_mentioned:
            return "Not Present"
        
        if not text:
            return "Not Present"
        
        # Check if NBA is the only league mentioned
        if leagues_mentioned == {'NBA'}:
            return "Exclusive Focus"
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Check first sentence for NBA
        if sentences and 'NBA' in self._check_leagues_in_text(sentences[0]):
            # Check if it's a primary recommendation
            first_sent_lower = sentences[0].lower()
            if any(word in first_sent_lower for word in ['most', 'best', 'top', 'leading', 'premier', 'popular']):
                return "Featured First"
            else:
                return "Listed First Among Options"
        
        # NBA mentioned but not first
        return "Listed Among Options"
    
    def _detect_other_leagues(self, text: str) -> List[str]:
        """Detect non-major league mentions (MLS, international leagues, etc.)"""
        if not text:
            return []
        
        text_lower = text.lower()
        other_leagues = []
        
        # Common other leagues
        other_patterns = {
            'MLS': ['mls', 'major league soccer'],
            'Premier League': ['premier league', 'epl'],
            'La Liga': ['la liga'],
            'Serie A': ['serie a'],
            'Bundesliga': ['bundesliga'],
            'Champions League': ['champions league', 'uefa'],
            'NCAA': ['ncaa', 'college basketball', 'college football']
        }
        
        for league, patterns in other_patterns.items():
            if any(p in text_lower for p in patterns):
                other_leagues.append(league)
        
        return other_leagues
    
    def _track_competitive_mentions(
        self,
        response_text: str,
        citations: List[Dict],
        query: str,
        query_type: str,
        platform: str,
        leagues_in_response: Set[str]
    ) -> List[Dict]:
        """Track competitive league mentions and compare to NBA"""
        competitive_rows = []
        
        # Check which leagues are in citations
        leagues_in_citations = set()
        for citation in citations:
            url = citation.get('url', '')
            leagues_in_citations.update(self._check_leagues_in_url(url))
        
        # Check for viewership and cultural impact data
        has_viewership_data = any(word in response_text.lower() 
                                  for word in ['viewership', 'ratings', 'attendance', 'viewers', 'audience'])
        has_cultural_impact = any(word in response_text.lower() 
                                 for word in ['cultural', 'culture', 'impact', 'influence', 'global'])
        
        # Track each major league
        for league in ['NFL', 'NBA', 'MLB', 'NHL']:
            in_response = league in leagues_in_response
            in_citations = league in leagues_in_citations
            
            # Determine prominence vs NBA
            if league == 'NBA':
                prominence = self._determine_nba_prominence(response_text, leagues_in_response)
            else:
                prominence = self._compare_league_to_nba(
                    response_text, league, 'NBA' in leagues_in_response
                )
            
            competitive_rows.append({
                'query': query,
                'query_type': query_type,
                'engine': platform,
                'league_mentioned': league,
                'mentioned_in_response': "Yes" if in_response else "No",
                'mentioned_in_citations': "Yes" if in_citations else "No",
                'prominence_vs_nba': prominence,
                'viewership_data_cited': "Yes" if has_viewership_data else "No",
                'cultural_impact_noted': "Yes" if has_cultural_impact else "No"
            })
        
        return competitive_rows
    
    def _compare_league_to_nba(self, text: str, league: str, nba_present: bool) -> str:
        """Compare another league's prominence to NBA"""
        if not text:
            return "Both Absent"
        
        text_lower = text.lower()
        league_lower = league.lower()
        
        # Find positions in text
        league_pos = text_lower.find(league_lower)
        nba_pos = text_lower.find('nba')
        
        league_present = league_pos != -1
        
        if not league_present and not nba_present:
            return "Both Absent"
        elif league_present and not nba_present:
            return "Present, NBA Absent"
        elif not league_present and nba_present:
            return "N/A - NBA Present Only"
        else:
            # Both present - check order and emphasis
            if league_pos < nba_pos:
                # Check if featured prominently
                context_before_league = text_lower[max(0, league_pos-50):league_pos]
                if any(word in context_before_league for word in ['most', 'best', 'top', 'leading']):
                    return "Higher - Featured First"
                return "Higher - Mentioned First"
            elif league_pos > nba_pos:
                return "Lower - Mentioned After"
            else:
                return "Equal - Listed Together"
    
    def _generate_csv_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all three CSV files plus JSON summary"""
        output_dir = "case_studies/nba_analysis/v2_audit"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. LEAGUE_RESPONSE_MATRIX.csv
        matrix_path = f"{output_dir}/NBA_LEAGUE_RESPONSE_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'engine', 'nba_mentioned_in_response',
                'nfl_mentioned', 'mlb_mentioned', 'nhl_mentioned', 'other_leagues_mentioned',
                'total_citations', 'citations_mentioning_nba', 'citations_mentioning_nfl',
                'citations_mentioning_mlb', 'citations_mentioning_nhl', 'response_prominence_nba'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.league_response_data)
        files['league_matrix'] = matrix_path
        logger.info(f"Generated: {matrix_path}")
        
        # 2. CITATION_DETAILS.csv
        details_path = f"{output_dir}/NBA_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'query_type', 'citation_url', 'domain',
                'domain_classification', 'nba_mentioned_in_source', 'nfl_mentioned_in_source',
                'mlb_mentioned_in_source', 'nhl_mentioned_in_source', 
                'content_type', 'primary_league_focus'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citation_details'] = details_path
        logger.info(f"Generated: {details_path}")
        
        # 3. COMPETITIVE_MENTIONS.csv
        competitive_path = f"{output_dir}/NBA_COMPETITIVE_MENTIONS_{timestamp}.csv"
        with open(competitive_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'engine', 'league_mentioned',
                'mentioned_in_response', 'mentioned_in_citations', 'prominence_vs_nba',
                'viewership_data_cited', 'cultural_impact_noted'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.competitive_mentions_data)
        files['competitive_mentions'] = competitive_path
        logger.info(f"Generated: {competitive_path}")
        
        # 4. Generate summary JSON
        summary_path = f"{output_dir}/NBA_AUDIT_SUMMARY_{timestamp}.json"
        summary = self._generate_summary()
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files['summary'] = summary_path
        logger.info(f"Generated: {summary_path}")
        
        return files
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics including revenue-adjusted metrics"""
        total_queries = len(self.league_response_data)
        
        # NBA statistics
        nba_mentions = sum(1 for row in self.league_response_data 
                          if row['nba_mentioned_in_response'] == 'Yes')
        nba_mention_rate = (nba_mentions / total_queries * 100) if total_queries > 0 else 0
        
        # Citation statistics
        total_citations = sum(row['total_citations'] for row in self.league_response_data)
        nba_citations = sum(row['citations_mentioning_nba'] for row in self.league_response_data)
        nba_citation_authority = (nba_citations / total_citations * 100) if total_citations > 0 else 0
        
        # By query type
        branded_queries = [r for r in self.league_response_data if r['query_type'] == 'branded']
        agnostic_queries = [r for r in self.league_response_data if r['query_type'] == 'league_agnostic']
        
        branded_nba_mentions = sum(1 for r in branded_queries if r['nba_mentioned_in_response'] == 'Yes')
        agnostic_nba_mentions = sum(1 for r in agnostic_queries if r['nba_mentioned_in_response'] == 'Yes')
        
        # By platform
        platform_stats = {}
        for platform in ['chatgpt', 'claude', 'perplexity', 'gemini']:
            platform_queries = [r for r in self.league_response_data if r['engine'] == platform]
            platform_nba_mentions = sum(1 for r in platform_queries if r['nba_mentioned_in_response'] == 'Yes')
            platform_stats[platform] = {
                'total_queries': len(platform_queries),
                'nba_mentions': platform_nba_mentions,
                'mention_rate': (platform_nba_mentions / len(platform_queries) * 100) if len(platform_queries) > 0 else 0
            }
        
        # Competitive landscape
        nfl_mentions = sum(1 for r in self.league_response_data if r['nfl_mentioned'] == 'Yes')
        mlb_mentions = sum(1 for r in self.league_response_data if r['mlb_mentioned'] == 'Yes')
        nhl_mentions = sum(1 for r in self.league_response_data if r['nhl_mentioned'] == 'Yes')
        
        # Revenue-adjusted metrics
        nba_mentions_per_billion = nba_mentions / self.league_revenue['NBA']
        nfl_mentions_per_billion = nfl_mentions / self.league_revenue['NFL']
        mlb_mentions_per_billion = mlb_mentions / self.league_revenue['MLB']
        nhl_mentions_per_billion = nhl_mentions / self.league_revenue['NHL']
        
        return {
            'audit_date': datetime.now().isoformat(),
            'total_queries_tested': total_queries,
            'total_platforms': len(self.platforms),
            'total_tests_conducted': len(self.queries) * len(self.platforms),
            'overall_metrics': {
                'nba_mention_rate': round(nba_mention_rate, 2),
                'total_nba_mentions': nba_mentions,
                'total_citations': total_citations,
                'citations_with_nba': nba_citations,
                'nba_citation_authority_score': round(nba_citation_authority, 2)
            },
            'by_query_type': {
                'branded': {
                    'total': len(branded_queries),
                    'nba_mentions': branded_nba_mentions,
                    'rate': round((branded_nba_mentions / len(branded_queries) * 100) if len(branded_queries) > 0 else 0, 2)
                },
                'league_agnostic': {
                    'total': len(agnostic_queries),
                    'nba_mentions': agnostic_nba_mentions,
                    'rate': round((agnostic_nba_mentions / len(agnostic_queries) * 100) if len(agnostic_queries) > 0 else 0, 2)
                }
            },
            'by_platform': platform_stats,
            'competitive_landscape': {
                'nfl_mentions': nfl_mentions,
                'mlb_mentions': mlb_mentions,
                'nhl_mentions': nhl_mentions,
                'other_mentions': sum(1 for r in self.league_response_data if r['other_leagues_mentioned'] != 'None')
            },
            'revenue_adjusted_metrics': {
                'nba': {
                    'revenue_billions': self.league_revenue['NBA'],
                    'absolute_mentions': nba_mentions,
                    'mentions_per_billion': round(nba_mentions_per_billion, 3)
                },
                'nfl': {
                    'revenue_billions': self.league_revenue['NFL'],
                    'absolute_mentions': nfl_mentions,
                    'mentions_per_billion': round(nfl_mentions_per_billion, 3)
                },
                'mlb': {
                    'revenue_billions': self.league_revenue['MLB'],
                    'absolute_mentions': mlb_mentions,
                    'mentions_per_billion': round(mlb_mentions_per_billion, 3)
                },
                'nhl': {
                    'revenue_billions': self.league_revenue['NHL'],
                    'absolute_mentions': nhl_mentions,
                    'mentions_per_billion': round(nhl_mentions_per_billion, 3)
                }
            }
        }


def main():
    """Main execution function"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify API keys
        required_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY', 'GOOGLE_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
            logger.error("Please set these in your .env file")
            sys.exit(1)
        
        # Create auditor and run
        auditor = NBALeagueAuditor()
        output_files = auditor.run_audit()
        
        logger.info("\n" + "="*80)
        logger.info("NBA League Audit Complete!")
        logger.info("="*80)
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type}: {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

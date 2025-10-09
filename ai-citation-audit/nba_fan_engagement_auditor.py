#!/usr/bin/env python3
"""
NBA Fan Engagement AEO Analysis
Tests 18 queries across 4 AI platforms (72 total tests)
Focus: Consumer decision moments (streaming, tickets, fan recruitment)
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
from collections import defaultdict

# Import platform adapters
from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NBAFanEngagementAuditor:
    """
    Comprehensive auditor for NBA visibility in fan engagement queries
    Focus on commercial intent: streaming, ticketing, fan acquisition
    """
    
    def __init__(self):
        # Initialize platforms
        self.platforms = {
            'ChatGPT': ChatGPTPlatform(),
            'Claude': ClaudePlatform(),
            'Perplexity': PerplexityPlatform(),
            'Gemini': GeminiPlatform()
        }
        
        # Define queries with commercial intent
        self.queries = self._define_queries()
        
        # Media outlets to track
        self.tracked_media = self._define_tracked_media()
        
        # Storage for results
        self.engagement_matrix_data = []
        self.citation_details_data = []
        self.competitive_analysis_data = []
        self.media_tracking_data = defaultdict(lambda: {
            'total_citations': 0,
            'nba_mentions': 0,
            'queries_cited': set(),
            'engines_citing': set()
        })
        
        logger.info("NBA Fan Engagement Auditor initialized")
    
    def _define_queries(self) -> List[Dict[str, str]]:
        """Define 18 test queries with commercial intent categories"""
        queries = []
        
        # BRANDED QUERIES (6 queries - explicit NBA mentions)
        branded = [
            ("How do I watch NBA games?", "streaming"),
            ("Where can I stream NBA games live?", "streaming"),
            ("How do I get tickets to NBA games?", "ticketing"),
            ("Best NBA games to attend this season", "ticketing"),
            ("How do I become an NBA fan?", "fan_acquisition"),
            ("What NBA team should I root for?", "fan_acquisition")
        ]
        for text, intent in branded:
            queries.append({
                "text": text,
                "type": "branded",
                "commercial_intent": intent
            })
        
        # LEAGUE-AGNOSTIC QUERIES (12 queries - no league specified)
        agnostic = [
            ("What's the best professional sports league to watch?", "brand_preference"),
            ("Which sports have the best streaming options?", "streaming"),
            ("Most exciting sports to watch live?", "brand_preference"),
            ("Which sports league has the most passionate fans?", "brand_preference"),
            ("Easiest professional sport to get into as a new fan", "fan_acquisition"),
            ("Best sports league for international fans", "fan_acquisition"),
            ("Which sports leagues have the biggest cultural impact?", "brand_preference"),
            ("Most socially engaged sports leagues", "brand_preference"),
            ("Sports leagues with the best athletes", "brand_preference"),
            ("Best professional sports for families to watch", "fan_acquisition"),
            ("Which sports are most fun to play and watch?", "brand_preference"),
            ("Fastest growing sports leagues in the world", "brand_preference")
        ]
        for text, intent in agnostic:
            queries.append({
                "text": text,
                "type": "league_agnostic",
                "commercial_intent": intent
            })
        
        return queries
    
    def _define_tracked_media(self) -> Dict[str, Dict[str, str]]:
        """Define specific media outlets to track"""
        return {
            'espn.com': {'name': 'ESPN', 'classification': 'sports_media'},
            'theathletic.com': {'name': 'The Athletic', 'classification': 'sports_media'},
            'bleacherreport.com': {'name': 'Bleacher Report', 'classification': 'sports_media'},
            'si.com': {'name': 'Sports Illustrated', 'classification': 'sports_media'},
            'forbes.com': {'name': 'Forbes', 'classification': 'business_media'},
            'nba.com': {'name': 'NBA.com', 'classification': 'league_official'},
            'ticketmaster.com': {'name': 'Ticketmaster', 'classification': 'ticketing_platform'},
            'stubhub.com': {'name': 'StubHub', 'classification': 'ticketing_platform'},
            'statista.com': {'name': 'Statista', 'classification': 'statistics_data'},
            'youtube.com': {'name': 'YouTube', 'classification': 'social_media'},
            'instagram.com': {'name': 'Instagram', 'classification': 'social_media'},
            'reddit.com': {'name': 'Reddit', 'classification': 'social_media'}
        }
    
    def run_audit(self) -> Dict[str, str]:
        """
        Execute complete audit across all queries and platforms
        Returns paths to generated output files
        """
        logger.info(f"\n{'='*80}")
        logger.info("NBA FAN ENGAGEMENT AEO ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Queries: {len(self.queries)}")
        logger.info(f"Platforms: {len(self.platforms)}")
        logger.info(f"Total Tests: {len(self.queries) * len(self.platforms)}")
        logger.info(f"{'='*80}\n")
        
        total_tests = len(self.queries) * len(self.platforms)
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            query_type = query_info["type"]
            commercial_intent = query_info["commercial_intent"]
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Type: {query_type} | Intent: {commercial_intent}")
            logger.info(f"{'='*80}")
            
            for platform_name, platform in self.platforms.items():
                completed += 1
                logger.info(f"\n[{completed}/{total_tests}] Testing on {platform_name}...")
                
                try:
                    # Get response from platform
                    result = self._query_platform(platform, platform_name, query_text)
                    
                    if result:
                        # Analyze response
                        analysis = self._analyze_response(
                            result['response_text'],
                            result['citations'],
                            query_text,
                            query_type,
                            commercial_intent,
                            platform_name
                        )
                        
                        # Store results
                        self.engagement_matrix_data.append(analysis['matrix_row'])
                        self.citation_details_data.extend(analysis['citation_rows'])
                        self.competitive_analysis_data.extend(analysis['competitive_rows'])
                        
                        # Track media sources
                        self._track_media_sources(
                            result['citations'],
                            query_text,
                            platform_name
                        )
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error testing {query_text} on {platform_name}: {e}")
                    continue
        
        # Generate output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("NBA FAN ENGAGEMENT AUDIT COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info("Generated files:")
        for key, path in output_files.items():
            logger.info(f"  ✓ {key}")
            logger.info(f"    {path}")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _query_platform(self, platform, platform_name: str, query: str) -> Dict[str, Any]:
        """Query a platform and return structured results"""
        try:
            # Get citations
            citations = platform.get_citations(query)
            
            # Get full response text
            response_text = self._get_full_response(platform_name, query)
            
            return {
                'response_text': response_text,
                'citations': citations,
                'platform': platform_name
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {e}")
            return None
    
    def _get_full_response(self, platform_name: str, query: str) -> str:
        """Get full response text from platform"""
        try:
            if platform_name == 'ChatGPT':
                return self._get_chatgpt_response(query)
            elif platform_name == 'Claude':
                return self._get_claude_response(query)
            elif platform_name == 'Perplexity':
                return self._get_perplexity_response(query)
            elif platform_name == 'Gemini':
                return self._get_gemini_response(query)
            return ""
        except Exception as e:
            logger.error(f"Error getting response from {platform_name}: {e}")
            return ""
    
    def _get_chatgpt_response(self, query: str) -> str:
        """Get ChatGPT response"""
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
            return response.json()['choices'][0]['message']['content']
        return ""
    
    def _get_claude_response(self, query: str) -> str:
        """Get Claude response"""
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
    
    def _get_perplexity_response(self, query: str) -> str:
        """Get Perplexity response"""
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
            return response.json()['choices'][0]['message']['content']
        return ""
    
    def _get_gemini_response(self, query: str) -> str:
        """Get Gemini response"""
        api_key = os.getenv('GOOGLE_API_KEY')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
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
    
    def _analyze_response(
        self,
        response_text: str,
        citations: List[Dict],
        query: str,
        query_type: str,
        commercial_intent: str,
        platform: str
    ) -> Dict[str, Any]:
        """Analyze response for league mentions and commercial intent"""
        
        # Check league mentions in response
        leagues = self._check_league_mentions(response_text)
        
        # Determine featured league and NBA prominence
        featured_league = self._determine_featured_league(response_text, leagues)
        nba_prominence = self._determine_nba_prominence(response_text, leagues, featured_league)
        
        # Check for actionable NBA information
        has_actionable_info = self._has_nba_actionable_info(response_text, commercial_intent)
        
        # Analyze citations
        citation_analysis = self._analyze_citations(citations, query, query_type, commercial_intent, platform)
        
        # Build matrix row
        matrix_row = {
            'query': query,
            'query_type': query_type,
            'commercial_intent': commercial_intent,
            'engine': platform,
            'nba_mentioned_in_response': "Yes" if 'NBA' in leagues else "No",
            'nfl_mentioned': "Yes" if 'NFL' in leagues else "No",
            'mlb_mentioned': "Yes" if 'MLB' in leagues else "No",
            'nhl_mentioned': "Yes" if 'NHL' in leagues else "No",
            'mls_mentioned': "Yes" if 'MLS' in leagues else "No",
            'other_leagues_mentioned': ",".join(self._detect_other_leagues(response_text)),
            'featured_league': featured_league,
            'nba_prominence': nba_prominence,
            'contains_nba_actionable_info': "Yes" if has_actionable_info else "No",
            'total_citations': len(citations),
            'citations_mentioning_nba': citation_analysis['nba_citations'],
            'citations_mentioning_nfl': citation_analysis['nfl_citations'],
            'citations_mentioning_mlb': citation_analysis['mlb_citations'],
            'citations_mentioning_nhl': citation_analysis['nhl_citations']
        }
        
        # Build competitive rows
        competitive_rows = self._build_competitive_rows(
            response_text, leagues, query, query_type, commercial_intent, platform
        )
        
        return {
            'matrix_row': matrix_row,
            'citation_rows': citation_analysis['citation_rows'],
            'competitive_rows': competitive_rows
        }
    
    def _check_league_mentions(self, text: str) -> Set[str]:
        """Check which leagues are mentioned in text"""
        if not text:
            return set()
        
        text_lower = text.lower()
        leagues = set()
        
        patterns = {
            'NBA': ['nba', 'national basketball association'],
            'NFL': ['nfl', 'national football league'],
            'MLB': ['mlb', 'major league baseball'],
            'NHL': ['nhl', 'national hockey league'],
            'MLS': ['mls', 'major league soccer']
        }
        
        for league, terms in patterns.items():
            if any(term in text_lower for term in terms):
                leagues.add(league)
        
        return leagues
    
    def _determine_featured_league(self, text: str, leagues: Set[str]) -> str:
        """Determine which league was featured first/most favorably"""
        if not text or not leagues:
            return "None"
        
        text_lower = text.lower()
        
        # Find first mention of each league
        positions = {}
        for league in leagues:
            pos = text_lower.find(league.lower())
            if pos != -1:
                positions[league] = pos
        
        if not positions:
            return "None"
        
        # Return league with earliest position
        return min(positions.items(), key=lambda x: x[1])[0]
    
    def _determine_nba_prominence(self, text: str, leagues: Set[str], featured_league: str) -> str:
        """Determine NBA's prominence in the response"""
        if 'NBA' not in leagues:
            return "Not_Present"
        
        if featured_league == 'NBA':
            # Check if it's exclusive or just first
            if len(leagues) == 1:
                return "Featured_First"
            else:
                return "Featured_First"
        
        # NBA mentioned but not first
        if len(leagues) == 1:
            return "Featured_First"
        
        # Check position in response
        text_lower = text.lower()
        nba_pos = text_lower.find('nba')
        
        # Split into sections
        first_third = len(text) // 3
        
        if nba_pos < first_third:
            return "Mentioned_After"
        else:
            return "Buried"
    
    def _has_nba_actionable_info(self, text: str, commercial_intent: str) -> bool:
        """Check if response contains actionable NBA information"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        if commercial_intent == 'streaming':
            streaming_terms = ['league pass', 'stream', 'watch', 'espn+', 'youtube tv', 'hulu']
            return any(term in text_lower for term in streaming_terms) and 'nba' in text_lower
        
        elif commercial_intent == 'ticketing':
            ticketing_terms = ['ticketmaster', 'stubhub', 'ticket', 'seats', 'buy']
            return any(term in text_lower for term in ticketing_terms) and 'nba' in text_lower
        
        elif commercial_intent == 'fan_acquisition':
            fan_terms = ['team', 'follow', 'watch', 'start', 'begin']
            return any(term in text_lower for term in fan_terms) and 'nba' in text_lower
        
        elif commercial_intent == 'brand_preference':
            return 'nba' in text_lower
        
        return False
    
    def _analyze_citations(
        self,
        citations: List[Dict],
        query: str,
        query_type: str,
        commercial_intent: str,
        platform: str
    ) -> Dict[str, Any]:
        """Analyze citations for league mentions"""
        
        citation_rows = []
        nba_count = 0
        nfl_count = 0
        mlb_count = 0
        nhl_count = 0
        
        for citation in citations:
            url = citation.get('url', '')
            domain = self._extract_domain(url)
            
            # Check league mentions in URL
            leagues_in_url = self._check_leagues_in_url(url)
            
            if 'NBA' in leagues_in_url:
                nba_count += 1
            if 'NFL' in leagues_in_url:
                nfl_count += 1
            if 'MLB' in leagues_in_url:
                mlb_count += 1
            if 'NHL' in leagues_in_url:
                nhl_count += 1
            
            # Build citation row
            citation_rows.append({
                'engine': platform,
                'query': query,
                'query_type': query_type,
                'commercial_intent': commercial_intent,
                'citation_url': url,
                'domain': domain,
                'domain_classification': self._classify_domain(url),
                'nba_mentioned_in_source': "Yes" if 'NBA' in leagues_in_url else "No",
                'nfl_mentioned_in_source': "Yes" if 'NFL' in leagues_in_url else "No",
                'mlb_mentioned_in_source': "Yes" if 'MLB' in leagues_in_url else "No",
                'nhl_mentioned_in_source': "Yes" if 'NHL' in leagues_in_url else "No",
                'content_type': self._classify_content_type(url),
                'primary_league_focus': self._determine_primary_focus(url, leagues_in_url)
            })
        
        return {
            'citation_rows': citation_rows,
            'nba_citations': nba_count,
            'nfl_citations': nfl_count,
            'mlb_citations': mlb_count,
            'nhl_citations': nhl_count
        }
    
    def _check_leagues_in_url(self, url: str) -> Set[str]:
        """Check which leagues are mentioned in URL"""
        if not url:
            return set()
        
        url_lower = url.lower()
        leagues = set()
        
        patterns = {
            'NBA': ['nba', 'basketball'],
            'NFL': ['nfl', 'football'],
            'MLB': ['mlb', 'baseball'],
            'NHL': ['nhl', 'hockey'],
            'MLS': ['mls', 'soccer']
        }
        
        for league, terms in patterns.items():
            if any(term in url_lower for term in terms):
                leagues.add(league)
        
        return leagues
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _classify_domain(self, url: str) -> str:
        """Classify domain type"""
        domain = self._extract_domain(url)
        
        # League official
        if any(league in domain for league in ['nba.com', 'nfl.com', 'mlb.com', 'nhl.com']):
            return 'league_official'
        
        # Sports media
        sports_media = ['espn.com', 'theathletic.com', 'bleacherreport.com', 'si.com']
        if any(d in domain for d in sports_media):
            return 'sports_media'
        
        # Business media
        business = ['forbes.com', 'bloomberg.com', 'cnbc.com']
        if any(d in domain for d in business):
            return 'business_media'
        
        # Tech media
        tech = ['techcrunch.com', 'theverge.com', 'wired.com']
        if any(d in domain for d in tech):
            return 'tech_media'
        
        # Lifestyle/culture
        lifestyle = ['gq.com', 'complex.com', 'esquire.com']
        if any(d in domain for d in lifestyle):
            return 'lifestyle_culture'
        
        # Statistics
        if 'statista' in domain or 'sports-reference' in domain:
            return 'statistics_data'
        
        # Ticketing
        if any(d in domain for d in ['ticketmaster', 'stubhub', 'seatgeek']):
            return 'ticketing_platform'
        
        # Streaming
        if any(d in domain for d in ['leaguepass', 'espn+', 'youtube', 'hulu']):
            return 'streaming_service'
        
        # Social media
        if any(d in domain for d in ['twitter', 'instagram', 'reddit', 'tiktok', 'facebook']):
            return 'social_media'
        
        # Reference
        if 'wikipedia' in domain:
            return 'reference'
        
        return 'other'
    
    def _classify_content_type(self, url: str) -> str:
        """Classify content type"""
        url_lower = url.lower()
        
        if any(word in url_lower for word in ['schedule', 'calendar']):
            return 'schedule'
        elif any(word in url_lower for word in ['stats', 'statistics']):
            return 'statistics'
        elif any(word in url_lower for word in ['video', 'watch', 'youtube']):
            return 'video'
        elif any(word in url_lower for word in ['news', 'article']):
            return 'news_article'
        elif any(word in url_lower for word in ['guide', 'how-to']):
            return 'guide'
        elif any(word in url_lower for word in ['social', 'post', 'tweet']):
            return 'social_post'
        elif 'official' in url_lower or any(league in url_lower for league in ['nba.com', 'nfl.com']):
            return 'official_announcement'
        else:
            return 'other'
    
    def _determine_primary_focus(self, url: str, leagues: Set[str]) -> str:
        """Determine primary league focus"""
        if not leagues:
            return "None"
        
        if len(leagues) == 1:
            return list(leagues)[0]
        
        # Check if URL is from official league site
        url_lower = url.lower()
        for league in leagues:
            if league.lower() in url_lower:
                return league
        
        return "Multi-Sport"
    
    def _detect_other_leagues(self, text: str) -> List[str]:
        """Detect other leagues beyond major US leagues"""
        if not text:
            return []
        
        text_lower = text.lower()
        other = []
        
        patterns = {
            'Premier League': 'premier league',
            'La Liga': 'la liga',
            'Serie A': 'serie a',
            'Bundesliga': 'bundesliga',
            'Champions League': 'champions league',
            'NCAA': 'ncaa'
        }
        
        for league, pattern in patterns.items():
            if pattern in text_lower:
                other.append(league)
        
        return other
    
    def _build_competitive_rows(
        self,
        response_text: str,
        leagues: Set[str],
        query: str,
        query_type: str,
        commercial_intent: str,
        platform: str
    ) -> List[Dict]:
        """Build competitive analysis rows"""
        rows = []
        
        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
            mentioned = league in leagues
            
            # Determine prominence vs NBA
            if league == 'NBA':
                prominence = "N/A"
                favorability = self._assess_favorability(response_text, 'NBA')
            else:
                prominence = self._compare_to_nba(response_text, league, 'NBA' in leagues)
                favorability = self._assess_favorability(response_text, league)
            
            rows.append({
                'query': query,
                'query_type': query_type,
                'commercial_intent': commercial_intent,
                'engine': platform,
                'league_mentioned': league,
                'mentioned_in_response': "Yes" if mentioned else "No",
                'mentioned_in_citations': "No",  # Will be filled from citation analysis
                'prominence_vs_nba': prominence,
                'recommendation_favorability': favorability
            })
        
        return rows
    
    def _compare_to_nba(self, text: str, league: str, nba_present: bool) -> str:
        """Compare league's prominence to NBA"""
        if not text:
            return "N/A"
        
        text_lower = text.lower()
        league_pos = text_lower.find(league.lower())
        nba_pos = text_lower.find('nba')
        
        if league_pos == -1 and nba_pos == -1:
            return "N/A"
        elif league_pos != -1 and nba_pos == -1:
            return "Featured_First"
        elif league_pos == -1 and nba_pos != -1:
            return "N/A"
        elif league_pos < nba_pos:
            return "Featured_First"
        elif league_pos > nba_pos:
            return "Mentioned_After"
        else:
            return "Equal"
    
    def _assess_favorability(self, text: str, league: str) -> str:
        """Assess recommendation favorability for a league"""
        if not text:
            return "Not_Mentioned"
        
        text_lower = text.lower()
        league_lower = league.lower()
        
        if league_lower not in text_lower:
            return "Not_Mentioned"
        
        # Look for positive indicators
        positive = ['best', 'top', 'leading', 'most popular', 'exciting', 'great', 'excellent']
        neutral = ['also', 'another', 'includes', 'such as']
        
        # Get context around league mention
        pos = text_lower.find(league_lower)
        context = text_lower[max(0, pos-50):min(len(text_lower), pos+50)]
        
        if any(word in context for word in positive):
            return "Most_Favorable"
        elif any(word in context for word in neutral):
            return "Neutral"
        else:
            return "Favorable"
    
    def _track_media_sources(self, citations: List[Dict], query: str, platform: str):
        """Track specific media outlets"""
        for citation in citations:
            url = citation.get('url', '')
            domain = self._extract_domain(url)
            
            # Check if this is a tracked media outlet
            for tracked_domain, info in self.tracked_media.items():
                if tracked_domain in domain:
                    self.media_tracking_data[tracked_domain]['total_citations'] += 1
                    self.media_tracking_data[tracked_domain]['queries_cited'].add(query)
                    self.media_tracking_data[tracked_domain]['engines_citing'].add(platform)
                    
                    # Check if NBA is mentioned in URL
                    leagues = self._check_leagues_in_url(url)
                    if 'NBA' in leagues:
                        self.media_tracking_data[tracked_domain]['nba_mentions'] += 1
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all 5 required output files"""
        output_dir = "case_studies/nba_analysis/fan_engagement"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. NBA_FAN_ENGAGEMENT_MATRIX
        matrix_path = f"{output_dir}/NBA_FAN_ENGAGEMENT_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'commercial_intent', 'engine',
                'nba_mentioned_in_response', 'nfl_mentioned', 'mlb_mentioned',
                'nhl_mentioned', 'mls_mentioned', 'other_leagues_mentioned',
                'featured_league', 'nba_prominence', 'contains_nba_actionable_info',
                'total_citations', 'citations_mentioning_nba', 'citations_mentioning_nfl',
                'citations_mentioning_mlb', 'citations_mentioning_nhl'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.engagement_matrix_data)
        files['engagement_matrix'] = matrix_path
        logger.info(f"✓ Generated: NBA_FAN_ENGAGEMENT_MATRIX_{timestamp}.csv")
        
        # 2. NBA_CITATION_DETAILS
        details_path = f"{output_dir}/NBA_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'query_type', 'commercial_intent', 'citation_url',
                'domain', 'domain_classification', 'nba_mentioned_in_source',
                'nfl_mentioned_in_source', 'mlb_mentioned_in_source', 
                'nhl_mentioned_in_source', 'content_type', 'primary_league_focus'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citation_details'] = details_path
        logger.info(f"✓ Generated: NBA_CITATION_DETAILS_{timestamp}.csv")
        
        # 3. NBA_COMPETITIVE_ANALYSIS
        competitive_path = f"{output_dir}/NBA_COMPETITIVE_ANALYSIS_{timestamp}.csv"
        with open(competitive_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'commercial_intent', 'engine', 'league_mentioned',
                'mentioned_in_response', 'mentioned_in_citations', 'prominence_vs_nba',
                'recommendation_favorability'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.competitive_analysis_data)
        files['competitive_analysis'] = competitive_path
        logger.info(f"✓ Generated: NBA_COMPETITIVE_ANALYSIS_{timestamp}.csv")
        
        # 4. NBA_MEDIA_SOURCE_TRACKING
        media_path = f"{output_dir}/NBA_MEDIA_SOURCE_TRACKING_{timestamp}.csv"
        with open(media_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'media_outlet', 'domain', 'total_citations', 'nba_mentions_in_citations',
                'queries_where_cited', 'engines_citing', 'classification'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for domain, data in self.media_tracking_data.items():
                if domain in self.tracked_media:
                    writer.writerow({
                        'media_outlet': self.tracked_media[domain]['name'],
                        'domain': domain,
                        'total_citations': data['total_citations'],
                        'nba_mentions_in_citations': data['nba_mentions'],
                        'queries_where_cited': ",".join(sorted(data['queries_cited'])),
                        'engines_citing': ",".join(sorted(data['engines_citing'])),
                        'classification': self.tracked_media[domain]['classification']
                    })
        files['media_tracking'] = media_path
        logger.info(f"✓ Generated: NBA_MEDIA_SOURCE_TRACKING_{timestamp}.csv")
        
        # 5. NBA_COMMERCIAL_INTENT_SUMMARY (JSON)
        summary_path = f"{output_dir}/NBA_COMMERCIAL_INTENT_SUMMARY_{timestamp}.json"
        summary = self._generate_summary_json(timestamp)
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files['summary_json'] = summary_path
        logger.info(f"✓ Generated: NBA_COMMERCIAL_INTENT_SUMMARY_{timestamp}.json")
        
        return files
    
    def _generate_summary_json(self, timestamp: str) -> Dict[str, Any]:
        """Generate comprehensive summary JSON"""
        
        # Overall metrics
        total_queries = len(self.queries)
        total_tests = len(self.engagement_matrix_data)
        
        # By intent category
        intent_stats = {}
        for intent in ['streaming', 'ticketing', 'fan_acquisition', 'brand_preference']:
            intent_rows = [r for r in self.engagement_matrix_data if r['commercial_intent'] == intent]
            nba_mentions = sum(1 for r in intent_rows if r['nba_mentioned_in_response'] == 'Yes')
            actionable = sum(1 for r in intent_rows if r['contains_nba_actionable_info'] == 'Yes')
            
            intent_stats[intent] = {
                'queries_tested': len(intent_rows),
                'nba_mention_rate': round((nba_mentions / len(intent_rows) * 100) if len(intent_rows) > 0 else 0, 2),
                'actionable_info_provided': actionable
            }
        
        # By platform
        platform_stats = {}
        for platform in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
            platform_rows = [r for r in self.engagement_matrix_data if r['engine'] == platform]
            nba_mentions = sum(1 for r in platform_rows if r['nba_mentioned_in_response'] == 'Yes')
            featured_first = sum(1 for r in platform_rows if r['nba_prominence'] == 'Featured_First')
            avg_citations = sum(r['total_citations'] for r in platform_rows) / len(platform_rows) if platform_rows else 0
            
            platform_stats[platform] = {
                'nba_mention_rate': round((nba_mentions / len(platform_rows) * 100) if len(platform_rows) > 0 else 0, 2),
                'featured_first_rate': round((featured_first / len(platform_rows) * 100) if len(platform_rows) > 0 else 0, 2),
                'avg_citations': round(avg_citations, 2)
            }
        
        # Competitive landscape
        nba_mentions = sum(1 for r in self.engagement_matrix_data if r['nba_mentioned_in_response'] == 'Yes')
        nfl_mentions = sum(1 for r in self.engagement_matrix_data if r['nfl_mentioned'] == 'Yes')
        mlb_mentions = sum(1 for r in self.engagement_matrix_data if r['mlb_mentioned'] == 'Yes')
        nhl_mentions = sum(1 for r in self.engagement_matrix_data if r['nhl_mentioned'] == 'Yes')
        mls_mentions = sum(1 for r in self.engagement_matrix_data if r['mls_mentioned'] == 'Yes')
        
        # Citation analysis
        total_citations = sum(r['total_citations'] for r in self.engagement_matrix_data)
        citations_with_nba = sum(r['citations_mentioning_nba'] for r in self.engagement_matrix_data)
        
        # Streaming visibility
        streaming_queries = [r for r in self.engagement_matrix_data if r['commercial_intent'] == 'streaming']
        league_pass_mentions = sum(1 for r in streaming_queries if 'league pass' in str(r).lower())
        
        # Ticketing visibility
        ticketing_citations = [r for r in self.citation_details_data 
                              if r['commercial_intent'] == 'ticketing' and r['domain_classification'] == 'ticketing_platform']
        
        # Top cited domains
        domain_counts = defaultdict(int)
        for citation in self.citation_details_data:
            domain_counts[citation['domain']] += 1
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'analysis_date': datetime.now().isoformat(),
            'total_queries': total_queries,
            'total_tests': total_tests,
            'by_intent_category': intent_stats,
            'by_platform': platform_stats,
            'competitive_landscape': {
                'nba_mentions': nba_mentions,
                'nfl_mentions': nfl_mentions,
                'mlb_mentions': mlb_mentions,
                'nhl_mentions': nhl_mentions,
                'mls_mentions': mls_mentions
            },
            'citation_analysis': {
                'total_citations': total_citations,
                'citations_with_nba': citations_with_nba,
                'citations_with_streaming_info': len([c for c in self.citation_details_data 
                                                     if c['domain_classification'] == 'streaming_service']),
                'citations_with_ticketing_info': len(ticketing_citations),
                'top_cited_domains': [{'domain': d, 'count': c} for d, c in top_domains]
            },
            'streaming_visibility': {
                'league_pass_mentioned': league_pass_mentions,
                'partner_platforms_mentioned': [],
                'streaming_guide_citations': len([c for c in self.citation_details_data 
                                                 if c['content_type'] == 'guide' and c['commercial_intent'] == 'streaming'])
            },
            'ticketing_visibility': {
                'ticketing_platforms_cited': list(set(c['domain'] for c in ticketing_citations)),
                'ticket_purchase_guidance': len(ticketing_citations)
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
        logger.info("\n" + "="*80)
        logger.info("NBA FAN ENGAGEMENT AEO ANALYSIS")
        logger.info("Focus: Streaming, Ticketing, Fan Acquisition")
        logger.info("="*80 + "\n")
        
        auditor = NBAFanEngagementAuditor()
        output_files = auditor.run_audit()
        
        logger.info("\n" + "="*80)
        logger.info("✓ NBA FAN ENGAGEMENT AUDIT COMPLETE!")
        logger.info("="*80)
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  • {file_path}")
        logger.info("\n" + "="*80 + "\n")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

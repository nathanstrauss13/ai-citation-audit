#!/usr/bin/env python3
"""
Enhanced Sports League AEO Analysis
Comprehensive multi-league comparison with improved methodology
Addresses data quality concerns from previous analysis

Features:
- Multi-key Gemini load balancing (3 API keys)
- Consistency testing (3 runs for critical queries)
- Content fetching with sentiment analysis
- GPT-4 with enhanced citation prompts
- 24 queries + 6 competitive baseline
- 5 enhanced output files
"""

import os
import sys
import json
import csv
import logging
import requests
import time
import re
import random
from datetime import datetime
from typing import List, Dict, Any, Set, Optional, Tuple
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup

# Import platform adapters
from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiKeyManager:
    """Manages multiple Gemini API keys with load balancing and failure tracking"""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.key_failure_counts = {key: 0 for key in api_keys}
        self.key_success_counts = {key: 0 for key in api_keys}
        self.key_last_used = {key: 0 for key in api_keys}
        logger.info(f"GeminiKeyManager initialized with {len(api_keys)} API keys")
    
    def get_next_key(self) -> str:
        """Get next available key using round-robin with failure awareness"""
        # Skip keys with high failure rates
        available_keys = [key for key in self.api_keys 
                         if self.key_failure_counts[key] < 5]
        
        if not available_keys:
            # Reset failure counts if all keys exhausted
            logger.warning("All Gemini keys exhausted, resetting failure counts")
            self.key_failure_counts = {key: 0 for key in self.api_keys}
            available_keys = self.api_keys
        
        # Round-robin through available keys
        key = available_keys[self.current_key_index % len(available_keys)]
        self.current_key_index += 1
        self.key_last_used[key] = time.time()
        
        return key
    
    def mark_success(self, key: str):
        """Mark successful use of a key"""
        self.key_success_counts[key] += 1
        # Reduce failure count on success
        if self.key_failure_counts[key] > 0:
            self.key_failure_counts[key] = max(0, self.key_failure_counts[key] - 1)
    
    def mark_failure(self, key: str):
        """Mark failed use of a key"""
        self.key_failure_counts[key] += 1
        logger.warning(f"Gemini key failure count: {self.key_failure_counts[key]}/5")
    
    def get_stats(self) -> Dict:
        """Get performance statistics for all keys"""
        stats = {}
        for i, key in enumerate(self.api_keys, 1):
            key_id = f"key_{i}_(...{key[-8:]})"
            total = self.key_success_counts[key] + self.key_failure_counts[key]
            success_rate = (self.key_success_counts[key] / total * 100) if total > 0 else 0
            stats[key_id] = {
                'successes': self.key_success_counts[key],
                'failures': self.key_failure_counts[key],
                'success_rate': round(success_rate, 2)
            }
        return stats


class ContentFetcher:
    """Fetches and analyzes web content from citation URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0; +http://example.com/bot)'
        })
        self.fetch_count = 0
        self.success_count = 0
    
    def fetch_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from URL with timeout"""
        try:
            self.fetch_count += 1
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            self.success_count += 1
            return text[:10000]  # Limit to first 10K characters
            
        except Exception as e:
            logger.debug(f"Content fetch failed for {url}: {e}")
            return None
    
    def analyze_league_sentiment(self, content: str, league: str) -> str:
        """Analyze sentiment for a specific league in content"""
        if not content:
            return "unknown"
        
        content_lower = content.lower()
        league_lower = league.lower()
        
        # Check if league is mentioned
        if league_lower not in content_lower:
            return "not_mentioned"
        
        # Find contexts where league is mentioned
        pattern = re.compile(f'.{{0,100}}{league_lower}.{{0,100}}', re.IGNORECASE)
        contexts = pattern.findall(content)
        
        if not contexts:
            return "neutral"
        
        # Simple sentiment analysis
        positive_words = ['best', 'great', 'excellent', 'leading', 'top', 'popular', 'exciting', 
                         'amazing', 'outstanding', 'premier', 'dominant', 'successful']
        negative_words = ['worst', 'poor', 'declining', 'struggling', 'failing', 'problematic',
                         'controversial', 'criticized', 'issues', 'concerns']
        
        positive_count = 0
        negative_count = 0
        
        for context in contexts:
            context_lower = context.lower()
            positive_count += sum(1 for word in positive_words if word in context_lower)
            negative_count += sum(1 for word in negative_words if word in context_lower)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"
    
    def get_stats(self) -> Dict:
        """Get fetching statistics"""
        success_rate = (self.success_count / self.fetch_count * 100) if self.fetch_count > 0 else 0
        return {
            'total_attempts': self.fetch_count,
            'successful': self.success_count,
            'success_rate': round(success_rate, 2)
        }


class EnhancedSportsLeagueAuditor:
    """
    Comprehensive sports league auditor with improved methodology
    """
    
    def __init__(self, gemini_keys: List[str]):
        # Initialize Gemini key manager
        self.gemini_key_manager = GeminiKeyManager(gemini_keys)
        
        # Initialize content fetcher
        self.content_fetcher = ContentFetcher()
        
        # Initialize platforms
        self.platforms = {
            'ChatGPT': ChatGPTPlatform(),
            'Claude': ClaudePlatform(),
            'Perplexity': PerplexityPlatform()
            # Gemini handled separately with key manager
        }
        
        # Define queries
        self.queries = self._define_queries()
        
        # Storage for results
        self.analysis_matrix_data = []
        self.competitive_context_data = []
        self.citation_details_data = []
        self.consistency_data = []
        self.fetched_content = {}  # Cache for fetched content
        
        # Track Gemini usage
        self.gemini_attempts = 0
        self.gemini_successes = 0
        self.gemini_primary_model_used = 0
        self.gemini_fallback_model_used = 0
        
        logger.info("Enhanced Sports League Auditor initialized")
    
    def _define_queries(self) -> List[Dict[str, Any]]:
        """Define all 24 queries + consistency test flags"""
        queries = []
        
        # BRANDED QUERIES (6 - NBA specific)
        branded = [
            ("How do I watch NBA games?", "streaming", True),  # consistency test
            ("Where can I stream NBA games live?", "streaming", False),
            ("How do I get tickets to NBA games?", "ticketing", False),
            ("Best NBA games to attend this season", "ticketing", False),
            ("How do I become an NBA fan?", "fan_acquisition", False),
            ("What NBA team should I root for?", "fan_acquisition", False)
        ]
        for text, intent, consistency in branded:
            queries.append({
                "text": text,
                "type": "branded",
                "league": "NBA",
                "commercial_intent": intent,
                "consistency_test": consistency
            })
        
        # LEAGUE-AGNOSTIC QUERIES (12)
        agnostic = [
            ("What's the best professional sports league to watch?", "brand_preference", True),
            ("Which sports have the best streaming options?", "streaming", False),
            ("Most exciting sports to watch live?", "brand_preference", True),
            ("Which sports league has the most passionate fans?", "brand_preference", True),
            ("Easiest professional sport to get into as a new fan", "fan_acquisition", False),
            ("Best sports league for international fans", "fan_acquisition", False),
            ("Which sports leagues have the biggest cultural impact?", "brand_preference", False),
            ("Most socially engaged sports leagues", "brand_preference", False),
            ("Sports leagues with the best athletes", "brand_preference", False),
            ("Best professional sports for families to watch", "fan_acquisition", False),
            ("Which sports are most fun to play and watch?", "brand_preference", False),
            ("Fastest growing sports leagues in the world", "brand_preference", False)
        ]
        for text, intent, consistency in agnostic:
            queries.append({
                "text": text,
                "type": "league_agnostic",
                "league": "None",
                "commercial_intent": intent,
                "consistency_test": consistency
            })
        
        # COMPETITIVE BASELINE QUERIES (6)
        baseline = [
            ("How do I watch NFL games?", "streaming", "NFL"),
            ("How do I get tickets to NFL games?", "ticketing", "NFL"),
            ("How do I watch MLB games?", "streaming", "MLB"),
            ("How do I get tickets to MLB games?", "ticketing", "MLB"),
            ("How do I watch NHL games?", "streaming", "NHL"),
            ("How do I get tickets to NHL games?", "ticketing", "NHL")
        ]
        for text, intent, league in baseline:
            queries.append({
                "text": text,
                "type": "competitive_baseline",
                "league": league,
                "commercial_intent": intent,
                "consistency_test": False
            })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """Execute complete enhanced audit"""
        logger.info(f"\n{'='*80}")
        logger.info("ENHANCED SPORTS LEAGUE AEO ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Total Queries: {len(self.queries)}")
        logger.info(f"Platforms: {len(self.platforms) + 1} (including Gemini)")
        logger.info(f"Base Tests: {len(self.queries) * (len(self.platforms) + 1)}")
        
        # Count consistency tests
        consistency_queries = [q for q in self.queries if q['consistency_test']]
        consistency_tests = len(consistency_queries) * 4 * 2  # 4 platforms × 2 additional runs
        logger.info(f"Consistency Tests: {consistency_tests}")
        logger.info(f"Total Tests: {len(self.queries) * 4 + consistency_tests}")
        logger.info(f"{'='*80}\n")
        
        # Phase 1: Base query execution
        logger.info("PHASE 1: Base Query Execution")
        self._execute_base_queries()
        
        # Phase 2: Consistency testing
        logger.info("\nPHASE 2: Consistency Testing")
        self._execute_consistency_tests()
        
        # Phase 3: Content fetching for top citations
        logger.info("\nPHASE 3: Citation Content Analysis")
        self._fetch_top_citations()
        
        # Phase 4: Generate output files
        logger.info("\nPHASE 4: Generating Output Files")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("ENHANCED AUDIT COMPLETE!")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _execute_base_queries(self):
        """Execute all base queries across all platforms"""
        total = len(self.queries) * 4
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            query_type = query_info["type"]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Type: {query_type}")
            logger.info(f"{'='*60}")
            
            # Test on all platforms
            for platform_name in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
                completed += 1
                logger.info(f"\n[{completed}/{total}] Testing on {platform_name}...")
                
                try:
                    result = self._query_platform(platform_name, query_text, run_number=1)
                    
                    if result:
                        analysis = self._analyze_response(
                            result, query_info, platform_name, run_number=1
                        )
                        self.analysis_matrix_data.append(analysis['matrix_row'])
                        self.citation_details_data.extend(analysis['citation_rows'])
                        self.competitive_context_data.extend(analysis['competitive_rows'])
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
    
    def _execute_consistency_tests(self):
        """Execute additional runs for consistency testing"""
        consistency_queries = [q for q in self.queries if q['consistency_test']]
        
        logger.info(f"Running consistency tests for {len(consistency_queries)} critical queries")
        
        for query_info in consistency_queries:
            query_text = query_info["text"]
            
            logger.info(f"\nConsistency Test: {query_text}")
            
            for platform_name in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
                # Run 2 additional times (already have run 1 from base)
                for run_num in [2, 3]:
                    logger.info(f"  {platform_name} - Run {run_num}/3")
                    
                    try:
                        result = self._query_platform(platform_name, query_text, run_number=run_num)
                        
                        if result:
                            analysis = self._analyze_response(
                                result, query_info, platform_name, run_number=run_num
                            )
                            self.analysis_matrix_data.append(analysis['matrix_row'])
                            # Don't duplicate citations/competitive data
                        
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        logger.error(f"Consistency test error: {e}")
                        continue
        
        # Calculate consistency scores
        self._calculate_consistency_scores()
    
    def _query_platform(self, platform_name: str, query: str, run_number: int = 1) -> Optional[Dict]:
        """Query a specific platform"""
        try:
            if platform_name == 'Gemini':
                return self._query_gemini(query)
            elif platform_name == 'ChatGPT':
                return self._query_chatgpt_enhanced(query)
            else:
                platform = self.platforms[platform_name]
                citations = platform.get_citations(query)
                response_text = self._get_response_text(platform_name, query)
                
                return {
                    'response_text': response_text,
                    'citations': citations,
                    'platform': platform_name
                }
        except Exception as e:
            logger.error(f"Platform query error: {e}")
            return None
    
    def _query_gemini(self, query: str) -> Optional[Dict]:
        """Query Gemini with multi-key support and fallback"""
        self.gemini_attempts += 1
        max_key_attempts = len(self.gemini_key_manager.api_keys)
        
        for key_attempt in range(max_key_attempts):
            current_key = self.gemini_key_manager.get_next_key()
            
            # Try primary model
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={current_key}"
                
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
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        self.gemini_key_manager.mark_success(current_key)
                        self.gemini_successes += 1
                        self.gemini_primary_model_used += 1
                        
                        # Extract citations (Gemini doesn't natively provide them)
                        citations = self._extract_citations_from_text(text)
                        
                        return {
                            'response_text': text,
                            'citations': citations,
                            'platform': 'Gemini',
                            'model': 'gemini-2.0-flash-exp',
                            'api_key_used': current_key[-8:]
                        }
                
            except Exception as e:
                logger.debug(f"Gemini primary model failed: {e}")
            
            # Try fallback model
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent?key={current_key}"
                
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": query}]}],
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
                    },
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        self.gemini_key_manager.mark_success(current_key)
                        self.gemini_successes += 1
                        self.gemini_fallback_model_used += 1
                        
                        citations = self._extract_citations_from_text(text)
                        
                        return {
                            'response_text': text,
                            'citations': citations,
                            'platform': 'Gemini',
                            'model': 'gemini-1.5-pro-002',
                            'api_key_used': current_key[-8:]
                        }
                        
            except Exception as e:
                self.gemini_key_manager.mark_failure(current_key)
                logger.debug(f"Gemini fallback failed: {e}")
                
                if key_attempt < max_key_attempts - 1:
                    time.sleep(random.uniform(2, 5))
                    continue
        
        logger.warning("All Gemini keys exhausted for this query")
        return None
    
    def _query_chatgpt_enhanced(self, query: str) -> Optional[Dict]:
        """Query ChatGPT with GPT-4 and enhanced citation prompt"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            
            # Enhanced system prompt for better citations
            system_prompt = """You are a helpful assistant. For every factual claim you make, provide specific numbered citations with full URLs. Format all citations as a numbered list at the end of your response. Only cite sources you would actually reference for the information provided."""
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",  # Using GPT-4
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                citations = self._extract_citations_from_text(text)
                
                return {
                    'response_text': text,
                    'citations': citations,
                    'platform': 'ChatGPT',
                    'model': 'gpt-4o'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"ChatGPT enhanced query error: {e}")
            return None
    
    def _get_response_text(self, platform_name: str, query: str) -> str:
        """Get response text for non-Gemini platforms"""
        try:
            if platform_name == 'Claude':
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
                    
            elif platform_name == 'Perplexity':
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
            
        except Exception as e:
            logger.error(f"Response text error: {e}")
            return ""
    
    def _extract_citations_from_text(self, text: str) -> List[Dict]:
        """Extract citation URLs from response text"""
        citations = []
        
        # Pattern for URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            # Clean up URL
            url = url.rstrip('.,;:)')
            citations.append({'url': url})
        
        return citations
    
    def _analyze_response(self, result: Dict, query_info: Dict, platform: str, run_number: int) -> Dict:
        """Analyze response for league mentions and patterns"""
        
        response_text = result['response_text']
        citations = result['citations']
        
        # Check league mentions
        leagues_mentioned = self._check_league_mentions(response_text)
        
        # Determine featured league
        featured_league = self._determine_featured_league(response_text, leagues_mentioned)
        
        # Build matrix row
        matrix_row = {
            'query': query_info['text'],
            'query_type': query_info['type'],
            'commercial_intent': query_info['commercial_intent'],
            'engine': platform,
            'run_number': run_number,
            'nba_mentioned': "Yes" if 'NBA' in leagues_mentioned else "No",
            'nfl_mentioned': "Yes" if 'NFL' in leagues_mentioned else "No",
            'mlb_mentioned': "Yes" if 'MLB' in leagues_mentioned else "No",
            'nhl_mentioned': "Yes" if 'NHL' in leagues_mentioned else "No",
            'featured_league': featured_league,
            'nba_prominence': self._determine_prominence(response_text, 'NBA', featured_league),
            'consistency_score': 0.0,  # Will be calculated later
            'total_citations': len(citations),
            'nba_citations': 0,
            'nfl_citations': 0,
            'mlb_citations': 0,
            'nhl_citations': 0
        }
        
        # Analyze citations
        citation_rows = []
        for citation in citations:
            url = citation.get('url', '')
            citation_leagues = self._check_leagues_in_url(url)
            
            # Update citation counts
            if 'NBA' in citation_leagues:
                matrix_row['nba_citations'] += 1
            if 'NFL' in citation_leagues:
                matrix_row['nfl_citations'] += 1
            if 'MLB' in citation_leagues:
                matrix_row['mlb_citations'] += 1
            if 'NHL' in citation_leagues:
                matrix_row['nhl_citations'] += 1
            
            citation_rows.append({
                'engine': platform,
                'query': query_info['text'],
                'citation_url': url,
                'domain': self._extract_domain(url),
                'domain_classification': self._classify_domain(url),
                'fetch_success': False,
                'content_available': False,
                'nba_mentioned_in_source': "Yes" if 'NBA' in citation_leagues else "No",
                'nfl_mentioned_in_source': "Yes" if 'NFL' in citation_leagues else "No",
                'mlb_mentioned_in_source': "Yes" if 'MLB' in citation_leagues else "No",
                'nhl_mentioned_in_source': "Yes" if 'NHL' in citation_leagues else "No",
                'primary_league_focus': self._determine_primary_focus(url, citation_leagues),
                'article_type': self._classify_content_type(url),
                'content_summary': None
            })
        
        # Build competitive context rows
        competitive_rows = []
        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
            competitive_rows.append({
                'league': league,
                'query': query_info['text'],
                'query_type': query_info['type'],
                'engine': platform,
                'mentioned_in_response': "Yes" if league in leagues_mentioned else "No",
                'prominence_ranking': self._get_prominence_rank(response_text, league, leagues_mentioned),
                'actionable_info_provided': self._has_actionable_info(response_text, league),
                'total_citations': len(citations),
                'cross_league_mentions': len(leagues_mentioned)
            })
        
        return {
            'matrix_row': matrix_row,
            'citation_rows': citation_rows,
            'competitive_rows': competitive_rows
        }
    
    def _check_league_mentions(self, text: str) -> Set[str]:
        """Check which leagues are mentioned"""
        if not text:
            return set()
        
        text_lower = text.lower()
        leagues = set()
        
        patterns = {
            'NBA': ['nba', 'national basketball association'],
            'NFL': ['nfl', 'national football league'],
            'MLB': ['mlb', 'major league baseball'],
            'NHL': ['nhl', 'national hockey league']
        }
        
        for league, terms in patterns.items():
            if any(term in text_lower for term in terms):
                leagues.add(league)
        
        return leagues
    
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
            'NHL': ['nhl', 'hockey']
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
        
        if any(league in domain for league in ['nba.com', 'nfl.com', 'mlb.com', 'nhl.com']):
            return 'league_official'
        
        sports_media = ['espn.com', 'theathletic.com', 'bleacherreport.com', 'si.com']
        if any(d in domain for d in sports_media):
            return 'sports_media'
        
        if any(d in domain for d in ['ticketmaster', 'stubhub', 'seatgeek']):
            return 'ticketing_platform'
        
        if 'statista' in domain or 'sports-reference' in domain:
            return 'statistics_data'
        
        return 'other'
    
    def _determine_primary_focus(self, url: str, leagues: Set[str]) -> str:
        """Determine primary league focus"""
        if not leagues:
            return "None"
        if len(leagues) == 1:
            return list(leagues)[0]
        return "Multi-Sport"
    
    def _classify_content_type(self, url: str) -> str:
        """Classify content type"""
        url_lower = url.lower()
        if any(word in url_lower for word in ['schedule', 'calendar']):
            return 'schedule'
        elif any(word in url_lower for word in ['stats', 'statistics']):
            return 'statistics'
        elif any(word in url_lower for word in ['video', 'watch']):
            return 'video'
        elif any(word in url_lower for word in ['news', 'article']):
            return 'news_article'
        return 'other'
    
    def _determine_featured_league(self, text: str, leagues: Set[str]) -> str:
        """Determine which league is featured first"""
        if not text or not leagues:
            return "None"
        
        text_lower = text.lower()
        positions = {}
        for league in leagues:
            pos = text_lower.find(league.lower())
            if pos != -1:
                positions[league] = pos
        
        if not positions:
            return "None"
        
        return min(positions.items(), key=lambda x: x[1])[0]
    
    def _determine_prominence(self, text: str, league: str, featured_league: str) -> str:
        """Determine league prominence"""
        if league not in self._check_league_mentions(text):
            return "Not_Present"
        if featured_league == league:
            return "Featured_First"
        return "Mentioned_After"
    
    def _get_prominence_rank(self, text: str, league: str, leagues: Set[str]) -> int:
        """Get prominence rank"""
        if league not in leagues:
            return 0
        
        text_lower = text.lower()
        positions = {}
        for l in leagues:
            pos = text_lower.find(l.lower())
            if pos != -1:
                positions[l] = pos
        
        sorted_leagues = sorted(positions.items(), key=lambda x: x[1])
        for i, (l, _) in enumerate(sorted_leagues, 1):
            if l == league:
                return i
        return 0
    
    def _has_actionable_info(self, text: str, league: str) -> str:
        """Check if response has actionable info for league"""
        if not text:
            return "No"
        
        text_lower = text.lower()
        league_lower = league.lower()
        
        if league_lower not in text_lower:
            return "No"
        
        actionable_terms = ['watch', 'stream', 'ticket', 'buy', 'subscribe', 'visit', 'go to']
        if any(term in text_lower for term in actionable_terms):
            return "Yes"
        
        return "No"
    
    def _calculate_consistency_scores(self):
        """Calculate consistency scores for multiple runs"""
        # Group by query and platform
        query_platform_runs = defaultdict(list)
        
        for row in self.analysis_matrix_data:
            if row['run_number'] > 0:
                key = (row['query'], row['engine'])
                query_platform_runs[key].append(row)
        
        # Calculate consistency for each query/platform combination
        for (query, platform), runs in query_platform_runs.items():
            if len(runs) >= 3:
                featured_leagues = [r['featured_league'] for r in runs]
                # Calculate agreement
                most_common = max(set(featured_leagues), key=featured_leagues.count)
                consistency = featured_leagues.count(most_common) / len(featured_leagues)
                
                # Update all runs with consistency score
                for row in runs:
                    row['consistency_score'] = round(consistency, 2)
                
                # Store in consistency data
                self.consistency_data.append({
                    'query': query,
                    'engine': platform,
                    'run_1_featured_league': featured_leagues[0] if len(featured_leagues) > 0 else "None",
                    'run_2_featured_league': featured_leagues[1] if len(featured_leagues) > 1 else "None",
                    'run_3_featured_league': featured_leagues[2] if len(featured_leagues) > 2 else "None",
                    'consistency_score': round(consistency, 2),
                    'variance_type': "Low" if consistency >= 0.8 else "High"
                })
    
    def _fetch_top_citations(self):
        """Fetch content for top 50 most-cited URLs"""
        # Count URL frequency
        url_counts = defaultdict(int)
        for citation in self.citation_details_data:
            url_counts[citation['citation_url']] += 1
        
        # Get top 50
        top_urls = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        
        logger.info(f"Fetching content for top {len(top_urls)} cited URLs")
        
        for url, count in top_urls:
            if url in self.fetched_content:
                continue
            
            logger.info(f"  Fetching: {url} ({count} citations)")
            content = self.content_fetcher.fetch_content(url)
            
            if content:
                self.fetched_content[url] = content
                
                # Update citation rows with content analysis
                for citation in self.citation_details_data:
                    if citation['citation_url'] == url:
                        citation['fetch_success'] = True
                        citation['content_available'] = True
                        citation['content_summary'] = content[:200] + "..."
                        
                        # Analyze sentiment for each league
                        for league in ['NBA', 'NFL', 'MLB', 'NHL']:
                            sentiment = self.content_fetcher.analyze_league_sentiment(content, league)
                            citation[f'{league.lower()}_sentiment'] = sentiment
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all 5 output files"""
        output_dir = "case_studies/nba_analysis/enhanced_v2"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. ENHANCED_LEAGUE_ANALYSIS_MATRIX
        matrix_path = f"{output_dir}/ENHANCED_LEAGUE_ANALYSIS_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'commercial_intent', 'engine', 'run_number',
                'nba_mentioned', 'nfl_mentioned', 'mlb_mentioned', 'nhl_mentioned',
                'featured_league', 'nba_prominence', 'consistency_score',
                'total_citations', 'nba_citations', 'nfl_citations', 'mlb_citations', 'nhl_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.analysis_matrix_data)
        files['analysis_matrix'] = matrix_path
        logger.info(f"✓ Generated: ENHANCED_LEAGUE_ANALYSIS_MATRIX_{timestamp}.csv")
        
        # 2. COMPETITIVE_CONTEXT_MATRIX
        context_path = f"{output_dir}/COMPETITIVE_CONTEXT_MATRIX_{timestamp}.csv"
        with open(context_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'league', 'query', 'query_type', 'engine', 'mentioned_in_response',
                'prominence_ranking', 'actionable_info_provided', 'total_citations',
                'cross_league_mentions'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.competitive_context_data)
        files['competitive_context'] = context_path
        logger.info(f"✓ Generated: COMPETITIVE_CONTEXT_MATRIX_{timestamp}.csv")
        
        # 3. ENHANCED_CITATION_DETAILS
        details_path = f"{output_dir}/ENHANCED_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'citation_url', 'domain', 'domain_classification',
                'fetch_success', 'content_available', 'nba_mentioned_in_source',
                'nfl_mentioned_in_source', 'mlb_mentioned_in_source', 'nhl_mentioned_in_source',
                'primary_league_focus', 'article_type', 'content_summary',
                'nba_sentiment', 'nfl_sentiment', 'mlb_sentiment', 'nhl_sentiment'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citation_details'] = details_path
        logger.info(f"✓ Generated: ENHANCED_CITATION_DETAILS_{timestamp}.csv")
        
        # 4. CONSISTENCY_ANALYSIS
        consistency_path = f"{output_dir}/CONSISTENCY_ANALYSIS_{timestamp}.csv"
        with open(consistency_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'engine', 'run_1_featured_league', 'run_2_featured_league',
                'run_3_featured_league', 'consistency_score', 'variance_type'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.consistency_data)
        files['consistency'] = consistency_path
        logger.info(f"✓ Generated: CONSISTENCY_ANALYSIS_{timestamp}.csv")
        
        # 5. PLATFORM_RELIABILITY_REPORT (JSON)
        report_path = f"{output_dir}/PLATFORM_RELIABILITY_REPORT_{timestamp}.json"
        report = self._generate_reliability_report()
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        files['reliability_report'] = report_path
        logger.info(f"✓ Generated: PLATFORM_RELIABILITY_REPORT_{timestamp}.json")
        
        return files
    
    def _generate_reliability_report(self) -> Dict:
        """Generate comprehensive reliability report"""
        total_queries = len(self.queries)
        total_attempts = total_queries * 4
        
        # Platform success rates
        platform_success = defaultdict(int)
        for row in self.analysis_matrix_data:
            if row['run_number'] == 1:
                platform_success[row['engine']] += 1
        
        gemini_success_rate = (self.gemini_successes / self.gemini_attempts * 100) if self.gemini_attempts > 0 else 0
        
        return {
            'execution_summary': {
                'total_queries_attempted': total_attempts,
                'successful_completions': len([r for r in self.analysis_matrix_data if r['run_number'] == 1]),
                'platform_success_rates': {
                    'chatgpt': round(platform_success['ChatGPT'] / total_queries * 100, 2),
                    'claude': round(platform_success['Claude'] / total_queries * 100, 2),
                    'perplexity': round(platform_success['Perplexity'] / total_queries * 100, 2),
                    'gemini': round(gemini_success_rate, 2)
                }
            },
            'gemini_debugging': {
                'api_keys_used': len(self.gemini_key_manager.api_keys),
                'key_performance': self.gemini_key_manager.get_stats(),
                'primary_model_attempts': self.gemini_primary_model_used,
                'fallback_model_used': self.gemini_fallback_model_used,
                'total_failures': self.gemini_attempts - self.gemini_successes,
                'retry_success_rate': round(gemini_success_rate, 2),
                'parallel_key_effectiveness': "Effective" if gemini_success_rate > 80 else "Needs Improvement"
            },
            'citation_quality': {
                'total_citations': len(self.citation_details_data),
                'content_fetch_success_rate': round(self.content_fetcher.get_stats()['success_rate'], 2),
                'chatgpt_citation_reliability': "Enhanced with GPT-4",
                'top_domains_verified': len(self.fetched_content)
            }
        }


def main():
    """Main execution function"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get Gemini API keys
        gemini_keys = [
            os.getenv('GOOGLE_API_KEY'),
            "AIzaSyAjyRcAwv1zEv0GvgVE18Aelqo_f5E-23A",
            "AIzaSyDvHaUxZrE7xvvvUuqsDUkKUGzWf-nGxa8"
        ]
        
        # Verify all keys are present
        if not all(gemini_keys):
            logger.error("Missing Gemini API keys")
            sys.exit(1)
        
        # Verify other API keys
        required_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY']
        missing = [key for key in required_keys if not os.getenv(key)]
        
        if missing:
            logger.error(f"Missing API keys: {', '.join(missing)}")
            sys.exit(1)
        
        # Create auditor
        auditor = EnhancedSportsLeagueAuditor(gemini_keys)
        
        # Run audit
        output_files = auditor.run_audit()
        
        logger.info("\n✓ Enhanced Sports League Audit Complete!")
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  • {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

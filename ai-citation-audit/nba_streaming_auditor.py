#!/usr/bin/env python3
"""
NBA Streaming Options Citation Analysis
Amazon Prime Competitive Intelligence - Full Data Collection Protocol

Strategic Objective: Measure how AI platforms recommend NBA streaming options
to inform Amazon PR strategy for increasing Amazon Prime Video's share of voice.

Protocol:
- 10 queries (6 service-agnostic + 4 service-specific)
- 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini)
- 40 total prompts
- 3 CSV outputs: Query Matrix, Raw Citations, Media Tracking

Key Analysis:
- Service positioning (First/Prominent/Secondary/Buried/Not Present)
- Citation source intelligence (scraped URLs vs inferred sources)
- Media outlet tracking by tier (Premium, Network, Tech, Mainstream)
- Platform-specific recommendation patterns
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
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urlparse
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NBAStreamingAuditor:
    """
    NBA Streaming Citation Auditor for Amazon Prime Competitive Intelligence
    """
    
    def __init__(self):
        # Verify API keys
        self._verify_api_keys()
        
        # Define queries
        self.queries = self._define_queries()
        
        # Storage for results
        self.query_matrix_data = []
        self.raw_citations_data = []
        self.media_tracking = defaultdict(lambda: {
            'total_citations': 0,
            'scraped_count': 0,
            'inferred_count': 0,
            'services_favored': set(),
            'amazon_mention_count': 0,
            'leaguepass_mention_count': 0,
            'queries_appeared_in': set(),
            'engines_citing': set(),
            'sample_urls': []
        })
        
        # Citation counter
        self.citation_id_counter = 1
        
        # Tracked services
        self.services = [
            'NBA League Pass',
            'Amazon Prime Video',
            'YouTube TV',
            'Hulu Live TV'
        ]
        
        logger.info("NBA Streaming Auditor initialized")
    
    def _verify_api_keys(self):
        """Verify all required API keys are present"""
        required_keys = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'PERPLEXITY_API_KEY',
            'GOOGLE_API_KEY'
        ]
        
        missing = [key for key in required_keys if not os.getenv(key)]
        
        if missing:
            logger.error(f"Missing API keys: {', '.join(missing)}")
            sys.exit(1)
    
    def _define_queries(self) -> List[Dict[str, Any]]:
        """Define all 10 queries with metadata"""
        queries = []
        
        # Query Set A: Service-Agnostic Core Queries (6)
        service_agnostic = [
            "How can I stream NBA games online?",
            "What's the best way to watch NBA games without cable?",
            "NBA streaming options comparison",
            "Where to watch NBA games 2025-2026 season",
            "Best streaming service for NBA fans",
            "How to watch NBA games on streaming platforms"
        ]
        
        for i, text in enumerate(service_agnostic, 1):
            queries.append({
                'query_id': f'A{i}',
                'text': text,
                'query_type': 'service_agnostic'
            })
        
        # Query Set B: Service-Specific Queries (4)
        service_specific = [
            "How do I get NBA League Pass?",
            "Can I watch NBA games on Amazon Prime?",
            "Is NBA League Pass worth it compared to YouTube TV?",
            "Hulu vs NBA League Pass for watching basketball"
        ]
        
        for i, text in enumerate(service_specific, 1):
            queries.append({
                'query_id': f'B{i}',
                'text': text,
                'query_type': 'service_specific'
            })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """Execute complete NBA streaming audit"""
        logger.info(f"\n{'='*80}")
        logger.info("NBA STREAMING OPTIONS CITATION ANALYSIS")
        logger.info("Amazon Prime Competitive Intelligence")
        logger.info(f"{'='*80}")
        logger.info(f"Total Queries: {len(self.queries)}")
        logger.info(f"Platforms: 4 (ChatGPT, Claude, Perplexity, Gemini)")
        logger.info(f"Total Tests: {len(self.queries) * 4} prompts")
        logger.info(f"{'='*80}\n")
        
        # Execute all queries across all platforms
        total = len(self.queries) * 4
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info['text']
            query_id = query_info['query_id']
            query_type = query_info['query_type']
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Query {query_id}: {query_text}")
            logger.info(f"Type: {query_type}")
            logger.info(f"{'='*70}")
            
            # Test on all platforms
            for platform_name in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
                completed += 1
                logger.info(f"\n[{completed}/{total}] Testing on {platform_name}...")
                
                try:
                    result = self._query_platform(platform_name, query_text)
                    
                    if result:
                        self._analyze_response(
                            result, query_info, platform_name
                        )
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error on {platform_name}: {e}")
                    # Add empty row to maintain data consistency
                    self._add_empty_result(query_info, platform_name)
                    continue
        
        # Generate output files
        logger.info(f"\n{'='*80}")
        logger.info("Generating Output Files...")
        logger.info(f"{'='*80}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("NBA STREAMING AUDIT COMPLETE!")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _query_platform(self, platform: str, query: str) -> Optional[Dict]:
        """Query specific AI platform"""
        try:
            if platform == 'ChatGPT':
                return self._query_chatgpt(query)
            elif platform == 'Claude':
                return self._query_claude(query)
            elif platform == 'Perplexity':
                return self._query_perplexity(query)
            elif platform == 'Gemini':
                return self._query_gemini(query)
            
            return None
            
        except Exception as e:
            logger.error(f"{platform} query failed: {e}")
            return None
    
    def _query_chatgpt(self, query: str) -> Optional[Dict]:
        """Query ChatGPT (GPT-4)"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Provide specific, accurate information with citations where appropriate."},
                        {"role": "user", "content": query}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                
                return {
                    'response_text': text,
                    'platform': 'ChatGPT'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            return None
    
    def _query_claude(self, query: str) -> Optional[Dict]:
        """Query Claude"""
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
                
                return {
                    'response_text': text,
                    'platform': 'Claude'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return None
    
    def _query_perplexity(self, query: str) -> Optional[Dict]:
        """Query Perplexity"""
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
                    "max_tokens": 1000,
                    "return_citations": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                citations = data.get('citations', [])
                
                return {
                    'response_text': text,
                    'platform': 'Perplexity',
                    'citations': citations
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return None
    
    def _query_gemini(self, query: str) -> Optional[Dict]:
        """Query Gemini"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": query}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    
                    return {
                        'response_text': text,
                        'platform': 'Gemini'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    def _analyze_response(self, result: Dict, query_info: Dict, platform: str):
        """Analyze response for service mentions and citations"""
        response_text = result['response_text']
        query_id = query_info['query_id']
        query_text = query_info['text']
        query_type = query_info['query_type']
        
        # Check service mentions
        service_mentions = self._check_service_mentions(response_text)
        
        # Determine positions
        service_positions = self._determine_service_positions(
            response_text, service_mentions
        )
        
        # Determine primary recommendation
        primary_recommendation = self._determine_primary_recommendation(
            response_text, service_mentions, service_positions
        )
        
        # Extract citations
        citations = self._extract_citations(result, response_text, platform)
        
        # Count citations by type
        scraped_count = sum(1 for c in citations if c['citation_type'] == 'scraped_url')
        inferred_count = sum(1 for c in citations if c['citation_type'] == 'inferred_source')
        
        # Build query matrix row
        matrix_row = {
            'query_id': query_id,
            'query_text': query_text,
            'query_type': query_type,
            'engine': platform,
            'nba_leaguepass_mentioned': 'Yes' if 'NBA League Pass' in service_mentions else 'No',
            'nba_leaguepass_position': service_positions.get('NBA League Pass', 'Not Present'),
            'amazon_prime_mentioned': 'Yes' if 'Amazon Prime Video' in service_mentions else 'No',
            'amazon_prime_position': service_positions.get('Amazon Prime Video', 'Not Present'),
            'youtube_tv_mentioned': 'Yes' if 'YouTube TV' in service_mentions else 'No',
            'youtube_tv_position': service_positions.get('YouTube TV', 'Not Present'),
            'hulu_mentioned': 'Yes' if 'Hulu Live TV' in service_mentions else 'No',
            'hulu_position': service_positions.get('Hulu Live TV', 'Not Present'),
            'other_services_mentioned': self._get_other_services(response_text),
            'primary_recommendation': primary_recommendation,
            'total_citations': len(citations),
            'scraped_citations': scraped_count,
            'inferred_citations': inferred_count
        }
        
        self.query_matrix_data.append(matrix_row)
        
        logger.info(f"  Services mentioned: {', '.join(service_mentions) if service_mentions else 'None'}")
        logger.info(f"  Primary recommendation: {primary_recommendation}")
        logger.info(f"  Citations: {len(citations)} ({scraped_count} scraped, {inferred_count} inferred)")
        
        # Process citations
        for citation in citations:
            citation_row = {
                'citation_id': f'C{self.citation_id_counter:03d}',
                'query_id': query_id,
                'engine': platform,
                'citation_type': citation['citation_type'],
                'domain': citation['domain'],
                'classification': citation['classification'],
                'full_url': citation['url'],
                'service_supported': citation['service_supported'],
                'citation_context': citation['context']
            }
            
            self.raw_citations_data.append(citation_row)
            self.citation_id_counter += 1
            
            # Update media tracking
            if citation['domain']:
                media = self.media_tracking[citation['domain']]
                media['total_citations'] += 1
                
                if citation['citation_type'] == 'scraped_url':
                    media['scraped_count'] += 1
                else:
                    media['inferred_count'] += 1
                
                if citation['service_supported'] != 'General':
                    media['services_favored'].add(citation['service_supported'])
                
                if 'Amazon' in citation['service_supported']:
                    media['amazon_mention_count'] += 1
                if 'League Pass' in citation['service_supported']:
                    media['leaguepass_mention_count'] += 1
                
                media['queries_appeared_in'].add(query_id)
                media['engines_citing'].add(platform)
                
                if citation['url'] != 'INFERRED' and len(media['sample_urls']) < 3:
                    media['sample_urls'].append(citation['url'])
    
    def _check_service_mentions(self, text: str) -> Set[str]:
        """Check which services are mentioned in response"""
        if not text:
            return set()
        
        text_lower = text.lower()
        mentioned = set()
        
        # Check each service
        if 'nba league pass' in text_lower or 'league pass' in text_lower:
            mentioned.add('NBA League Pass')
        
        if 'amazon prime' in text_lower or 'prime video' in text_lower:
            mentioned.add('Amazon Prime Video')
        
        if 'youtube tv' in text_lower:
            mentioned.add('YouTube TV')
        
        if 'hulu' in text_lower and ('live' in text_lower or 'tv' in text_lower):
            mentioned.add('Hulu Live TV')
        
        return mentioned
    
    def _determine_service_positions(self, text: str, services: Set[str]) -> Dict[str, str]:
        """Determine position/prominence of each mentioned service"""
        if not text or not services:
            return {}
        
        text_lower = text.lower()
        positions = {}
        
        # Find first mention position for each service
        service_positions_raw = {}
        
        for service in services:
            search_terms = self._get_service_search_terms(service)
            first_pos = float('inf')
            
            for term in search_terms:
                pos = text_lower.find(term)
                if pos != -1 and pos < first_pos:
                    first_pos = pos
            
            if first_pos != float('inf'):
                service_positions_raw[service] = first_pos
        
        # Sort by position
        sorted_services = sorted(service_positions_raw.items(), key=lambda x: x[1])
        
        # Classify positions
        for i, (service, pos) in enumerate(sorted_services):
            if i == 0 and pos < 200:  # First mention in first 200 chars
                positions[service] = 'First'
            elif i < 3:  # Top 3 mentions
                positions[service] = 'Prominent'
            elif i < len(sorted_services) - 1:
                positions[service] = 'Secondary'
            else:
                positions[service] = 'Buried'
        
        return positions
    
    def _get_service_search_terms(self, service: str) -> List[str]:
        """Get search terms for a service"""
        terms_map = {
            'NBA League Pass': ['nba league pass', 'league pass'],
            'Amazon Prime Video': ['amazon prime video', 'amazon prime', 'prime video'],
            'YouTube TV': ['youtube tv'],
            'Hulu Live TV': ['hulu live tv', 'hulu + live tv', 'hulu live']
        }
        return terms_map.get(service, [service.lower()])
    
    def _determine_primary_recommendation(self, text: str, services: Set[str], 
                                         positions: Dict[str, str]) -> str:
        """Determine which service is primary recommendation"""
        if not services:
            return 'None'
        
        # Check for explicit recommendation language
        text_lower = text.lower()
        
        for service in services:
            service_terms = self._get_service_search_terms(service)
            
            for term in service_terms:
                # Look for recommendation context around service mention
                pattern = f'.{{0,100}}{re.escape(term)}.{{0,100}}'
                matches = re.findall(pattern, text_lower)
                
                for match in matches:
                    if any(word in match for word in ['best', 'recommend', 'top choice', 'ideal', 'excellent']):
                        return service
        
        # If no explicit recommendation, use first mentioned service
        first_services = [s for s, p in positions.items() if p == 'First']
        if first_services:
            return first_services[0]
        
        # Return most prominently featured
        prominent = [s for s, p in positions.items() if p in ['First', 'Prominent']]
        if prominent:
            return prominent[0]
        
        return 'Mixed' if len(services) > 1 else list(services)[0]
    
    def _get_other_services(self, text: str) -> str:
        """Get comma-separated list of other streaming services mentioned"""
        if not text:
            return ''
        
        text_lower = text.lower()
        other_services = []
        
        service_checks = {
            'Sling TV': ['sling tv', 'sling'],
            'FuboTV': ['fubotv', 'fubo tv', 'fubo'],
            'DirecTV Stream': ['directv stream', 'directv'],
            'ESPN+': ['espn+', 'espn plus']
        }
        
        for service, terms in service_checks.items():
            if any(term in text_lower for term in terms):
                other_services.append(service)
        
        return ','.join(other_services)
    
    def _extract_citations(self, result: Dict, text: str, platform: str) -> List[Dict]:
        """Extract all citations from response"""
        citations = []
        
        # Perplexity provides citations directly
        if platform == 'Perplexity' and 'citations' in result:
            for url in result['citations']:
                citation = self._analyze_citation(url, text, 'scraped_url')
                citations.append(citation)
        
        # Extract URLs from text (for all platforms)
        urls = self._extract_urls_from_text(text)
        for url in urls:
            citation = self._analyze_citation(url, text, 'scraped_url')
            citations.append(citation)
        
        # Extract inferred sources (common in Claude)
        inferred = self._extract_inferred_sources(text)
        for source in inferred:
            citation = self._analyze_citation(source, text, 'inferred_source')
            citations.append(citation)
        
        # Deduplicate
        seen_urls = set()
        unique_citations = []
        for c in citations:
            key = c['url']
            if key not in seen_urls:
                seen_urls.add(key)
                unique_citations.append(c)
        
        return unique_citations
    
    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text"""
        if not text:
            return []
        
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(pattern, text)
        
        # Clean up URLs
        cleaned = []
        for url in urls:
            url = url.rstrip('.,;:)')
            cleaned.append(url)
        
        return cleaned
    
    def _extract_inferred_sources(self, text: str) -> List[str]:
        """Extract inferred source mentions (e.g., 'According to ESPN')"""
        if not text:
            return []
        
        sources = []
        
        # Common attribution patterns
        patterns = [
            r'according to ([A-Z][A-Za-z\s\.]+)',
            r'as reported by ([A-Z][A-Za-z\s\.]+)',
            r'([A-Z][A-Za-z\s\.]+) reports',
            r'([A-Z][A-Za-z\s\.]+) states',
            r'per ([A-Z][A-Za-z\s\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up source name
                source = match.strip().rstrip(',.')
                if len(source) > 3 and len(source) < 50:
                    sources.append(source)
        
        return sources
    
    def _analyze_citation(self, url_or_source: str, context_text: str, 
                         citation_type: str) -> Dict:
        """Analyze a citation and extract metadata"""
        
        # Extract domain
        if citation_type == 'scraped_url':
            domain = self._extract_domain(url_or_source)
            full_url = url_or_source
        else:
            # Inferred source - try to guess domain
            domain = self._infer_domain_from_source(url_or_source)
            full_url = 'INFERRED'
        
        # Classify domain
        classification = self._classify_domain(domain, url_or_source)
        
        # Determine service supported
        service_supported = self._determine_service_support(
            url_or_source, context_text
        )
        
        # Extract context
        citation_context = self._extract_citation_context(
            url_or_source, context_text
        )
        
        return {
            'url': full_url,
            'domain': domain,
            'citation_type': citation_type,
            'classification': classification,
            'service_supported': service_supported,
            'context': citation_context
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ''
    
    def _infer_domain_from_source(self, source: str) -> str:
        """Infer domain from source name"""
        source_lower = source.lower()
        
        # Common source name to domain mappings
        mappings = {
            'espn': 'espn.com',
            'the athletic': 'theathletic.com',
            'sports illustrated': 'si.com',
            'bleacher report': 'bleacherreport.com',
            'fox sports': 'foxsports.com',
            'cbs sports': 'cbssports.com',
            'yahoo sports': 'sports.yahoo.com',
            'nbc sports': 'nbcsports.com',
            'cnet': 'cnet.com',
            'techradar': 'techradar.com',
            'the verge': 'theverge.com',
            'forbes': 'forbes.com',
            'nba': 'nba.com',
            'amazon': 'amazon.com'
        }
        
        for name, domain in mappings.items():
            if name in source_lower:
                return domain
        
        return source_lower.replace(' ', '')
    
    def _classify_domain(self, domain: str, url_or_source: str) -> str:
        """Classify domain into categories"""
        if not domain:
            return 'other'
        
        domain_lower = domain.lower()
        source_lower = url_or_source.lower()
        
        # League official
        if 'nba.com' in domain_lower:
            return 'league_official'
        
        # Amazon official
        if any(d in domain_lower for d in ['amazon.com', 'primevideo.com', 'aboutamazon.com']):
            return 'amazon_official'
        
        # Streaming official
        if any(d in domain_lower for d in ['youtube.com', 'hulu.com', 'sling.com', 'fubo.tv']):
            return 'streaming_official'
        
        # Sports Media Tier 1 (Premium/Subscription)
        tier1_sports = ['espn.com', 'theathletic.com', 'si.com', 'bleacherreport.com']
        if any(d in domain_lower for d in tier1_sports):
            return 'sports_media_tier1'
        
        # Sports Media Tier 2 (Major Networks)
        tier2_sports = ['foxsports.com', 'cbssports.com', 'sports.yahoo.com', 
                       'nbcsports.com', 'sportingnews.com']
        if any(d in domain_lower for d in tier2_sports):
            return 'sports_media_tier2'
        
        # Tech media
        tech_media = ['cnet.com', 'techradar.com', 'theverge.com', 'wired.com', 'tomsguide.com']
        if any(d in domain_lower for d in tech_media):
            return 'tech_media'
        
        # Cord cutting media
        cord_cutting = ['cordcuttersnews.com', 'flixed.io', 'streamingbetter.com']
        if any(d in domain_lower for d in cord_cutting):
            return 'cord_cutting_media'
        
        # Mainstream news
        mainstream = ['nytimes.com', 'washingtonpost.com', 'usatoday.com']
        if any(d in domain_lower for d in mainstream):
            return 'mainstream_news'
        
        # Finance/Business
        finance = ['forbes.com', 'wsj.com', 'bloomberg.com', 'cnbc.com']
        if any(d in domain_lower for d in finance):
            return 'finance_business'
        
        # Reference
        if any(d in domain_lower for d in ['wikipedia.org', 'reddit.com', 'quora.com']):
            return 'reference'
        
        return 'other'
    
    def _determine_service_support(self, url_or_source: str, context: str) -> str:
        """Determine which streaming service a citation supports"""
        combined = (url_or_source + ' ' + context).lower()
        
        # Check for explicit service mentions
        if 'league pass' in combined:
            return 'NBA League Pass'
        if 'amazon' in combined or 'prime' in combined:
            return 'Amazon Prime Video'
        if 'youtube tv' in combined:
            return 'YouTube TV'
        if 'hulu' in combined:
            return 'Hulu Live TV'
        
        # Check for comparison/multiple services
        service_count = sum([
            'league pass' in combined,
            'amazon' in combined or 'prime' in combined,
            'youtube' in combined,
            'hulu' in combined
        ])
        
        if service_count > 1:
            return 'Multiple'
        
        return 'General'
    
    def _extract_citation_context(self, url_or_source: str, text: str) -> str:
        """Extract context around a citation"""
        if not text:
            return ''
        
        text_lower = text.lower()
        search_term = url_or_source.lower()
        
        # For inferred sources, search for the source name
        if search_term not in text_lower:
            # Try domain extraction
            if '.' in search_term:
                domain_part = search_term.split('.')[0]
                search_term = domain_part
        
        pos = text_lower.find(search_term)
        if pos == -1:
            return ''
        
        # Extract 100 chars before and after
        start = max(0, pos - 100)
        end = min(len(text), pos + len(search_term) + 100)
        
        context = text[start:end].strip()
        return context[:200]  # Limit to 200 chars
    
    def _add_empty_result(self, query_info: Dict, platform: str):
        """Add empty result row when platform query fails"""
        matrix_row = {
            'query_id': query_info['query_id'],
            'query_text': query_info['text'],
            'query_type': query_info['query_type'],
            'engine': platform,
            'nba_leaguepass_mentioned': 'No',
            'nba_leaguepass_position': 'Not Present',
            'amazon_prime_mentioned': 'No',
            'amazon_prime_position': 'Not Present',
            'youtube_tv_mentioned': 'No',
            'youtube_tv_position': 'Not Present',
            'hulu_mentioned': 'No',
            'hulu_position': 'Not Present',
            'other_services_mentioned': '',
            'primary_recommendation': 'ERROR',
            'total_citations': 0,
            'scraped_citations': 0,
            'inferred_citations': 0
        }
        self.query_matrix_data.append(matrix_row)
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all 3 required CSV files"""
        output_dir = 'case_studies/nba_streaming'
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. NBA_STREAMING_QUERY_MATRIX
        matrix_path = f'{output_dir}/NBA_STREAMING_QUERY_MATRIX_{timestamp}.csv'
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query_id', 'query_text', 'query_type', 'engine',
                'nba_leaguepass_mentioned', 'nba_leaguepass_position',
                'amazon_prime_mentioned', 'amazon_prime_position',
                'youtube_tv_mentioned', 'youtube_tv_position',
                'hulu_mentioned', 'hulu_position',
                'other_services_mentioned', 'primary_recommendation',
                'total_citations', 'scraped_citations', 'inferred_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.query_matrix_data)
        
        files['query_matrix'] = matrix_path
        logger.info(f'✓ Generated: NBA_STREAMING_QUERY_MATRIX_{timestamp}.csv')
        
        # 2. NBA_STREAMING_RAW_CITATIONS
        citations_path = f'{output_dir}/NBA_STREAMING_RAW_CITATIONS_{timestamp}.csv'
        with open(citations_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'citation_id', 'query_id', 'engine', 'citation_type',
                'domain', 'classification', 'full_url',
                'service_supported', 'citation_context'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.raw_citations_data)
        
        files['raw_citations'] = citations_path
        logger.info(f'✓ Generated: NBA_STREAMING_RAW_CITATIONS_{timestamp}.csv')
        
        # 3. NBA_STREAMING_MEDIA_TRACKING
        media_path = f'{output_dir}/NBA_STREAMING_MEDIA_TRACKING_{timestamp}.csv'
        with open(media_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'media_outlet', 'total_citations', 'scraped_count',
                'inferred_count', 'services_favored', 'amazon_mention_count',
                'leaguepass_mention_count', 'queries_appeared_in',
                'engines_citing', 'sample_urls'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Convert media tracking to rows
            for outlet, data in sorted(self.media_tracking.items()):
                row = {
                    'media_outlet': outlet,
                    'total_citations': data['total_citations'],
                    'scraped_count': data['scraped_count'],
                    'inferred_count': data['inferred_count'],
                    'services_favored': ','.join(sorted(data['services_favored'])),
                    'amazon_mention_count': data['amazon_mention_count'],
                    'leaguepass_mention_count': data['leaguepass_mention_count'],
                    'queries_appeared_in': ','.join(sorted(data['queries_appeared_in'])),
                    'engines_citing': ','.join(sorted(data['engines_citing'])),
                    'sample_urls': ' | '.join(data['sample_urls'][:3])
                }
                writer.writerow(row)
        
        files['media_tracking'] = media_path
        logger.info(f'✓ Generated: NBA_STREAMING_MEDIA_TRACKING_{timestamp}.csv')
        
        # Generate summary JSON
        summary_path = f'{output_dir}/NBA_STREAMING_AUDIT_SUMMARY_{timestamp}.json'
        summary = self._generate_summary()
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        files['summary'] = summary_path
        logger.info(f'✓ Generated: NBA_STREAMING_AUDIT_SUMMARY_{timestamp}.json')
        
        return files
    
    def _generate_summary(self) -> Dict:
        """Generate comprehensive audit summary"""
        
        # Calculate service mention rates for service-agnostic queries
        agnostic_queries = [r for r in self.query_matrix_data if r['query_type'] == 'service_agnostic']
        
        amazon_mentions = sum(1 for r in agnostic_queries if r['amazon_prime_mentioned'] == 'Yes')
        leaguepass_mentions = sum(1 for r in agnostic_queries if r['nba_leaguepass_mentioned'] == 'Yes')
        youtube_mentions = sum(1 for r in agnostic_queries if r['youtube_tv_mentioned'] == 'Yes')
        hulu_mentions = sum(1 for r in agnostic_queries if r['hulu_mentioned'] == 'Yes')
        
        total_agnostic = len(agnostic_queries)
        
        # Calculate position metrics for Amazon Prime
        amazon_first = sum(1 for r in agnostic_queries if r['amazon_prime_position'] == 'First')
        amazon_prominent = sum(1 for r in agnostic_queries if r['amazon_prime_position'] in ['First', 'Prominent'])
        
        # Top media outlets
        top_media = sorted(
            [(outlet, data['total_citations']) for outlet, data in self.media_tracking.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'audit_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': len(self.queries),
                'service_agnostic_queries': 6,
                'service_specific_queries': 4,
                'platforms_tested': 4,
                'total_prompts': 40
            },
            'share_of_voice_analysis': {
                'service_agnostic_queries': {
                    'amazon_prime_mention_rate': round(amazon_mentions / total_agnostic * 100, 1) if total_agnostic > 0 else 0,
                    'nba_leaguepass_mention_rate': round(leaguepass_mentions / total_agnostic * 100, 1) if total_agnostic > 0 else 0,
                    'youtube_tv_mention_rate': round(youtube_mentions / total_agnostic * 100, 1) if total_agnostic > 0 else 0,
                    'hulu_mention_rate': round(hulu_mentions / total_agnostic * 100, 1) if total_agnostic > 0 else 0,
                    'amazon_first_position_rate': round(amazon_first / total_agnostic * 100, 1) if total_agnostic > 0 else 0,
                    'amazon_prominent_rate': round(amazon_prominent / total_agnostic * 100, 1) if total_agnostic > 0 else 0
                }
            },
            'citation_intelligence': {
                'total_citations': len(self.raw_citations_data),
                'scraped_urls': sum(1 for c in self.raw_citations_data if c['citation_type'] == 'scraped_url'),
                'inferred_sources': sum(1 for c in self.raw_citations_data if c['citation_type'] == 'inferred_source'),
                'amazon_supporting_citations': sum(1 for c in self.raw_citations_data if 'Amazon' in c['service_supported']),
                'leaguepass_supporting_citations': sum(1 for c in self.raw_citations_data if 'League Pass' in c['service_supported'])
            },
            'media_outlet_intelligence': {
                'unique_outlets': len(self.media_tracking),
                'top_10_outlets': [{'outlet': o, 'citations': c} for o, c in top_media]
            },
            'strategic_insights': {
                'amazon_visibility_gap': amazon_mentions < leaguepass_mentions,
                'primary_competitor': 'NBA League Pass',
                'earned_media_opportunity': 'High' if amazon_mentions < total_agnostic * 0.5 else 'Medium'
            }
        }


def main():
    """Main execution function"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create auditor
        auditor = NBAStreamingAuditor()
        
        # Run audit
        output_files = auditor.run_audit()
        
        logger.info('\n✓ NBA Streaming Audit Complete!')
        logger.info('\nGenerated Files:')
        for file_type, file_path in output_files.items():
            logger.info(f'  • {file_path}')
        
        logger.info('\n📊 NEXT STEPS:')
        logger.info('Upload CSVs to Claude for dashboard creation:')
        logger.info('"Create an NBA Streaming Citation Analysis dashboard for Amazon PR team"')
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info('\nAudit interrupted by user')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

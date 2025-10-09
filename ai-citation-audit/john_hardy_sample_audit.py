#!/usr/bin/env python3
"""
John Hardy Jewelry - AEO Citation Analysis "Free Sample"
Proof-of-Concept: 10 Queries × 4 Engines = 40 Prompts

Demonstrates AEO analysis methodology value with minimal investment.
Tests strategic queries across sustainability, lab-grown diamonds, and competitive positioning.
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
from typing import List, Dict, Any, Tuple
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


class JohnHardySampleAuditor:
    """
    Proof-of-concept auditor for John Hardy jewelry brand
    Tests 10 strategic queries across 4 AI platforms
    """
    
    def __init__(self):
        self.brand_name = "John Hardy"
        self.brand_variants = [
            "John Hardy", "john hardy", "johnhardy", "john-hardy",
            "johnhardy.com", "John Hardy jewelry"
        ]
        
        # Initialize platforms
        self.platforms = {
            'chatgpt': ChatGPTPlatform(),
            'claude': ClaudePlatform(),
            'perplexity': PerplexityPlatform(),
            'gemini': GeminiPlatform()
        }
        
        # Competitor tracking list (luxury jewelry brands)
        self.competitors = [
            "Brilliant Earth", "Vrai", "Mejuri", "Aurate", "Tiffany & Co",
            "Cartier", "David Yurman", "Pandora", "Lagos", "Ippolita",
            "Monica Vinader", "Catbird", "Catbird NYC", "The Good Trade",
            "Bario Neal", "Chopard"
        ]
        
        # Priority media outlets to track
        self.priority_media = [
            "vogue.com", "forbes.com", "harpersbazaar.com", "thegoodtrade.com",
            "jckonline.com", "nordstrom.com", "brilliantearth.com", "tiffany.com",
            "nytimes.com", "businessinsider.com"
        ]
        
        # Query definitions
        self.queries = self._define_queries()
        
        # Storage for results
        self.matrix_data = []
        self.citations_data = []
        self.media_tracking_data = {}
        
        # Initialize media tracking
        for outlet in self.priority_media:
            self.media_tracking_data[outlet] = {
                'citation_count': 0,
                'john_hardy_citations': 0,
                'competitor_citations': 0,
                'queries': set(),
                'engines': set()
            }
        
        logger.info("John Hardy Sample Auditor initialized - 10 queries × 4 engines = 40 tests")
    
    def _define_queries(self) -> List[Dict[str, str]]:
        """Define the 10 strategic queries for proof-of-concept"""
        queries = []
        
        # Category 1: Brand Awareness (2 queries)
        queries.append({
            "text": "What is John Hardy jewelry known for?",
            "category": "brand_awareness",
            "intent": "Basic brand visibility"
        })
        queries.append({
            "text": "Is John Hardy jewelry worth the investment?",
            "category": "brand_awareness",
            "intent": "Value positioning"
        })
        
        # Category 2: Sustainability Focus (3 queries)
        queries.append({
            "text": "Most sustainable luxury jewelry brands",
            "category": "sustainability",
            "intent": "Sustainability positioning"
        })
        queries.append({
            "text": "Ethical jewelry brands that use recycled materials",
            "category": "sustainability",
            "intent": "Recycled metal messaging"
        })
        queries.append({
            "text": "Which jewelry companies are truly sustainable?",
            "category": "sustainability",
            "intent": "Authenticity/credibility"
        })
        
        # Category 3: Lab-Grown Diamonds (2 queries)
        queries.append({
            "text": "Best lab-grown diamond jewelry brands",
            "category": "lab_grown",
            "intent": "Lab-grown association"
        })
        queries.append({
            "text": "Luxury brands that offer lab-grown diamonds",
            "category": "lab_grown",
            "intent": "Product awareness"
        })
        
        # Category 4: Competitive Positioning (2 queries)
        queries.append({
            "text": "John Hardy vs Tiffany & Co sustainability",
            "category": "competitive",
            "intent": "Direct comparison"
        })
        queries.append({
            "text": "David Yurman vs John Hardy craftsmanship",
            "category": "competitive",
            "intent": "Craftsmanship positioning"
        })
        
        # Category 5: Thought Leadership (1 query)
        queries.append({
            "text": "Jewelry industry sustainability leaders",
            "category": "thought_leadership",
            "intent": "Industry authority"
        })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """
        Execute complete proof-of-concept audit
        Returns paths to generated CSV files
        """
        logger.info(f"\n{'='*80}")
        logger.info("JOHN HARDY AEO CITATION ANALYSIS - PROOF OF CONCEPT")
        logger.info(f"{'='*80}")
        logger.info(f"Testing: {len(self.queries)} queries × {len(self.platforms)} engines = {len(self.queries) * len(self.platforms)} total tests")
        logger.info(f"Estimated time: ~90 minutes\n")
        
        total_tests = len(self.queries) * len(self.platforms)
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            category = query_info["category"]
            intent = query_info["intent"]
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Category: {category} | Intent: {intent}")
            logger.info(f"{'='*80}")
            
            for platform_name, platform in self.platforms.items():
                completed += 1
                logger.info(f"\n[{completed}/{total_tests}] Testing on {platform_name}...")
                
                try:
                    # Get response and citations from platform
                    result = self._query_platform(platform, platform_name, query_text)
                    
                    if result:
                        # Analyze response
                        analysis = self._analyze_response(
                            result['response_text'],
                            result['citations'],
                            query_text,
                            category,
                            platform_name
                        )
                        
                        # Store results
                        self.matrix_data.append(analysis['matrix_row'])
                        self.citations_data.extend(analysis['citations'])
                        
                        # Update media tracking
                        self._update_media_tracking(
                            analysis['citations'],
                            query_text,
                            platform_name
                        )
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error testing {query_text} on {platform_name}: {e}")
                    continue
        
        # Generate CSV files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_csv_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("PROOF-OF-CONCEPT AUDIT COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"\nGenerated files:")
        for key, path in output_files.items():
            logger.info(f"  - {key}: {path}")
        logger.info(f"\n{'='*80}\n")
        
        return output_files
    
    def _query_platform(self, platform, platform_name: str, query: str) -> Dict[str, Any]:
        """Query a platform and return structured results"""
        try:
            # Get citations from platform
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
        category: str,
        platform: str
    ) -> Dict[str, Any]:
        """Analyze response and citations for brand mentions"""
        
        # Check if John Hardy present in response
        jh_present = self._check_brand_mention(response_text)
        
        # Extract competitors mentioned
        competitors_found = self._extract_competitors(response_text)
        
        # Determine position prominence
        prominence = self._determine_prominence(response_text, jh_present)
        
        # Determine winner brand (most favorably presented)
        winner = self._determine_winner(response_text, jh_present, competitors_found)
        
        # Total citations
        total_citations = len(citations)
        
        # Process each citation
        citation_rows = []
        for citation in citations:
            url = citation.get('url', '')
            domain = self._extract_domain(url)
            
            # Check for brand association
            brand_association = self._determine_brand_association(url, response_text)
            confidence = self._determine_confidence_level(url, brand_association)
            url_contains_brand = self._check_url_for_brand_name(url)
            
            # Classify source
            classification = self._classify_source(domain)
            content_type = self._classify_content_type(url)
            
            citation_rows.append({
                'Engine': platform,
                'Query': query,
                'Domain': domain,
                'Classification': classification,
                'URL': url,
                'Brand_Association': brand_association,
                'Confidence_Level': confidence,
                'URL_Contains_Brand': url_contains_brand,
                'Content_Type': content_type
            })
        
        # Build matrix row
        matrix_row = {
            'query': query,
            'engine': platform,
            'john_hardy_present': "Yes" if jh_present else "No",
            'competitors_mentioned': ", ".join(competitors_found) if competitors_found else "None",
            'position_prominence': prominence,
            'winner_brand': winner,
            'total_citations': total_citations
        }
        
        return {
            'matrix_row': matrix_row,
            'citations': citation_rows
        }
    
    def _check_brand_mention(self, text: str) -> bool:
        """Check if John Hardy is mentioned in text"""
        if not text:
            return False
        
        text_lower = text.lower()
        for variant in self.brand_variants:
            if variant.lower() in text_lower:
                return True
        return False
    
    def _extract_competitors(self, text: str) -> List[str]:
        """Extract competitor brands mentioned in text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found = []
        
        for competitor in self.competitors:
            if competitor.lower() in text_lower:
                found.append(competitor)
        
        return found
    
    def _determine_prominence(self, text: str, jh_present: bool) -> str:
        """Determine how prominently John Hardy is positioned"""
        if not jh_present:
            return "Not Present"
        
        if not text:
            return "Not Present"
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Check first few sentences
        first_sentences = ' '.join(sentences[:3]).lower()
        
        if self._check_brand_mention(first_sentences):
            # Check if it's featured prominently
            if any(word in first_sentences for word in ['recommend', 'best', 'top', 'leading', 'premier', 'known for']):
                return "High"
            else:
                return "Medium"
        
        # Mentioned but not early
        return "Low"
    
    def _determine_winner(self, text: str, jh_present: bool, competitors: List[str]) -> str:
        """Determine which brand is presented most favorably"""
        if not text:
            return "No Clear Winner"
        
        text_lower = text.lower()
        
        # Check for explicit recommendations
        for competitor in competitors:
            pattern = f"(recommend|best|top choice|leading|premier).*{competitor.lower()}"
            if re.search(pattern, text_lower):
                return competitor
        
        if jh_present:
            for variant in self.brand_variants:
                pattern = f"(recommend|best|top choice|leading|premier).*{variant.lower()}"
                if re.search(pattern, text_lower):
                    return "John Hardy"
        
        # Check position in list
        if jh_present and competitors:
            jh_pos = text_lower.find("john hardy")
            comp_positions = [text_lower.find(c.lower()) for c in competitors]
            comp_positions = [p for p in comp_positions if p != -1]
            
            if comp_positions and jh_pos < min(comp_positions):
                return "John Hardy"
            elif comp_positions:
                idx = comp_positions.index(min(comp_positions))
                return competitors[idx]
        
        if jh_present:
            return "John Hardy"
        elif competitors:
            return competitors[0]
        
        return "No Clear Winner"
    
    def _determine_brand_association(self, url: str, response_text: str) -> str:
        """Determine which brand is associated with this citation"""
        if not url:
            return "Unknown"
        
        url_lower = url.lower()
        
        # Check for John Hardy
        for variant in ["john-hardy", "johnhardy", "john_hardy"]:
            if variant in url_lower:
                return "John Hardy"
        
        # Check for competitors
        for competitor in self.competitors:
            comp_clean = competitor.lower().replace(' ', '').replace('&', '').replace('.', '')
            if comp_clean in url_lower.replace('-', '').replace('_', ''):
                return competitor
        
        # Check if URL domain matches any brand
        domain = self._extract_domain(url)
        if 'johnhardy' in domain:
            return "John Hardy"
        
        for competitor in self.competitors:
            comp_clean = competitor.lower().replace(' ', '').replace('&', '').replace('.', '')
            if comp_clean in domain.replace('.', ''):
                return competitor
        
        # Infer from response text context if possible
        return "John Hardy (inferred)" if self._check_brand_mention(response_text) else "Unknown"
    
    def _determine_confidence_level(self, url: str, brand_association: str) -> str:
        """Determine confidence level of brand association"""
        if brand_association == "Unknown":
            return "LOW"
        
        if "(inferred)" in brand_association:
            return "MEDIUM"
        
        # Check if brand name is explicitly in URL
        url_lower = url.lower()
        
        # HIGH confidence if brand clearly in URL
        if "john-hardy" in url_lower or "johnhardy" in url_lower:
            return "HIGH"
        
        for competitor in self.competitors:
            comp_clean = competitor.lower().replace(' ', '-')
            if comp_clean in url_lower:
                return "HIGH"
        
        return "MEDIUM"
    
    def _check_url_for_brand_name(self, url: str) -> str:
        """Check if URL contains brand name"""
        if not url:
            return "No"
        
        url_lower = url.lower()
        
        # Check for John Hardy
        if any(variant in url_lower for variant in ["john-hardy", "johnhardy", "john_hardy"]):
            return "Yes"
        
        return "No"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _classify_source(self, domain: str) -> str:
        """Classify the source type"""
        domain = domain.lower()
        
        # Luxury Fashion Tier 1
        if any(d in domain for d in ['vogue.com', 'harpersbazaar.com', 'elle.com', 'wwd.com']):
            return 'luxury_fashion_tier1'
        
        # Business/Sustainability
        if any(d in domain for d in ['forbes.com', 'fastcompany.com', 'inc.com', 'businessinsider.com']):
            return 'business_sustainability'
        
        # Jewelry Trade
        if any(d in domain for d in ['jckonline.com', 'nationaljeweler.com', 'jewelers.org']):
            return 'jewelry_trade'
        
        # Sustainability Media
        if any(d in domain for d in ['thegoodtrade.com', 'ecocult.com', 'sustainably-chic.com']):
            return 'sustainability_media'
        
        # Brand Official
        if 'johnhardy.com' in domain:
            return 'owned'
        
        # Competitor Official
        competitor_domains = ['brilliantearth.com', 'vrai.com', 'tiffany.com', 'cartier.com', 'davidyurman.com']
        if any(d in domain for d in competitor_domains):
            return 'competitor_owned'
        
        # Retail
        if any(d in domain for d in ['nordstrom.com', 'neimanmarcus.com', 'bloomingdales.com', 'saksfifthavenue.com']):
            return 'retail'
        
        return 'general_editorial'
    
    def _classify_content_type(self, url: str) -> str:
        """Classify content type based on URL"""
        url_lower = url.lower()
        
        if any(word in url_lower for word in ['best', 'top', 'guide', 'roundup']):
            return 'Editorial'
        elif any(word in url_lower for word in ['product', 'collection', 'jewelry']):
            return 'Product'
        elif any(word in url_lower for word in ['about', 'company', 'story', 'mission']):
            return 'Owned'
        elif any(word in url_lower for word in ['sustainability', 'ethical', 'eco']):
            return 'Sustainability'
        elif any(word in url_lower for word in ['news', 'press', 'article']):
            return 'News'
        else:
            return 'Other'
    
    def _update_media_tracking(self, citations: List[Dict], query: str, engine: str):
        """Update media tracking data"""
        for citation in citations:
            domain = citation.get('Domain', '')
            
            if domain in self.media_tracking_data:
                self.media_tracking_data[domain]['citation_count'] += 1
                self.media_tracking_data[domain]['queries'].add(query)
                self.media_tracking_data[domain]['engines'].add(engine)
                
                # Check brand association
                brand_assoc = citation.get('Brand_Association', '')
                if 'John Hardy' in brand_assoc:
                    self.media_tracking_data[domain]['john_hardy_citations'] += 1
                elif brand_assoc in self.competitors:
                    self.media_tracking_data[domain]['competitor_citations'] += 1
    
    def _generate_csv_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all three CSV files"""
        output_dir = "case_studies/john_hardy_sample"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. JOHN_HARDY_SAMPLE_MATRIX
        matrix_path = f"{output_dir}/JOHN_HARDY_SAMPLE_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'engine', 'john_hardy_present', 'competitors_mentioned',
                'position_prominence', 'winner_brand', 'total_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.matrix_data)
        files['matrix'] = matrix_path
        logger.info(f"Generated: {matrix_path}")
        
        # 2. RAW_CITATIONS_SAMPLE
        citations_path = f"{output_dir}/RAW_CITATIONS_SAMPLE_{timestamp}.csv"
        with open(citations_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'Engine', 'Query', 'Domain', 'Classification', 'URL',
                'Brand_Association', 'Confidence_Level', 'URL_Contains_Brand', 'Content_Type'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citations_data)
        files['citations'] = citations_path
        logger.info(f"Generated: {citations_path}")
        
        # 3. MEDIA_TRACKING_SAMPLE
        media_path = f"{output_dir}/MEDIA_TRACKING_SAMPLE_{timestamp}.csv"
        with open(media_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'Media_Outlet', 'Citation_Count', 'John_Hardy_Citations',
                'Competitor_Citations', 'Top_Queries', 'Engines'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            media_rows = []
            for outlet, data in self.media_tracking_data.items():
                if data['citation_count'] > 0:
                    media_rows.append({
                        'Media_Outlet': outlet,
                        'Citation_Count': data['citation_count'],
                        'John_Hardy_Citations': data['john_hardy_citations'],
                        'Competitor_Citations': data['competitor_citations'],
                        'Top_Queries': '; '.join(list(data['queries'])[:3]),
                        'Engines': ', '.join(sorted(data['engines']))
                    })
            
            # Sort by citation count
            media_rows.sort(key=lambda x: x['Citation_Count'], reverse=True)
            writer.writerows(media_rows)
        files['media'] = media_path
        logger.info(f"Generated: {media_path}")
        
        # 4. Generate summary JSON for analysis
        summary_path = f"{output_dir}/AUDIT_SUMMARY_{timestamp}.json"
        summary = self._generate_summary()
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files['summary'] = summary_path
        logger.info(f"Generated: {summary_path}")
        
        return files
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the proof-of-concept"""
        total_queries = len(self.matrix_data)
        
        # Overall visibility
        jh_present = sum(1 for row in self.matrix_data if row['john_hardy_present'] == 'Yes')
        visibility_rate = (jh_present / total_queries * 100) if total_queries > 0 else 0
        
        # By category
        category_stats = {}
        for query_info in self.queries:
            cat = query_info['category']
            if cat not in category_stats:
                category_stats[cat] = {'total': 0, 'present': 0}
            
            category_stats[cat]['total'] += len(self.platforms)
            
            # Count how many times JH appeared for this query
            query_text = query_info['text']
            present_count = sum(1 for row in self.matrix_data 
                              if row['query'] == query_text and row['john_hardy_present'] == 'Yes')
            category_stats[cat]['present'] += present_count
        
        # Calculate rates
        for cat in category_stats:
            total = category_stats[cat]['total']
            present = category_stats[cat]['present']
            category_stats[cat]['rate'] = round((present / total * 100) if total > 0 else 0, 2)
        
        # Top competitors
        competitor_mentions = {}
        for row in self.matrix_data:
            comps = row.get('competitors_mentioned', '').split(', ')
            for comp in comps:
                if comp and comp != 'None':
                    competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
        
        top_competitors = sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Platform comparison
        platform_stats = {}
        for platform in ['chatgpt', 'claude', 'perplexity', 'gemini']:
            platform_queries = [r for r in self.matrix_data if r['engine'] == platform]
            platform_present = sum(1 for r in platform_queries if r['john_hardy_present'] == 'Yes')
            platform_stats[platform] = {
                'total_queries': len(platform_queries),
                'jh_present': platform_present,
                'visibility_rate': round((platform_present / len(platform_queries) * 100) if len(platform_queries) > 0 else 0, 2)
            }
        
        return {
            'audit_date': datetime.now().isoformat(),
            'total_queries_tested': len(self.queries),
            'total_platforms': len(self.platforms),
            'total_tests_conducted': len(self.queries) * len(self.platforms),
            'overall_metrics': {
                'john_hardy_visibility_rate': round(visibility_rate, 2),
                'times_jh_present': jh_present,
                'total_citations': sum(row['total_citations'] for row in self.matrix_data)
            },
            'by_category': category_stats,
            'top_competitors': [{'brand': comp[0], 'mentions': comp[1]} for comp in top_competitors],
            'by_platform': platform_stats,
            'media_coverage': {
                'total_outlets_citing': len([o for o, d in self.media_tracking_data.items() if d['citation_count'] > 0]),
                'jh_citations': sum(d['john_hardy_citations'] for d in self.media_tracking_data.values()),
                'competitor_citations': sum(d['competitor_citations'] for d in self.media_tracking_data.values())
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
        auditor = JohnHardySampleAuditor()
        output_files = auditor.run_audit()
        
        logger.info("\n" + "="*80)
        logger.info("JOHN HARDY PROOF-OF-CONCEPT AUDIT COMPLETE!")
        logger.info("="*80)
        logger.info("\nNext Steps:")
        logger.info("1. Review the generated CSV files")
        logger.info("2. Upload CSVs to Claude for dashboard generation")
        logger.info("3. Analyze strategic insights")
        logger.info("4. Decide on full 100-prompt analysis")
        logger.info("\n" + "="*80)
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

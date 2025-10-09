#!/usr/bin/env python3
"""
Simple Lead Generation Auditor
Lightweight POC for customer-facing AI visibility audit

Runs only 5 queries across 4 platforms for fast execution (~2-3 minutes)
Generates simplified dashboard with clear CTA for full analysis
"""

import os
import json
import csv
import logging
import requests
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Set
from collections import defaultdict
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleLeadAuditor:
    """
    Simplified auditor for lead generation
    - Limited to 5 queries
    - 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini)
    - Basic metrics only
    """
    
    def __init__(self, brand: str, competitors: List[str], sample_query: str, email: str):
        self.brand = brand
        self.competitors = competitors[:3]  # Max 3 competitors
        self.sample_query = sample_query
        self.email = email
        
        # Storage
        self.query_results = []
        self.platform_success = defaultdict(int)
        self.platform_attempts = defaultdict(int)
        
        logger.info(f"SimpleLeadAuditor initialized for {brand}")
    
    def generate_queries(self) -> List[str]:
        """Generate 5 strategic queries"""
        queries = [self.sample_query]
        
        # Infer category from sample query
        category = self._infer_category(self.sample_query)
        
        # Add 4 more queries
        queries.append(f"Who are the top brands like {self.brand}?")
        
        if self.competitors:
            queries.append(f"Compare {self.brand} and {self.competitors[0]}")
        else:
            queries.append(f"What makes {self.brand} different?")
        
        if category:
            queries.append(f"Best {category}")
        else:
            queries.append(f"Top alternatives to {self.brand}")
        
        queries.append(f"Where to buy {self.brand}?")
        
        return queries[:5]  # Ensure exactly 5
    
    def _infer_category(self, query: str) -> str:
        """Infer product category from query"""
        query_lower = query.lower()
        
        if 'gift' in query_lower or 'holiday' in query_lower:
            return 'holiday gifts'
        elif 'food' in query_lower or 'restaurant' in query_lower:
            return 'food options'
        elif 'software' in query_lower or 'app' in query_lower:
            return 'software solutions'
        elif 'service' in query_lower:
            return 'services'
        else:
            return 'products'
    
    def run_audit(self) -> Dict[str, Any]:
        """Execute the 5-query audit across 4 platforms"""
        logger.info(f"\n{'='*60}")
        logger.info("SIMPLE LEAD GENERATION AUDIT")
        logger.info(f"Brand: {self.brand}")
        logger.info(f"Email: {self.email}")
        logger.info(f"{'='*60}\n")
        
        queries = self.generate_queries()
        logger.info(f"Generated {len(queries)} queries")
        
        platforms = ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']
        total_tests = len(queries) * len(platforms)
        completed = 0
        
        for query in queries:
            logger.info(f"\nQuery: {query}")
            
            for platform in platforms:
                completed += 1
                logger.info(f"  [{completed}/{total_tests}] Testing {platform}...")
                
                self.platform_attempts[platform] += 1
                
                try:
                    result = self._query_platform(platform, query)
                    
                    if result:
                        self.platform_success[platform] += 1
                        analysis = self._analyze_response(result, query, platform)
                        self.query_results.append(analysis)
                    else:
                        # Add empty result
                        self.query_results.append({
                            'query': query,
                            'platform': platform,
                            'brand_mentioned': False,
                            'competitors_mentioned': [],
                            'position': None,
                            'response_text': ''
                        })
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error on {platform}: {e}")
                    self.query_results.append({
                        'query': query,
                        'platform': platform,
                        'brand_mentioned': False,
                        'competitors_mentioned': [],
                        'position': None,
                        'response_text': ''
                    })
        
        # Generate summary
        summary = self._generate_summary()
        
        logger.info(f"\n{'='*60}")
        logger.info("AUDIT COMPLETE")
        logger.info(f"{'='*60}\n")
        
        return summary
    
    def _query_platform(self, platform: str, query: str) -> Dict:
        """Query a specific AI platform"""
        try:
            if platform == 'ChatGPT':
                return self._query_chatgpt(query)
            elif platform == 'Claude':
                return self._query_claude(query)
            elif platform == 'Perplexity':
                return self._query_perplexity(query)
            elif platform == 'Gemini':
                return self._query_gemini(query)
        except Exception as e:
            logger.error(f"{platform} query failed: {e}")
            return None
    
    def _query_chatgpt(self, query: str) -> Dict:
        """Query ChatGPT"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": query}],
                "max_tokens": 1000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            return {'response_text': text, 'platform': 'ChatGPT'}
        
        return None
    
    def _query_claude(self, query: str) -> Dict:
        """Query Claude"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
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
            return {'response_text': text, 'platform': 'Claude'}
        
        return None
    
    def _query_perplexity(self, query: str) -> Dict:
        """Query Perplexity"""
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": query}],
                "max_tokens": 800
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content']
            return {'response_text': text, 'platform': 'Perplexity'}
        
        return None
    
    def _query_gemini(self, query: str) -> Dict:
        """Query Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": query}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                return {'response_text': text, 'platform': 'Gemini'}
        
        return None
    
    def _analyze_response(self, result: Dict, query: str, platform: str) -> Dict:
        """Analyze response for brand and competitor mentions"""
        text = result['response_text']
        text_lower = text.lower()
        
        # Check brand mention
        brand_mentioned = self.brand.lower() in text_lower
        
        # Check competitor mentions
        competitors_mentioned = [
            comp for comp in self.competitors 
            if comp.lower() in text_lower
        ]
        
        # Determine position if brand mentioned
        position = None
        if brand_mentioned:
            brand_pos = text_lower.find(self.brand.lower())
            
            # Check if mentioned first
            first_mention = True
            for comp in self.competitors:
                comp_pos = text_lower.find(comp.lower())
                if comp_pos != -1 and comp_pos < brand_pos:
                    first_mention = False
                    break
            
            position = 'First' if first_mention else 'Later'
        
        return {
            'query': query,
            'platform': platform,
            'brand_mentioned': brand_mentioned,
            'competitors_mentioned': competitors_mentioned,
            'position': position,
            'response_text': text[:200]  # Store snippet only
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary"""
        
        # Calculate brand mention rate
        total_responses = len(self.query_results)
        brand_mentions = sum(1 for r in self.query_results if r['brand_mentioned'])
        brand_mention_rate = (brand_mentions / total_responses * 100) if total_responses > 0 else 0
        
        # Calculate competitor mention rates
        competitor_rates = {}
        for comp in self.competitors:
            comp_mentions = sum(
                1 for r in self.query_results 
                if comp in r['competitors_mentioned']
            )
            competitor_rates[comp] = (comp_mentions / total_responses * 100) if total_responses > 0 else 0
        
        # Platform performance
        platform_performance = {}
        for platform in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
            success = self.platform_success[platform]
            attempts = self.platform_attempts[platform]
            platform_performance[platform] = {
                'success_rate': (success / attempts * 100) if attempts > 0 else 0,
                'brand_mentions': sum(
                    1 for r in self.query_results 
                    if r['platform'] == platform and r['brand_mentioned']
                )
            }
        
        # Sample query analysis
        sample_results = [
            r for r in self.query_results 
            if r['query'] == self.sample_query
        ]
        
        return {
            'metadata': {
                'brand': self.brand,
                'competitors': self.competitors,
                'email': self.email,
                'total_queries': 5,
                'total_tests': total_responses,
                'timestamp': datetime.now().isoformat()
            },
            'key_metrics': {
                'brand_mention_rate': round(brand_mention_rate, 1),
                'competitor_rates': {k: round(v, 1) for k, v in competitor_rates.items()},
                'first_position_count': sum(1 for r in self.query_results if r['position'] == 'First')
            },
            'platform_performance': platform_performance,
            'sample_query_results': sample_results,
            'all_results': self.query_results
        }
    
    def save_results(self, output_dir: str = 'lead_audits') -> Dict[str, str]:
        """Save results to CSV and JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        safe_brand = "".join(c for c in self.brand if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # Save CSV
        csv_path = f"{output_dir}/{safe_brand}_sample_{timestamp}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['query', 'platform', 'brand_mentioned', 'competitors_mentioned', 'position']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.query_results:
                writer.writerow({
                    'query': result['query'],
                    'platform': result['platform'],
                    'brand_mentioned': 'Yes' if result['brand_mentioned'] else 'No',
                    'competitors_mentioned': ', '.join(result['competitors_mentioned']),
                    'position': result['position'] or 'Not Mentioned'
                })
        
        # Save JSON summary
        json_path = f"{output_dir}/{safe_brand}_summary_{timestamp}.json"
        summary = self._generate_summary()
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return {
            'csv': csv_path,
            'json': json_path,
            'timestamp': timestamp
        }


def main():
    """Test function"""
    auditor = SimpleLeadAuditor(
        brand="ACME Corp",
        competitors=["Dunder Mifflin", "Wayne Enterprises"],
        sample_query="What are the best widgets for holiday gift giving?",
        email="test@example.com"
    )
    
    summary = auditor.run_audit()
    files = auditor.save_results()
    
    print("\n=== AUDIT SUMMARY ===")
    print(f"Brand Mention Rate: {summary['key_metrics']['brand_mention_rate']}%")
    print(f"\nFiles saved:")
    print(f"  CSV: {files['csv']}")
    print(f"  JSON: {files['json']}")


if __name__ == '__main__':
    main()

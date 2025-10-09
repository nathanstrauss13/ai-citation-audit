#!/usr/bin/env python3
"""
HoneyBaked Ham Programmatic API Data Collection
Precision Methodology for AI Citation Analysis

Captures brand mentions, citations, and competitive positioning 
across multiple AI platforms for holiday and food-related queries.
"""

import os
import re
import csv
import sys
import json
import time
import datetime
import requests
from urllib.parse import urlparse

# Load environment variables
try:
    from load_env import load_env
    load_env()
except ImportError:
    pass

class HoneyBakedHamCitationAudit:
    def __init__(self):
        # Query Configuration
        self.BRANDED_QUERIES = [
            "Compare HoneyBaked Ham to Omaha Steaks for holiday meals",
            "What makes HoneyBaked Ham different from other spiral hams?", 
            "Where can I find HoneyBaked Ham stores near me?"
        ]
        
        self.BRAND_AGNOSTIC_QUERIES = {
            'Holiday Ham': [
                "What is the best ham for Thanksgiving dinner?",
                "What is the best ham for Christmas dinner?", 
                "Best spiral cut ham brands",
                "Best mail-order hams for holidays"
            ],
            'Convenience/Ordering': [
                "What should I serve for Christmas dinner if I don't want to cook?",
                "What is the easiest holiday meal to order online?", 
                "Last-minute Thanksgiving dinner options",
                "Where can I order a complete holiday meal?"
            ],
            'Gifting': [
                "Best holiday food gifts to ship",
                "What's the best food gift for the holidays?", 
                "Premium food gifts for corporate clients"
            ],
            'Thought Leadership': [
                "Who are the top chefs in the holiday catering industry?"
            ]
        }
        
        # Competitors to track
        self.COMPETITORS = [
            "Omaha Steaks", "Whole Foods", "Costco", 
            "Harry & David", "Williams Sonoma", 
            "D'Artagnan", "Smithfield", 
            "Spiral Ham Store", "Glazier Ham"
        ]
        
        # Domain Classifications
        self.DOMAIN_CLASSIFICATIONS = {
            'tier1_news': ['nytimes.com', 'wsj.com', 'washingtonpost.com'],
            'tier2_news': ['businessinsider.com', 'forbes.com'],
            'food_media': ['seriouseats.com', 'bonappetit.com', 'foodnetwork.com', 'allrecipes.com', 'eater.com', 'spruceeats.com'],
            'lifestyle_media': ['goodhousekeeping.com', 'marthastewart.com', 'realsimple.com'],
            'business_media': ['businessinsider.com', 'forbes.com', 'inc.com', 'fastcompany.com'],
            'authority': ['consumerreports.org', 'wirecutter.com'],
            'brand_official': ['honeybaked.com'],
            'retail': ['amazon.com', 'walmart.com']
        }
        
        # Timestamp for file naming
        self.TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    def normalize_url(self, url):
        """Normalize URL for consistent comparison"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            path = parsed.path.rstrip('/')
            return f"{parsed.scheme}://{domain}{path}"
        except Exception:
            return url
    
    def extract_domain(self, url):
        """Extract root domain from URL"""
        try:
            return urlparse(url).netloc.lower().replace('www.', '')
        except Exception:
            return ''
    
    def classify_domain(self, domain):
        """Classify domain based on predefined categories"""
        for category, domains in self.DOMAIN_CLASSIFICATIONS.items():
            if domain in domains:
                return category
        return 'other'
    
    def check_brand_mention(self, text):
        """Check if HoneyBaked is mentioned in text"""
        return 'honeybaked' in text.lower() or 'honey baked' in text.lower()
    
    def run_query(self, query, engine):
        """Run query across different AI platforms"""
        # Placeholder for actual API calls
        # You'll need to implement actual API calls for each platform
        # This is a mock implementation
        return {
            'content': f'Sample response for {query} from {engine}',
            'citations': [
                'https://www.seriouseats.com/holiday-ham-guide',
                'https://www.honeybaked.com/products'
            ]
        }
    
    def analyze_citations(self, citations):
        """Analyze citations for brand mentions"""
        brand_citations = []
        for citation in citations:
            # In a real implementation, you'd fetch and check the source content
            brand_mentioned = self.check_brand_mention(citation)
            brand_citations.append({
                'url': citation,
                'domain': self.extract_domain(citation),
                'domain_classification': self.classify_domain(self.extract_domain(citation)),
                'honeybaked_mentioned': brand_mentioned
            })
        return brand_citations
    
    def generate_query_response_matrix(self, results):
        """Generate QUERY_RESPONSE_MATRIX.csv"""
        matrix = []
        for result in results:
            matrix.append({
                'query': result['query'],
                'query_type': 'branded' if result['query'] in self.BRANDED_QUERIES else 'brand_agnostic',
                'engine': result['engine'],
                'brand_mentioned_in_response': 'Yes' if self.check_brand_mention(result['content']) else 'No',
                'total_citations': len(result['citations']),
                'citations_mentioning_brand': len([c for c in result['citations'] if self.check_brand_mention(c)]),
                'response_prominence': self.determine_response_prominence(result['content']),
                'chef_tim_mentioned': 'Yes' if 'chef tim' in result['content'].lower() else 'No'
            })
        return matrix
    
    def generate_citation_details(self, results):
        """Generate CITATION_DETAILS.csv"""
        details = []
        for result in results:
            for citation in result['citations']:
                details.append({
                    'engine': result['engine'],
                    'query': result['query'],
                    'query_type': 'branded' if result['query'] in self.BRANDED_QUERIES else 'brand_agnostic',
                    'citation_url': citation,
                    'domain': self.extract_domain(citation),
                    'domain_classification': self.classify_domain(self.extract_domain(citation)),
                    'honeybaked_mentioned_in_source': 'Yes' if self.check_brand_mention(citation) else 'No',
                    'content_type': self.determine_content_type(citation)
                })
        return details
    
    def generate_competitive_mentions(self, results):
        """Generate COMPETITIVE_MENTIONS.csv"""
        mentions = []
        for result in results:
            for competitor in self.COMPETITORS:
                mentions.append({
                    'query': result['query'],
                    'query_type': 'branded' if result['query'] in self.BRANDED_QUERIES else 'brand_agnostic',
                    'engine': result['engine'],
                    'competitor_mentioned': competitor,
                    'mentioned_in_response': 'Yes' if competitor.lower() in result['content'].lower() else 'No',
                    'mentioned_in_citations': 'Yes' if any(competitor.lower() in citation.lower() for citation in result['citations']) else 'No',
                    'prominence_vs_honeybaked': self.determine_competitive_prominence(result['content'], competitor)
                })
        return mentions
    
    def determine_response_prominence(self, content):
        """Determine brand prominence in response"""
        if 'honeybaked' in content.lower()[:200]:
            return 'Featured First'
        elif 'honeybaked' in content.lower():
            return 'Listed Among Options'
        return 'Not Present'
    
    def determine_content_type(self, url):
        """Determine content type based on URL"""
        if 'buying-guide' in url or 'best-of' in url:
            return 'buying_guide'
        elif 'review' in url:
            return 'product_review'
        elif 'news' in url:
            return 'news_article'
        elif 'recipe' in url or 'how-to' in url:
            return 'how_to'
        elif 'about' in url or 'product' in url:
            return 'company_page'
        return 'other'
    
    def determine_competitive_prominence(self, content, competitor):
        """Determine competitive prominence"""
        if competitor.lower() in content.lower()[:200]:
            return 'Higher - Featured First'
        elif competitor.lower() in content.lower():
            return 'Equal - Listed Together'
        return 'Not Present'
    
    def run_audit(self):
        """Execute full citation audit"""
        all_queries = self.BRANDED_QUERIES + [
            query for category in self.BRAND_AGNOSTIC_QUERIES.values() for query in category
        ]
        
        results = []
        engines = ['chatgpt', 'claude', 'perplexity', 'gemini']
        
        for query in all_queries:
            for engine in engines:
                result = self.run_query(query, engine)
                result.update({
                    'query': query,
                    'engine': engine
                })
                results.append(result)
        
        # Generate CSV files
        output_dir = 'case_studies/honeybaked_ham/citation_audit'
        os.makedirs(output_dir, exist_ok=True)
        
        # Query Response Matrix
        query_matrix = self.generate_query_response_matrix(results)
        matrix_path = os.path.join(output_dir, f'HONEYBAKED_QUERY_RESPONSE_MATRIX_{self.TIMESTAMP}.csv')
        with open(matrix_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=query_matrix[0].keys())
            writer.writeheader()
            writer.writerows(query_matrix)
        
        # Citation Details
        citation_details = self.generate_citation_details(results)
        details_path = os.path.join(output_dir, f'HONEYBAKED_CITATION_DETAILS_{self.TIMESTAMP}.csv')
        with open(details_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=citation_details[0].keys())
            writer.writeheader()
            writer.writerows(citation_details)
        
        # Competitive Mentions
        competitive_mentions = self.generate_competitive_mentions(results)
        mentions_path = os.path.join(output_dir, f'HONEYBAKED_COMPETITIVE_MENTIONS_{self.TIMESTAMP}.csv')
        with open(mentions_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=competitive_mentions[0].keys())
            writer.writeheader()
            writer.writerows(competitive_mentions)
        
        print(f"Audit complete. Files generated:\n{matrix_path}\n{details_path}\n{mentions_path}")

def main():
    audit = HoneyBakedHamCitationAudit()
    audit.run_audit()

if __name__ == "__main__":
    main()

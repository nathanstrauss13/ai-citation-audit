#!/usr/bin/env python3
"""
Comprehensive Test Suite for HoneyBaked Ham Citation Audit

Validates the core functionality, data processing, 
and output generation of the citation audit script.
"""

import os
import sys
import unittest
import csv
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from honeybaked_ham_citation_audit import HoneyBakedHamCitationAudit

class TestHoneyBakedHamCitationAudit(unittest.TestCase):
    def setUp(self):
        """Initialize the audit class before each test"""
        self.audit = HoneyBakedHamCitationAudit()
    
    def test_query_configuration(self):
        """Validate query configuration"""
        # Check total number of queries
        total_queries = (
            len(self.audit.BRANDED_QUERIES) + 
            sum(len(category) for category in self.audit.BRAND_AGNOSTIC_QUERIES.values())
        )
        self.assertEqual(total_queries, 15, "Total queries should be exactly 15")
        
        # Check query types
        branded_queries = self.audit.BRANDED_QUERIES
        brand_agnostic_queries = [
            query for category in self.audit.BRAND_AGNOSTIC_QUERIES.values() 
            for query in category
        ]
        
        self.assertEqual(len(branded_queries), 3, "Should have exactly 3 branded queries")
        self.assertEqual(len(brand_agnostic_queries), 12, "Should have exactly 12 brand-agnostic queries")
    
    def test_url_normalization(self):
        """Test URL normalization methods"""
        test_urls = [
            'https://www.example.com/page',
            'http://example.com/page/',
            'https://subdomain.example.com/page'
        ]
        
        for url in test_urls:
            normalized = self.audit.normalize_url(url)
            self.assertTrue(normalized.startswith('http'), "Normalized URL should start with http/https")
            self.assertFalse(normalized.endswith('/'), "Normalized URL should not end with /")
    
    def test_domain_extraction(self):
        """Test domain extraction method"""
        test_cases = [
            ('https://www.seriouseats.com/recipe', 'seriouseats.com'),
            ('http://subdomain.example.co.uk/page', 'example.co.uk'),
            ('https://honeybaked.com/products', 'honeybaked.com')
        ]
        
        for url, expected_domain in test_cases:
            extracted_domain = self.audit.extract_domain(url)
            self.assertEqual(extracted_domain, expected_domain, f"Failed to extract domain from {url}")
    
    def test_domain_classification(self):
        """Test domain classification method"""
        test_cases = [
            ('seriouseats.com', 'food_media'),
            ('nytimes.com', 'tier1_news'),
            ('honeybaked.com', 'brand_official'),
            ('randomsite.com', 'other')
        ]
        
        for domain, expected_classification in test_cases:
            classification = self.audit.classify_domain(domain)
            self.assertEqual(classification, expected_classification, f"Incorrect classification for {domain}")
    
    def test_brand_mention_detection(self):
        """Test brand mention detection"""
        test_cases = [
            ('HoneyBaked Ham is delicious', True),
            ('Honey Baked Ham offers great options', True),
            ('This ham is tasty', False),
            ('Try the honeybaked ham today', True)
        ]
        
        for text, expected_result in test_cases:
            result = self.audit.check_brand_mention(text)
            self.assertEqual(result, expected_result, f"Failed brand mention check for: {text}")
    
    def test_mock_query_generation(self):
        """Test mock query generation method"""
        mock_result = self.audit.run_query("Test query", "mock_engine")
        
        self.assertIn('content', mock_result, "Mock query should return content")
        self.assertIn('citations', mock_result, "Mock query should return citations")
        self.assertTrue(isinstance(mock_result['citations'], list), "Citations should be a list")
    
    def test_citation_analysis(self):
        """Test citation analysis method"""
        test_citations = [
            'https://www.seriouseats.com/honeybaked-ham-guide',
            'https://www.example.com/random-article'
        ]
        
        analyzed_citations = self.audit.analyze_citations(test_citations)
        
        self.assertEqual(len(analyzed_citations), len(test_citations), "Should analyze all citations")
        
        for citation in analyzed_citations:
            self.assertIn('url', citation)
            self.assertIn('domain', citation)
            self.assertIn('domain_classification', citation)
            self.assertIn('honeybaked_mentioned', citation)
    
    def test_output_generation(self):
        """Test generation of output CSV files"""
        # Mock results to simulate audit
        mock_results = [
            {
                'query': 'Test branded query',
                'query_type': 'branded',
                'engine': 'mock_engine',
                'content': 'HoneyBaked Ham is great',
                'citations': ['https://honeybaked.com/products']
            }
        ]
        
        # Generate matrices
        query_matrix = self.audit.generate_query_response_matrix(mock_results)
        citation_details = self.audit.generate_citation_details(mock_results)
        competitive_mentions = self.audit.generate_competitive_mentions(mock_results)
        
        # Validate matrices
        self.assertTrue(query_matrix, "Query matrix should not be empty")
        self.assertTrue(citation_details, "Citation details should not be empty")
        self.assertTrue(competitive_mentions, "Competitive mentions should not be empty")
        
        # Validate matrix columns
        expected_query_matrix_columns = [
            'query', 'query_type', 'engine', 'brand_mentioned_in_response', 
            'total_citations', 'citations_mentioning_brand', 
            'response_prominence', 'chef_tim_mentioned'
        ]
        
        for column in expected_query_matrix_columns:
            self.assertTrue(
                all(column in row for row in query_matrix), 
                f"Missing column {column} in query matrix"
            )

def main():
    """Run the test suite"""
    unittest.main()

if __name__ == '__main__':
    main()

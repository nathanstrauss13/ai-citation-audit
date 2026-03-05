#!/usr/bin/env python3
"""
LLM-Powered Response Analyzer

Uses Claude to intelligently analyze LLM responses and extract:
- Competitor mentions and featured brands
- Accurate citation classifications
- Content insights

This replaces basic regex-based detection with sophisticated AI analysis.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ResponseAnalyzer:
    """Analyzes LLM responses using Claude for accurate insights."""

    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required for response analysis")

        self.client = Anthropic(api_key=self.api_key)
        # Use fallback models in case primary isn't available
        self.candidate_models = [
            "claude-sonnet-4-20250514",
            "claude-3-opus-20240229",
            "claude-3-5-sonnet-20241022",
        ]
        self.model = self.candidate_models[0]  # Start with first candidate

    def classify_citations_only(
        self,
        citation_urls: List[str],
        brand_name: str
    ) -> Dict:
        """
        Classify citation URLs into categories using LLM.
        This is a focused, cost-effective approach for citation analysis only.

        Returns:
            {
                'citation_classifications': {
                    'owned': List[str],
                    'editorial': List[str],
                    'retail': List[str],
                    'social_community': List[str],
                    'wikipedia': List[str],
                    'other': List[str]
                }
            }
        """
        if not citation_urls:
            return self._get_empty_citation_classifications()

        citation_list = "\n".join(f"- {url}" for url in citation_urls[:100])

        prompt = f"""Classify these citation URLs into categories for brand: {brand_name}

**Citation URLs to classify:**
{citation_list}

Classify each URL into ONE of these categories:

- **owned**: Brand's own website, blog, or official social media accounts
- **editorial**: News sites, magazines, reputable publications (Forbes, NYT, Vogue, GQ, Travel+Leisure, Condé Nast, etc.)
- **retail**: E-commerce sites (Amazon, Booking.com, Expedia, Hotels.com, retail platforms)
- **social_community**: Social media (Twitter, Instagram, Facebook, TikTok), Reddit, forums, review sites (TripAdvisor, Yelp, Google Reviews)
- **wikipedia**: Wikipedia entries
- **other**: Everything else

Return ONLY valid JSON with URLs sorted into categories:
```json
{{
  "citation_classifications": {{
    "owned": ["url1", "url2"],
    "editorial": ["url3", "url4"],
    "retail": ["url5"],
    "social_community": ["url6", "url7"],
    "wikipedia": ["url8"],
    "other": []
  }}
}}
```"""

        # Try multiple models in case primary isn't available
        for model_name in self.candidate_models:
            try:
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=1500,
                    temperature=0.1,  # Lower temperature for classification
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract JSON from response
                content = response.content[0].text.strip()

                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                result = json.loads(content.strip())

                logger.info(f"Classified {len(citation_urls)} citations with {model_name}")

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse citation classification JSON from {model_name}: {e}")
                continue  # Try next model

            except Exception as e:
                if "not_found_error" in str(e):
                    logger.warning(f"Model {model_name} not found, trying next...")
                    continue
                logger.error(f"Citation classification failed with {model_name}: {e}")
                continue  # Try next model

        # If all models failed
        logger.error("All Claude models failed for citation classification, using fallback")
        return self._get_empty_citation_classifications()

    def analyze_response(
        self,
        query: str,
        response_text: str,
        brand_name: str,
        competitors: List[str],
        citation_urls: List[str]
    ) -> Dict:
        """
        Analyze a single LLM response for comprehensive insights.

        Returns:
            {
                'competitors_mentioned': List[str],
                'featured_brand': str,  # Which brand won/was featured
                'brand_position': int,  # 1-5 or None
                'citation_classifications': {
                    'owned': List[str],
                    'editorial': List[str],
                    'retail': List[str],
                    'social_community': List[str],
                    'wikipedia': List[str],
                    'other': List[str]
                },
                'content_quality': str,  # 'high', 'medium', 'low'
                'sentiment': str  # 'positive', 'neutral', 'negative'
            }
        """

        # Build competitor list for prompt
        competitor_list = "\n".join(f"- {c}" for c in competitors) if competitors else "None provided"
        citation_list = "\n".join(f"- {url}" for url in citation_urls[:100]) if citation_urls else "None"

        prompt = f"""Analyze this AI response and extract structured insights.

**Query:** {query}

**Brand Being Analyzed:** {brand_name}

**Known Competitors:**
{competitor_list}

**Response Text:**
{response_text[:3000]}

**Citation URLs:**
{citation_list}

Please analyze and return a JSON object with:

1. **competitors_mentioned**: List of competitor brand names actually mentioned in the response
2. **featured_brand**: Which brand was featured/recommended FIRST or most prominently (could be the focal brand or a competitor)
3. **brand_position**: Position where {brand_name} appeared (1-5, or null if not in a numbered list)
4. **citation_classifications**: Classify each citation URL into categories:
   - **owned**: Brand's own website/blog/social
   - **editorial**: News sites, magazines, reputable publications (Forbes, NYT, Vogue, GQ, etc.)
   - **retail**: E-commerce sites (Amazon, Nordstrom, etc.)
   - **social_community**: Social media, Reddit, forums, review sites
   - **wikipedia**: Wikipedia entries
   - **other**: Everything else

   Return as: {{"owned": [...], "editorial": [...], "retail": [...], "social_community": [...], "wikipedia": [...], "other": [...]}}

5. **content_quality**: Rate the response quality: "high" (detailed, helpful), "medium" (adequate), or "low" (vague, unhelpful)
6. **sentiment**: Overall sentiment toward {brand_name}: "positive", "neutral", or "negative"

Return ONLY valid JSON, no explanation:
```json
{{
  "competitors_mentioned": ["Brand A", "Brand B"],
  "featured_brand": "Brand A",
  "brand_position": 2,
  "citation_classifications": {{
    "owned": ["https://example.com"],
    "editorial": ["https://forbes.com/article"],
    "retail": ["https://amazon.com/product"],
    "social_community": ["https://reddit.com/r/example"],
    "wikipedia": ["https://en.wikipedia.org/wiki/Example"],
    "other": []
  }},
  "content_quality": "high",
  "sentiment": "positive"
}}
```"""

        # Try multiple models in case primary isn't available
        for model_name in self.candidate_models:
            try:
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=2000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract JSON from response
                content = response.content[0].text.strip()

                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                result = json.loads(content.strip())

                logger.info(f"Analyzed response with {model_name}: {len(result.get('competitors_mentioned', []))} competitors, "
                           f"featured: {result.get('featured_brand', 'none')}")

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM analysis JSON from {model_name}: {e}")
                continue  # Try next model

            except Exception as e:
                if "not_found_error" in str(e):
                    logger.warning(f"Model {model_name} not found, trying next...")
                    continue
                logger.error(f"LLM analysis failed with {model_name}: {e}")
                continue  # Try next model

        # If all models failed
        logger.error("All Claude models failed, using fallback analysis")
        return self._get_fallback_analysis()

    def _get_empty_citation_classifications(self) -> Dict:
        """Return empty citation classification structure."""
        return {
            'citation_classifications': {
                'owned': [],
                'editorial': [],
                'retail': [],
                'social_community': [],
                'wikipedia': [],
                'other': []
            }
        }

    def _get_fallback_analysis(self) -> Dict:
        """Return empty analysis structure if LLM fails."""
        return {
            'competitors_mentioned': [],
            'featured_brand': '',
            'brand_position': None,
            'citation_classifications': {
                'owned': [],
                'editorial': [],
                'retail': [],
                'social_community': [],
                'wikipedia': [],
                'other': []
            },
            'content_quality': 'unknown',
            'sentiment': 'neutral'
        }

    def batch_analyze_responses(
        self,
        responses: List[Dict],
        brand_name: str,
        competitors: List[str],
        max_responses: Optional[int] = None
    ) -> List[Dict]:
        """
        Analyze multiple responses in batch.

        Args:
            responses: List of response dicts with 'query', 'full_output', 'citation_urls'
            brand_name: The focal brand name
            competitors: List of competitor names
            max_responses: Optional limit (for testing/cost control)

        Returns:
            Enriched responses with analysis data
        """
        results = []

        responses_to_analyze = responses[:max_responses] if max_responses else responses

        logger.info(f"Batch analyzing {len(responses_to_analyze)} responses...")

        for i, resp in enumerate(responses_to_analyze, 1):
            logger.info(f"Analyzing response {i}/{len(responses_to_analyze)}...")

            # Parse citation URLs (handle both newline and pipe separated)
            citation_urls_str = resp.get('citation_urls', '')
            if citation_urls_str:
                if '\n' in citation_urls_str:
                    citation_urls = [u.strip() for u in citation_urls_str.split('\n') if u.strip()]
                else:
                    citation_urls = [u.strip() for u in citation_urls_str.split('|') if u.strip()]
            else:
                citation_urls = []

            analysis = self.analyze_response(
                query=resp.get('query', resp.get('query_text', '')),
                response_text=resp.get('full_output', ''),
                brand_name=brand_name,
                competitors=competitors,
                citation_urls=citation_urls
            )

            # Merge analysis into response
            enriched = {**resp, **analysis}
            results.append(enriched)

        logger.info(f"Batch analysis complete: {len(results)} responses enriched")
        return results

    def batch_classify_citations(
        self,
        responses: List[Dict],
        brand_name: str,
        max_responses: Optional[int] = None
    ) -> List[Dict]:
        """
        Classify citations for multiple responses using lightweight LLM approach.
        Competitors are extracted using regex (already in CSV), this only classifies URLs.

        Args:
            responses: List of response dicts with 'citation_urls'
            brand_name: The focal brand name
            max_responses: Optional limit (for testing/cost control)

        Returns:
            Enriched responses with citation classifications
        """
        results = []

        responses_to_analyze = responses[:max_responses] if max_responses else responses

        logger.info(f"Classifying citations for {len(responses_to_analyze)} responses...")

        for i, resp in enumerate(responses_to_analyze, 1):
            logger.info(f"Classifying citations {i}/{len(responses_to_analyze)}...")

            # Parse citation URLs (handle both newline and pipe separated)
            citation_urls_str = resp.get('citation_urls', '')
            if citation_urls_str:
                if '\n' in citation_urls_str:
                    citation_urls = [u.strip() for u in citation_urls_str.split('\n') if u.strip()]
                else:
                    citation_urls = [u.strip() for u in citation_urls_str.split('|') if u.strip()]
            else:
                citation_urls = []

            # Only classify citations (competitors already in CSV from regex)
            classification = self.classify_citations_only(
                citation_urls=citation_urls,
                brand_name=brand_name
            )

            # Merge classification into response
            enriched = {**resp, **classification}
            results.append(enriched)

        logger.info(f"Citation classification complete: {len(results)} responses enriched")
        return results


def enrich_csv_data(csv_rows: List[Dict], brand_name: str, competitors: List[str]) -> List[Dict]:
    """
    Convenience function to enrich CSV data with LLM analysis.

    Args:
        csv_rows: Raw CSV data
        brand_name: Focal brand name
        competitors: List of competitors

    Returns:
        Enriched data ready for dashboard generation
    """
    analyzer = ResponseAnalyzer()
    return analyzer.batch_analyze_responses(csv_rows, brand_name, competitors)


def classify_citations_in_csv(csv_rows: List[Dict], brand_name: str) -> List[Dict]:
    """
    Lightweight function to classify citations only (competitors already extracted via regex).

    Args:
        csv_rows: Raw CSV data with citation_urls column
        brand_name: Focal brand name

    Returns:
        Enriched data with citation classifications only
    """
    analyzer = ResponseAnalyzer()
    return analyzer.batch_classify_citations(csv_rows, brand_name)

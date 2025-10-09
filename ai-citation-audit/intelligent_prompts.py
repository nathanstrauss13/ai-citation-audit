#!/usr/bin/env python3
"""
Intelligent Prompt Generation for AI Citation Audit System

Uses AI to analyze brands and generate personalized, industry-specific prompts
that better measure PR visibility based on media cited by LLMs.
"""

import os
import re
import json
import requests
from typing import List, Dict, Tuple, Optional

def analyze_brand_with_ai(brand: str, competitors: List[str], api_key: str, region: str = "US") -> Dict:
    """
    Use AI to analyze a brand and determine industry, key attributes, and competitive landscape
    """
    competitors_str = ", ".join(competitors) if competitors else "unknown"
    
    analysis_prompt = f"""
Analyze the brand "{brand}" and provide a structured analysis for PR visibility measurement.

Competitors mentioned: {competitors_str}
Region: {region}

Please provide a JSON response with the following structure:
{{
    "industry": "primary industry category",
    "sub_industries": ["specific", "sub-categories"],
    "business_model": "B2B/B2C/B2B2C",
    "key_attributes": ["premium", "sustainable", "innovative", "etc"],
    "target_audiences": ["consumers", "businesses", "investors", "etc"],
    "typical_news_topics": ["product launches", "earnings", "partnerships", "etc"],
    "competitive_positioning": "how brand typically positions vs competitors",
    "media_focus_areas": ["areas where brand seeks media coverage"],
    "seasonal_relevance": ["Q1", "Q2", "Q3", "Q4", "holiday", "none"],
    "geographic_scope": "local/regional/national/global"
}}

Focus on insights that would help measure PR visibility and media citation patterns.
"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a brand analysis expert. Provide accurate, structured analysis in JSON format."},
                {"role": "user", "content": analysis_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"API Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"AI Analysis Content: {content[:200]}...")
            analysis_result = json.loads(content)
            
            # Enhance fallback analysis with AI insights
            enhanced_analysis = get_fallback_analysis(brand, competitors)
            enhanced_analysis.update(analysis_result)
            return enhanced_analysis
        else:
            print(f"API Error: {response.text}")
            return get_fallback_analysis(brand, competitors)
            
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return get_fallback_analysis(brand, competitors)

def get_fallback_analysis(brand: str, competitors: List[str]) -> Dict:
    """
    Fallback analysis when AI analysis fails
    """
    brand_lower = brand.lower()
    
    # Basic industry detection
    if any(term in brand_lower for term in ["food", "ham", "chicken", "turkey", "meat", "restaurant"]):
        industry = "Food & Beverage"
        sub_industries = ["Food Processing", "Consumer Packaged Goods"]
    elif any(term in brand_lower for term in ["tech", "software", "app", "digital", "ai", "data"]):
        industry = "Technology"
        sub_industries = ["Software", "Digital Services"]
    elif any(term in brand_lower for term in ["bank", "financial", "invest", "capital", "fund"]):
        industry = "Financial Services"
        sub_industries = ["Banking", "Investment"]
    elif any(term in brand_lower for term in ["health", "medical", "pharma", "bio", "care"]):
        industry = "Healthcare"
        sub_industries = ["Healthcare Services", "Medical Devices"]
    else:
        industry = "Consumer Goods"
        sub_industries = ["Consumer Products"]
    
    return {
        "industry": industry,
        "sub_industries": sub_industries,
        "business_model": "B2C",
        "key_attributes": ["quality", "trusted"],
        "target_audiences": ["consumers"],
        "typical_news_topics": ["product launches", "company news"],
        "competitive_positioning": "established player",
        "media_focus_areas": ["product quality", "market presence"],
        "seasonal_relevance": ["none"],
        "geographic_scope": "national"
    }

def generate_intelligent_prompts(brand: str, competitors: List[str], brand_analysis: Dict, 
                               region: str = "US", language: str = "English", 
                               time_hint: str = "") -> List[str]:
    """
    Generate intelligent, personalized prompts based on brand analysis
    """
    industry = brand_analysis.get("industry", "Consumer Goods")
    sub_industries = brand_analysis.get("sub_industries", [])
    key_attributes = brand_analysis.get("key_attributes", [])
    business_model = brand_analysis.get("business_model", "B2C")
    target_audiences = brand_analysis.get("target_audiences", ["consumers"])
    typical_news_topics = brand_analysis.get("typical_news_topics", [])
    competitive_positioning = brand_analysis.get("competitive_positioning", "")
    seasonal_relevance = brand_analysis.get("seasonal_relevance", [])
    
    # Language and region formatting
    lang_hint = f"Respond in {language}." if language else ""
    time_suffix = f" Focus on {time_hint}." if time_hint and time_hint.strip() else ""
    region_phrase = f"in {region}" if region else ""
    
    prompts = []
    
    # 1. Brand Authority & Presence
    prompts.extend([
        f"Tell me about {brand}. {lang_hint}{time_suffix}",
        f"What is {brand} known for? {lang_hint}{time_suffix}",
        f"Please tell me about recent news from {brand}. {lang_hint}{time_suffix}"
    ])
    
    # 2. Industry Leadership & Competitive Context
    if sub_industries:
        primary_sub = sub_industries[0]
        prompts.append(f"Who are the leading {primary_sub.lower()} companies {region_phrase}? {lang_hint}{time_suffix}")
    
    prompts.append(f"Top {industry.lower()} companies {region_phrase}. {lang_hint}{time_suffix}")
    
    # 3. Attribute-based queries (personalized to brand)
    attribute_queries = []
    for attr in key_attributes[:3]:  # Limit to top 3 attributes
        if attr.lower() in ["premium", "luxury", "high-end"]:
            if industry == "Food & Beverage":
                attribute_queries.append(f"best premium {industry.lower()} brands {region_phrase}")
            else:
                attribute_queries.append(f"premium {industry.lower()} companies {region_phrase}")
        elif attr.lower() in ["sustainable", "eco-friendly", "green"]:
            attribute_queries.append(f"most sustainable {industry.lower()} companies {region_phrase}")
        elif attr.lower() in ["innovative", "technology", "tech-forward"]:
            attribute_queries.append(f"most innovative {industry.lower()} companies {region_phrase}")
        elif attr.lower() in ["quality", "reliable", "trusted"]:
            attribute_queries.append(f"highest quality {industry.lower()} brands {region_phrase}")
        elif attr.lower() in ["affordable", "value", "budget"]:
            attribute_queries.append(f"best value {industry.lower()} brands {region_phrase}")
    
    # Add language and time hints to attribute queries
    for query in attribute_queries[:2]:  # Limit to 2 attribute queries
        prompts.append(f"{query}. {lang_hint}{time_suffix}")
    
    # 4. Industry-specific specialized queries
    specialized_queries = []
    
    # Food & Beverage specific queries (especially for ham/meat companies)
    if industry == "Food & Beverage" and any(term in brand.lower() for term in ["ham", "meat", "turkey", "chicken", "food"]):
        specialized_queries.extend([
            "best spiral cut ham brands",
            "where to buy holiday ham online", 
            "ham delivery services for Easter",
            "gourmet ham gift baskets",
            "best ham for Thanksgiving dinner",
            "spiral sliced ham companies in US",
            "premium meat delivery services",
            "artisanal ham producers"
        ])
    
    # Add specialized queries with language/time hints
    for query in specialized_queries[:3]:  # Limit to 3 specialized queries
        prompts.append(f"{query}. {lang_hint}{time_suffix}")
    
    # 5. News Topic-based queries (based on typical coverage areas)
    news_queries = []
    for topic in typical_news_topics[:2]:  # Limit to top 2 topics
        if topic.lower() in ["product launches", "new products"]:
            news_queries.append(f"recent {brand} product launches")
        elif topic.lower() in ["earnings", "financial", "revenue"]:
            news_queries.append(f"{brand} financial performance 2024 2025")
        elif topic.lower() in ["partnerships", "acquisitions", "deals"]:
            news_queries.append(f"{brand} partnerships and acquisitions")
        elif topic.lower() in ["expansion", "growth"]:
            news_queries.append(f"{brand} expansion plans")
    
    for query in news_queries:
        prompts.append(f"{query}. {lang_hint}{time_suffix}")
    
    # 5. Competitive Comparisons (personalized)
    for competitor in competitors[:2]:  # Limit to 2 competitors
        prompts.append(f"Compare {brand} and {competitor}. {lang_hint}{time_suffix}")
    
    # 6. Seasonal/Contextual queries (if relevant)
    if "holiday" in seasonal_relevance and industry == "Food & Beverage":
        prompts.append(f"best {industry.lower()} brands for holidays {region_phrase}. {lang_hint}{time_suffix}")
    
    # 7. Target audience specific queries
    if "businesses" in target_audiences:
        prompts.append(f"{brand} business solutions. {lang_hint}{time_suffix}")
    if "investors" in target_audiences:
        prompts.append(f"{brand} investment outlook. {lang_hint}{time_suffix}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_prompts = []
    for prompt in prompts:
        if prompt not in seen:
            seen.add(prompt)
            unique_prompts.append(prompt)
    
    return unique_prompts[:12]  # Limit to 12 prompts max

def build_intelligent_prompt_pack(brand: str, competitors: List[str], region: str = "US", 
                                language: str = "English", time_hint: str = "", 
                                openai_api_key: str = None) -> Tuple[List[str], Dict]:
    """
    Main function to build intelligent prompt pack
    Returns: (prompts, brand_analysis)
    """
    competitors_list = [c.strip() for c in competitors if c.strip()] if isinstance(competitors, list) else [c.strip() for c in str(competitors).split(",") if c.strip()]
    
    # Get brand analysis
    if openai_api_key:
        brand_analysis = analyze_brand_with_ai(brand, competitors_list, openai_api_key, region)
    else:
        brand_analysis = get_fallback_analysis(brand, competitors_list)
    
    # Generate intelligent prompts
    prompts = generate_intelligent_prompts(
        brand, competitors_list, brand_analysis, region, language, time_hint
    )
    
    return prompts, brand_analysis

# Test function
if __name__ == "__main__":
    # Test with different brands
    test_cases = [
        ("Apple", ["Microsoft", "Google"], "US"),
        ("Tesla", ["Ford", "GM"], "US"),
        ("Starbucks", ["Dunkin", "Costa Coffee"], "US"),
        ("Goldman Sachs", ["JPMorgan", "Morgan Stanley"], "US")
    ]
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    for brand, competitors, region in test_cases:
        print(f"\n=== {brand} ===")
        prompts, analysis = build_intelligent_prompt_pack(
            brand, competitors, region, openai_api_key=openai_key
        )
        print(f"Industry: {analysis.get('industry')}")
        print(f"Key Attributes: {analysis.get('key_attributes')}")
        print("Prompts:")
        for i, prompt in enumerate(prompts, 1):
            print(f"  {i}. {prompt}")

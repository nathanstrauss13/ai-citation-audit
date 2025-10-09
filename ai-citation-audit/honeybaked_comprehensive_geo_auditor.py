#!/usr/bin/env python3
"""
HoneyBaked Ham Holiday GEO Citation Analysis - Comprehensive Data Collection

Implements the complete methodology framework with:
- 35 unique queries (140 total tests across 4 platforms)
- 4 comprehensive CSV outputs
- Detailed domain and content classification
- PR media target tracking
- Competitive context analysis
- Chef Tim Ziga authority tracking

Usage:
    python honeybaked_comprehensive_geo_auditor.py
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
from typing import Dict, List, Set, Tuple

# Load environment variables
try:
    from load_env import load_env
    load_env()
except ImportError:
    pass

# ============================================================================
# DOMAIN CLASSIFICATION SYSTEM
# ============================================================================

DOMAIN_CLASSIFICATIONS = {
    # Brand official
    "honeybaked.com": "brand_official",
    "thehoneybakedhams.com": "brand_official",
    
    # Competitor official
    "omahasteaks.com": "competitor_official",
    "harryanddavid.com": "competitor_official",
    "costco.com": "competitor_official",
    "wholefoodsmarket.com": "competitor_official",
    "smithfieldfoods.com": "competitor_official",
    
    # Editorial Tier 1
    "foodandwine.com": "editorial_tier1",
    "bonappetit.com": "editorial_tier1",
    "seriouseats.com": "editorial_tier1",
    "epicurious.com": "editorial_tier1",
    
    # Editorial Tier 2
    "allrecipes.com": "editorial_tier2",
    "delish.com": "editorial_tier2",
    "tasteofhome.com": "editorial_tier2",
    "thekitchn.com": "editorial_tier2",
    
    # Editorial Tier 3
    "bustle.com": "editorial_tier3",
    "refinery29.com": "editorial_tier3",
    "buzzfeed.com": "editorial_tier3",
    
    # Lifestyle Tier 1
    "businessinsider.com": "lifestyle_tier1",
    "forbes.com": "lifestyle_tier1",
    "cnn.com": "lifestyle_tier1",
    
    # Lifestyle Tier 2
    "gq.com": "lifestyle_tier2",
    "southernliving.com": "lifestyle_tier2",
    "realsimple.com": "lifestyle_tier2",
    
    # News Media
    "nytimes.com": "news_media",
    "wsj.com": "news_media",
    "reuters.com": "news_media",
    "apnews.com": "news_media",
    
    # Food Trade
    "restaurantbusinessonline.com": "food_trade",
    "qsrmagazine.com": "food_trade",
    "nrn.com": "food_trade",
    
    # Retail Trade
    "retaildive.com": "retail_trade",
    "chainstoreage.com": "retail_trade",
    
    # Franchise Trade
    "franchisetimes.com": "franchise_trade",
    "entrepreneur.com": "franchise_trade",
    
    # Retail Partners
    "amazon.com": "retail_partner",
    "walmart.com": "retail_partner",
    "target.com": "retail_partner",
    "kroger.com": "retail_partner",
    
    # E-commerce Marketplace
    "etsy.com": "ecommerce_marketplace",
    "ebay.com": "ecommerce_marketplace",
    
    # PR Wire
    "prnewswire.com": "pr_wire",
    "businesswire.com": "pr_wire",
    "globenewswire.com": "pr_wire",
    
    # Reference
    "wikipedia.org": "wiki_reference",
    "britannica.com": "wiki_reference",
    
    # Review Platforms
    "yelp.com": "review_platform",
    "tripadvisor.com": "review_platform",
    "trustpilot.com": "review_platform",
    
    # Social
    "reddit.com": "social_reddit",
    "youtube.com": "social_youtube",
    "tiktok.com": "social_tiktok",
    "instagram.com": "social_instagram",
    "quora.com": "user_forum",
}

# ============================================================================
# CONTENT TYPE PATTERNS
# ============================================================================

CONTENT_TYPE_PATTERNS = {
    "buying_guide": [r"best\s+\w+", r"buying\s+guide", r"top\s+\d+", r"ultimate\s+guide"],
    "product_review": [r"review", r"tested", r"we tried"],
    "holiday_guide": [r"holiday", r"thanksgiving", r"christmas", r"seasonal"],
    "gift_guide": [r"gift", r"present", r"giving"],
    "recipe_content": [r"recipe", r"how to cook", r"preparation"],
    "how_to_guide": [r"how to", r"tips", r"guide to"],
    "news_article": [r"news", r"announces", r"reported"],
    "listicle": [r"\d+\s+\w+", r"list of"],
    "comparison_article": [r"vs\.", r"versus", r"compared", r"comparison"],
}

# ============================================================================
# PR TARGET MEDIA (from brief)
# ============================================================================

PR_TARGET_MEDIA = {
    "businessinsider.com": "Business Insider",
    "seriouseats.com": "Serious Eats",
    "allrecipes.com": "Allrecipes",
    "thespruceeats.com": "The Spruce Eats",
    "goodhousekeeping.com": "Good Housekeeping",
    "cnn.com": "CNN",
    "consumerreports.org": "Consumer Reports",
    "eater.com": "Eater",
    "foodandwine.com": "Food & Wine",
    "southernliving.com": "Southern Living",
    "bonappetit.com": "Bon Appétit",
}

# ============================================================================
# QUERY SET (35 queries as specified)
# ============================================================================

QUERY_SET = {
    # BRANDED QUERIES (7 queries)
    "branded": [
        "What is HoneyBaked Ham known for?",
        "Tell me about HoneyBaked Ham",
        "HoneyBaked Ham history and reputation",
        "Where can I buy HoneyBaked Ham?",
        "HoneyBaked Ham reviews and ratings",
        "Who is Chef Tim Ziga?",
        "HoneyBaked Ham holiday menu 2025",
    ],
    
    # PRIMARY HOLIDAY QUERIES (10 queries)
    "primary_holiday": [
        "What is the best ham for Thanksgiving dinner?",
        "What is the best ham for Christmas dinner?",
        "Where can I order a holiday ham quickly?",
        "What should I serve for Christmas dinner if I don't want to cook?",
        "What is the easiest holiday meal to order online?",
        "Best place to order Thanksgiving dinner",
        "Last minute holiday meal delivery",
        "Pre-cooked holiday ham delivery",
        "Complete Christmas dinner delivery service",
        "Best spiral cut ham for holidays",
    ],
    
    # GIFT & CONVENIENCE QUERIES (8 queries)
    "gift_convenience": [
        "What's the best food gift for the holidays?",
        "Best holiday food gifts to send",
        "Premium holiday ham gifts",
        "Corporate holiday food gifts",
        "Holiday meal gift baskets",
        "Best mail order holiday ham",
        "Gourmet holiday food gifts",
        "Holiday dinner catering services",
    ],
    
    # COMPETITIVE COMPARISON QUERIES (5 queries)
    "competitive": [
        "Best premium ham brands",
        "Compare holiday ham delivery services",
        "Omaha Steaks vs HoneyBaked Ham vs Harry & David",
        "Where do people order holiday hams from?",
        "Most popular holiday meal delivery companies",
    ],
    
    # QUALITY & EXPERTISE QUERIES (5 queries)
    "expertise": [
        "How to choose the best holiday ham",
        "What makes a quality spiral cut ham?",
        "Holiday ham preparation tips from chefs",
        "How to serve holiday ham like a professional",
        "Best honey glazed ham recipes",
    ],
}

COMPETITOR_BRANDS = [
    "Omaha Steaks",
    "Harry & David",
    "Costco",
    "Whole Foods",
    "Smithfield",
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_url(url: str) -> str:
    """Normalize URL for comparison"""
    try:
        if not url or url.startswith("data:") or url.startswith("#"):
            return ""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path or ""
        path = path.rstrip("/")
        return f"{parsed.scheme}://{netloc}{path}"
    except Exception:
        return url or ""

def extract_domain(url: str) -> str:
    """Extract domain from URL (no www., no paths)"""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.split(":")[0]
    except Exception:
        return ""

def classify_domain(domain: str) -> str:
    """Classify domain according to specification"""
    if not domain:
        return "other"
    
    # Direct match
    if domain in DOMAIN_CLASSIFICATIONS:
        return DOMAIN_CLASSIFICATIONS[domain]
    
    # Check if subdomain of known domain
    for known_domain, classification in DOMAIN_CLASSIFICATIONS.items():
        if domain.endswith(f".{known_domain}"):
            return classification
    
    return "other"

def classify_content_type(url: str, page_title: str = "") -> str:
    """Classify content type based on URL and title"""
    combined = f"{url} {page_title}".lower()
    
    for content_type, patterns in CONTENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined):
                return content_type
    
    # Fallback based on URL structure
    if "/recipe" in url.lower():
        return "recipe_content"
    elif "/review" in url.lower():
        return "product_review"
    elif "/news" in url.lower():
        return "news_article"
    
    return "owned_content" if "honeybaked" in combined else "other"

def determine_media_tier(domain: str, classification: str) -> str:
    """Determine media tier for PR tracking"""
    if classification in ["editorial_tier1", "lifestyle_tier1"]:
        return "tier1_lifestyle"
    elif classification == "editorial_tier2":
        return "tier2_food"
    elif classification == "editorial_tier3":
        return "tier3_general"
    elif classification in ["food_trade", "retail_trade", "franchise_trade"]:
        return "trade"
    elif classification == "wiki_reference":
        return "reference"
    else:
        return "other"

# ============================================================================
# API ADAPTERS
# ============================================================================

def query_perplexity(prompt: str, api_key: str, timeout: int = 30) -> Dict:
    """Query Perplexity API"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant. Provide detailed answers with citations."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "return_citations": True,
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return {"content": f"[error {resp.status_code}]", "citations": []}
        
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        citations = data.get("citations", [])
        
        # Normalize citations
        normalized = []
        seen = set()
        for citation in citations:
            if isinstance(citation, str):
                norm = normalize_url(citation)
                if norm and norm not in seen:
                    seen.add(norm)
                    normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"    Perplexity error: {e}")
        return {"content": f"[exception: {e}]", "citations": []}

def query_chatgpt(prompt: str, api_key: str, timeout: int = 30) -> Dict:
    """Query ChatGPT API"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant. Always include source citations with URLs in your responses. Format them as 'Source: https://...'"},
            {"role": "user", "content": f"{prompt}\n\nPlease include at least 5 source citations with URLs."}
        ],
        "temperature": 0.1,
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return {"content": f"[error {resp.status_code}]", "citations": []}
        
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"    ChatGPT error: {e}")
        return {"content": f"[exception: {e}]", "citations": []}

def query_claude(prompt: str, api_key: str, timeout: int = 35) -> Dict:
    """Query Claude API"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "temperature": 0.1,
        "system": "You are a research assistant. Always include source citations with URLs. Format them as 'Reference: https://...'",
        "messages": [{"role": "user", "content": f"{prompt}\n\nPlease include at least 5 reference citations with URLs."}]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return {"content": f"[error {resp.status_code}]", "citations": []}
        
        data = resp.json()
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"    Claude error: {e}")
        return {"content": f"[exception: {e}]", "citations": []}

def query_gemini(prompt: str, api_key: str, timeout: int = 30) -> Dict:
    """Query Gemini API"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(
            f"{prompt}\n\nPlease include source citations with URLs formatted as 'URL: https://...'",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        content = response.text if response.text else ""
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except ImportError:
        return {"content": "[gemini not available]", "citations": []}
    except Exception as e:
        print(f"    Gemini error: {e}")
        return {"content": f"[exception: {e}]", "citations": []}

# ============================================================================
# DATA COLLECTION
# ============================================================================

def run_comprehensive_audit(api_keys: Dict) -> List[Dict]:
    """Run complete audit across all queries and platforms"""
    
    all_queries = []
    for category, queries in QUERY_SET.items():
        for query in queries:
            all_queries.append({"query": query, "category": category})
    
    print(f"\n🔍 Running comprehensive audit:")
    print(f"  - Total queries: {len(all_queries)}")
    print(f"  - Platforms: ChatGPT, Claude, Perplexity, Gemini")
    print(f"  - Total tests: {len(all_queries) * 4} (140 expected)")
    
    results = []
    
    for i, query_data in enumerate(all_queries):
        query = query_data["query"]
        category = query_data["category"]
        query_type = "BRANDED" if category == "branded" else "UNBRANDED"
        
        print(f"\n[{i+1}/{len(all_queries)}] {query[:60]}...")
        
        # ChatGPT
        if api_keys.get("openai"):
            print("  → ChatGPT", end="", flush=True)
            result = query_chatgpt(query, api_keys["openai"])
            results.append({
                "engine": "ChatGPT",
                "query": query,
                "query_category": category,
                "query_type": query_type,
                "content": result["content"],
                "citations": result["citations"],
                "timestamp": datetime.datetime.now().isoformat(),
            })
            print(" ✓")
            time.sleep(1)
        
        # Claude
        if api_keys.get("anthropic"):
            print("  → Claude", end="", flush=True)
            result = query_claude(query, api_keys["anthropic"])
            results.append({
                "engine": "Claude",
                "query": query,
                "query_category": category,
                "query_type": query_type,
                "content": result["content"],
                "citations": result["citations"],
                "timestamp": datetime.datetime.now().isoformat(),
            })
            print(" ✓")
            time.sleep(1)
        
        # Perplexity
        if api_keys.get("perplexity"):
            print("  → Perplexity", end="", flush=True)
            result = query_perplexity(query, api_keys["perplexity"])
            results.append({
                "engine": "Perplexity",
                "query": query,
                "query_category": category,
                "query_type": query_type,
                "content": result["content"],
                "citations": result["citations"],
                "timestamp": datetime.datetime.now().isoformat(),
            })
            print(" ✓")
            time.sleep(1)
        
        # Gemini (limited to avoid rate limits)
        if api_keys.get("gemini") and i < 10:  # Only first 10 queries
            print("  → Gemini", end="", flush=True)
            result = query_gemini(query, api_keys["gemini"])
            results.append({
                "engine": "Gemini",
                "query": query,
                "query_category": category,
                "query_type": query_type,
                "content": result["content"],
                "citations": result["citations"],
                "timestamp": datetime.datetime.now().isoformat(),
            })
            print(" ✓")
            time.sleep(4)
    
    return results

# ============================================================================
# CSV GENERATION
# ============================================================================

def generate_analysis_matrix(results: List[Dict], timestamp: str, output_dir: str):
    """Generate FILE 1: HONEYBAKED_ANALYSIS_MATRIX"""
    
    filepath = os.path.join(output_dir, f"HONEYBAKED_ANALYSIS_MATRIX_{timestamp}.csv")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "query",
            "query_type",
            "query_category",
            "commercial_intent",
            "engine",
            "honeybaked_mentioned",
            "competitors_mentioned",
            "featured_brand",
            "honeybaked_prominence",
            "response_length",
            "total_citations",
            "honeybaked_citations",
            "competitor_citations",
            "owned_media_citations",
            "earned_media_citations",
            "chef_tim_ziga_mentioned",
            "test_timestamp",
            "platform_response_quality",
            "notes",
        ])
        
        # Write rows
        for result in results:
            query = result["query"]
            query_type = result["query_type"]
            query_category = result["query_category"].upper()
            engine = result["engine"]
            content = result["content"].lower()
            citations = result["citations"]
            
            # Determine commercial intent
            if query_category in ["PRIMARY_HOLIDAY", "GIFT_CONVENIENCE"]:
                commercial_intent = "High"
            elif query_category == "COMPETITIVE":
                commercial_intent = "Medium"
            else:
                commercial_intent = "Low"
            
            # Check brand mentions
            honeybaked_mentioned = "Yes" if "honeybaked" in content or "honey baked" in content else "No"
            
            # Check competitor mentions
            competitors_found = []
            for comp in COMPETITOR_BRANDS:
                if comp.lower() in content:
                    competitors_found.append(comp)
            competitors_mentioned = ",".join(competitors_found) if competitors_found else "None"
            
            # Determine featured brand
            if honeybaked_mentioned == "Yes" and not competitors_found:
                featured_brand = "HoneyBaked Ham"
            elif competitors_found and honeybaked_mentioned == "No":
                featured_brand = competitors_found[0]
            elif competitors_found and honeybaked_mentioned == "Yes":
                # First mentioned wins
                hb_index = content.find("honeybaked")
                if hb_index == -1:
                    hb_index = content.find("honey baked")
                comp_index = min([content.find(c.lower()) for c in competitors_found if content.find(c.lower()) != -1], default=99999)
                featured_brand = "HoneyBaked Ham" if hb_index < comp_index else competitors_found[0]
            else:
                featured_brand = "None"
            
            # Determine prominence
            if honeybaked_mentioned == "No":
                honeybaked_prominence = "not_present"
            else:
                hb_index = content.find("honeybaked")
                if hb_index == -1:
                    hb_index = content.find("honey baked")
                if hb_index < 200:
                    honeybaked_prominence = "high"
                elif hb_index < 500:
                    honeybaked_prominence = "medium"
                else:
                    honeybaked_prominence = "low"
            
            # Response length
            word_count = len(content.split())
            if word_count < 200:
                response_length = "Short (<200 words)"
            elif word_count < 500:
                response_length = "Medium (200-500)"
            else:
                response_length = "Long (500+)"
            
            # Citation analysis
            total_citations = len(citations)
            honeybaked_citations = sum(1 for url in citations if "honeybaked" in extract_domain(url))
            competitor_citations = sum(1 for url in citations if any(comp.lower().replace(" ", "") in extract_domain(url) for comp in COMPETITOR_BRANDS))
            owned_media_citations = honeybaked_citations
            earned_media_citations = total_citations - owned_media_citations
            
            # Chef Tim Ziga
            chef_tim_ziga_mentioned = "Yes" if "tim ziga" in content or "chef tim" in content else "No"
            
            # Platform response quality
            if "[error" in content or "[exception" in content:
                platform_response_quality = "Error"
            elif total_citations == 0:
                platform_response_quality = "Incomplete"
            elif word_count < 50:
                platform_response_quality = "Vague"
            else:
                platform_response_quality = "Clear"
            
            writer.writerow([
                query,
                query_type,
                query_category,
                commercial_intent,
                engine,
                honeybaked_mentioned,
                competitors_mentioned,
                featured_brand,
                honeybaked_prominence,
                response_length,
                total_citations,
                honeybaked_citations,
                competitor_citations,
                owned_media_citations,
                earned_media_citations,
                chef_tim_ziga_mentioned,
                result["timestamp"],
                platform_response_quality,
                "",  # notes
            ])
    
    print(f"✓ Generated: {filepath}")
    return filepath

def generate_citation_details(results: List[Dict], timestamp: str, output_dir: str):
    """Generate FILE 2: CITATION_DETAILS"""
    
    filepath = os.path.join(output_dir, f"CITATION_DETAILS_{timestamp}.csv")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "engine",
            "query",
            "query_category",
            "query_type",
            "citation_url",
            "domain",
            "domain_classification",
            "content_type",
            "honeybaked_mentioned",
            "competitor_mentioned",
            "citation_position",
            "media_tier",
            "page_title",
            "publish_date",
            "citation_context",
        ])
        
        # Write rows
        for result in results:
            engine = result["engine"]
            query = result["query"]
            query_category = result["query_category"].upper()
            query_type = result["query_type"]
            
            for position, citation_url in enumerate(result["citations"], 1):
                domain = extract_domain(citation_url)
                domain_classification = classify_domain(domain)
                content_type = classify_content_type(citation_url)
                
                # Check if HoneyBaked mentioned in domain
                honeybaked_mentioned = "Yes" if "honeybaked" in domain else "Unknown"
                
                # Check if competitor mentioned in domain
                competitor_mentioned = "None"
                for comp in COMPETITOR_BRANDS:
                    comp_clean = comp.lower().replace(" ", "")
                    if comp_clean in domain:
                        competitor_mentioned = comp
                        break
                
                media_tier = determine_media_tier(domain, domain_classification)
                
                writer.writerow([
                    engine,
                    query,
                    query_category,
                    query_type,
                    citation_url,
                    domain,
                    domain_classification,
                    content_type,
                    honeybaked_mentioned,
                    competitor_mentioned,
                    position,
                    media_tier,
                    "",  # page_title - would need web scraping
                    "",  # publish_date - would need web scraping
                    "",  # citation_context
                ])
    
    print(f"✓ Generated: {filepath}")
    return filepath

def generate_competitive_context(results: List[Dict], timestamp: str, output_dir: str):
    """Generate FILE 3: COMPETITIVE_CONTEXT"""
    
    filepath = os.path.join(output_dir, f"COMPETITIVE_CONTEXT_{timestamp}.csv")
    
    all_brands = ["HoneyBaked"] + COMPETITOR_BRANDS
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "brand",
            "query",
            "query_category",
            "query_type",
            "engine",
            "mentioned_in_response",
            "prominence_ranking",
            "tone",
            "specific_products_mentioned",
            "context_of_mention",
            "citation_count_for_brand",
        ])
        
        # Write rows
        for result in results:
            query = result["query"]
            query_category = result["query_category"].upper()
            query_type = result["query_type"]
            engine = result["engine"]
            content = result["content"].lower()
            citations = result["citations"]
            
            # Track mentions for prominence ranking
            brand_mentions = []
            
            for brand in all_brands:
                brand_lower = brand.lower()
                mentioned = brand_lower in content
                
                if mentioned:
                    # Find first occurrence position
                    index = content.find(brand_lower)
                    brand_mentions.append((brand, index))
            
            # Sort by position to get prominence ranking
            brand_mentions.sort(key=lambda x: x[1])
            
            # Write row for each brand
            for brand in all_brands:
                brand_lower = brand.lower()
                mentioned_in_response = "Yes" if brand_lower in content else "No"
                
                # Get prominence ranking
                prominence_ranking = 0
                for rank, (mentioned_brand, _) in enumerate(brand_mentions, 1):
                    if mentioned_brand == brand:
                        prominence_ranking = rank
                        break
                
                # Determine tone (placeholder - would need sentiment analysis)
                tone = "Neutral"
                
                # Check for specific products (placeholder)
                specific_products_mentioned = "No"
                
                # Context of mention
                context_of_mention = ""
                if mentioned_in_response == "Yes":
                    # Find context around mention
                    start = max(0, content.find(brand_lower) - 50)
                    end = min(len(content), content.find(brand_lower) + len(brand_lower) + 50)
                    context_of_mention = content[start:end].strip()[:100]
                
                # Count citations for this brand
                citation_count = 0
                for url in citations:
                    domain = extract_domain(url)
                    if brand_lower.replace(" ", "") in domain:
                        citation_count += 1
                
                writer.writerow([
                    brand,
                    query,
                    query_category,
                    query_type,
                    engine,
                    mentioned_in_response,
                    prominence_ranking if prominence_ranking > 0 else "",
                    tone,
                    specific_products_mentioned,
                    context_of_mention,
                    citation_count,
                ])
    
    print(f"✓ Generated: {filepath}")
    return filepath

def generate_pr_media_targets(results: List[Dict], timestamp: str, output_dir: str):
    """Generate FILE 4: PR_MEDIA_TARGETS"""
    
    filepath = os.path.join(output_dir, f"PR_MEDIA_TARGETS_{timestamp}.csv")
    
    # Track all PR target media appearances
    media_tracking = {}
    
    for media_domain, media_name in PR_TARGET_MEDIA.items():
        media_tracking[media_name] = {
            "domain": media_domain,
            "citation_count": 0,
            "queries_appeared_in": set(),
            "engines_cited_by": set(),
            "content_urls": [],
        }
    
    # Process all results
    for result in results:
        engine = result["engine"]
        query = result["query"]
        
        for citation_url in result["citations"]:
            domain = extract_domain(citation_url)
            
            if domain in PR_TARGET_MEDIA:
                media_name = PR_TARGET_MEDIA[domain]
                media_tracking[media_name]["citation_count"] += 1
                media_tracking[media_name]["queries_appeared_in"].add(query)
                media_tracking[media_name]["engines_cited_by"].add(engine)
                media_tracking[media_name]["content_urls"].append(citation_url)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "media_outlet",
            "domain",
            "target_status",
            "citation_count",
            "queries_appeared_in",
            "engines_cited_by",
            "content_urls",
            "honeybaked_mentioned_in_article",
            "article_publish_dates",
            "media_tier",
            "strategic_value",
        ])
        
        # Write rows
        for media_name, data in sorted(media_tracking.items()):
            target_status = "ACHIEVED" if data["citation_count"] > 0 else "TARGET"
            
            # Determine media tier
            domain = data["domain"]
            classification = classify_domain(domain)
            media_tier = determine_media_tier(domain, classification)
            
            # Determine strategic value
            if domain in ["businessinsider.com", "seriouseats.com", "foodandwine.com"]:
                strategic_value = "High"
            elif domain in ["allrecipes.com", "southernliving.com", "cnn.com"]:
                strategic_value = "Medium"
            else:
                strategic_value = "Low"
            
            writer.writerow([
                media_name,
                data["domain"],
                target_status,
                data["citation_count"],
                "; ".join(sorted(data["queries_appeared_in"])),
                "; ".join(sorted(data["engines_cited_by"])),
                "; ".join(data["content_urls"][:5]),  # Limit to 5 URLs
                "Unknown",  # Would need web scraping
                "",  # Would need web scraping
                media_tier,
                strategic_value,
            ])
    
    print(f"✓ Generated: {filepath}")
    return filepath

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("=" * 70)
    print("🎄 HONEYBAKED HAM HOLIDAY GEO CITATION ANALYSIS")
    print("   Comprehensive Data Collection - 35 Queries × 4 Platforms")
    print("=" * 70)
    
    # Get API keys
    api_keys = {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "perplexity": os.environ.get("PERPLEXITY_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
    }
    
    # Verify at least one API key
    available_platforms = [name for name, key in api_keys.items() if key]
    
    if not available_platforms:
        print("\n❌ ERROR: No API keys found!")
        print("Please set at least one of:")
        print("  - OPENAI_API_KEY (ChatGPT)")
        print("  - ANTHROPIC_API_KEY (Claude)")
        print("  - PERPLEXITY_API_KEY (Perplexity)")
        print("  - GEMINI_API_KEY or GOOGLE_API_KEY (Gemini)")
        sys.exit(1)
    
    print(f"\n✓ Available platforms: {', '.join(available_platforms)}")
    
    # Calculate total queries
    total_queries = sum(len(queries) for queries in QUERY_SET.values())
    print(f"✓ Total queries: {total_queries}")
    print(f"✓ Query breakdown:")
    for category, queries in QUERY_SET.items():
        print(f"  - {category}: {len(queries)} queries")
    
    # Run comprehensive audit
    print("\n" + "=" * 70)
    print("STARTING DATA COLLECTION")
    print("=" * 70)
    
    results = run_comprehensive_audit(api_keys)
    
    print(f"\n✓ Data collection complete!")
    print(f"  - Total responses collected: {len(results)}")
    print(f"  - Total citations: {sum(len(r['citations']) for r in results)}")
    
    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = "case_studies/honeybaked_ham/comprehensive_geo"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n" + "=" * 70)
    print(f"GENERATING CSV FILES")
    print("=" * 70)
    
    # Generate all 4 CSV files
    print("\n[1/4] Generating HONEYBAKED_ANALYSIS_MATRIX...")
    matrix_path = generate_analysis_matrix(results, timestamp, output_dir)
    
    print("\n[2/4] Generating CITATION_DETAILS...")
    citation_path = generate_citation_details(results, timestamp, output_dir)
    
    print("\n[3/4] Generating COMPETITIVE_CONTEXT...")
    competitive_path = generate_competitive_context(results, timestamp, output_dir)
    
    print("\n[4/4] Generating PR_MEDIA_TARGETS...")
    pr_path = generate_pr_media_targets(results, timestamp, output_dir)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    
    # Calculate key metrics
    total_citations = sum(len(r["citations"]) for r in results)
    honeybaked_mentions = sum(1 for r in results if "honeybaked" in r["content"].lower() or "honey baked" in r["content"].lower())
    tim_ziga_mentions = sum(1 for r in results if "tim ziga" in r["content"].lower() or "chef tim" in r["content"].lower())
    
    # PR target tracking
    pr_targets_found = set()
    for result in results:
        for citation in result["citations"]:
            domain = extract_domain(citation)
            if domain in PR_TARGET_MEDIA:
                pr_targets_found.add(PR_TARGET_MEDIA[domain])
    
    print(f"\n📊 Key Metrics:")
    print(f"  - Total responses: {len(results)}")
    print(f"  - Total citations: {total_citations}")
    print(f"  - HoneyBaked mentions: {honeybaked_mentions}/{len(results)} ({100*honeybaked_mentions/len(results):.1f}%)")
    print(f"  - Chef Tim Ziga mentions: {tim_ziga_mentions}")
    print(f"  - PR target media found: {len(pr_targets_found)}/11")
    
    print(f"\n📁 Generated Files:")
    print(f"  1. {matrix_path}")
    print(f"  2. {citation_path}")
    print(f"  3. {competitive_path}")
    print(f"  4. {pr_path}")
    
    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE GEO AUDIT COMPLETE!")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Upload CSV files to Claude for dashboard creation")
    print(f"  2. Review PR target media achievement")
    print(f"  3. Analyze competitive positioning")
    print(f"  4. Develop strategic recommendations")
    
    return {
        "results": results,
        "files": {
            "matrix": matrix_path,
            "citations": citation_path,
            "competitive": competitive_path,
            "pr_targets": pr_path,
        },
        "metrics": {
            "total_responses": len(results),
            "total_citations": total_citations,
            "honeybaked_mentions": honeybaked_mentions,
            "tim_ziga_mentions": tim_ziga_mentions,
            "pr_targets_found": len(pr_targets_found),
        }
    }

if __name__ == "__main__":
    main()

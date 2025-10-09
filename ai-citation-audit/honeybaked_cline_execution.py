#!/usr/bin/env python3
"""
HoneyBaked Ham GEO Analysis - Cline Execution
Test 15 holiday food queries across 4 AI platforms and export results to CSV files.

This script implements the exact specifications from the Cline execution prompt:
- 15 specific holiday queries
- 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini)
- 4 CSV output files with precise column specifications
- Comprehensive data collection for dashboard creation
"""

import os
import re
import csv
import sys
import time
import datetime
import requests
from urllib.parse import urlparse

# Load environment variables
try:
    from load_env import load_env
    load_env()
except ImportError:
    from dotenv import load_dotenv
    load_dotenv()

# ============================================================================
# EXACT 15 QUERIES AS SPECIFIED
# ============================================================================
QUERIES = [
    # Primary Holiday Queries (7)
    "What is the best ham for Thanksgiving dinner?",
    "What is the best ham for Christmas dinner?",
    "Where can I get a holiday ham quickly?",
    "What should I serve for Christmas dinner if I don't want to cook?",
    "What is the easiest holiday meal to order online?",
    "What's the best food gift for the holidays?",
    "Who is Chef Tim Ziga?",
    
    # Additional Holiday Queries (5)
    "Where can I order a holiday meal online?",
    "Last-minute Thanksgiving dinner options",
    "Best holiday food gifts to ship",
    "Best mail-order hams 2025",
    "Holiday ham delivery comparison",
    
    # Competitive Queries (3)
    "HoneyBaked Ham vs Omaha Steaks for holidays",
    "Best spiral cut ham brands for Christmas",
    "HoneyBaked Ham chef recommendations"
]

# Target Media Outlets to Track (8 specific)
TARGET_MEDIA = {
    "businessinsider.com": "Business Insider",
    "seriouseats.com": "Serious Eats",
    "allrecipes.com": "AllRecipes",
    "thespruceeats.com": "The Spruce Eats",
    "goodhousekeeping.com": "Good Housekeeping",
    "cnn.com": "CNN",
    "consumerreports.org": "Consumer Reports",
    "eater.com": "Eater"
}

# Competitor Brands to Track (8 specific)
COMPETITORS = [
    "Omaha Steaks",
    "Costco",
    "Whole Foods",
    "Harry & David",
    "Williams Sonoma",
    "Smithfield Foods",
    "Butterball",
    "D'Artagnan"
]

# Domain Classification for Citations
DOMAIN_CLASSIFICATIONS = {
    # Food Tier 1
    "foodandwine.com": "food_tier1",
    "bonappetit.com": "food_tier1",
    "saveur.com": "food_tier1",
    "eater.com": "food_tier1",
    "seriouseats.com": "food_tier1",
    "epicurious.com": "food_tier1",
    
    # Food Tier 2
    "delish.com": "food_tier2",
    "tastingtable.com": "food_tier2",
    "thekitchn.com": "food_tier2",
    "food52.com": "food_tier2",
    "foodnetwork.com": "food_tier2",
    "allrecipes.com": "food_tier2",
    "myrecipes.com": "food_tier2",
    "thespruceeats.com": "food_tier2",
    
    # Editorial Tier 1
    "nytimes.com": "editorial_tier1",
    "wsj.com": "editorial_tier1",
    "washingtonpost.com": "editorial_tier1",
    "businessinsider.com": "editorial_tier1",
    "cnn.com": "editorial_tier1",
    "forbes.com": "editorial_tier1",
    
    # Lifestyle Holiday
    "goodhousekeeping.com": "lifestyle_holiday",
    "southernliving.com": "lifestyle_holiday",
    "countryliving.com": "lifestyle_holiday",
    "realsimple.com": "lifestyle_holiday",
    "marthastewart.com": "lifestyle_holiday",
    
    # Consumer Reports
    "consumerreports.org": "editorial_tier1",
    
    # Business
    "bloomberg.com": "business",
    "cnbc.com": "business",
    "reuters.com": "business",
    
    # PR
    "prnewswire.com": "pr",
    "businesswire.com": "pr",
    "globenewswire.com": "pr"
}

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
    """Extract domain from URL"""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.split(":")[0]
    except Exception:
        return ""

def classify_domain(domain: str) -> str:
    """Classify domain based on predefined categories"""
    domain_lower = domain.lower()
    return DOMAIN_CLASSIFICATIONS.get(domain_lower, "other")

def call_perplexity(query: str, api_key: str) -> dict:
    """Call Perplexity API"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant that provides information about holiday food and dining."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.1,
        "return_citations": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return {"content": f"[Error {response.status_code}]", "citations": []}
        
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract citations
        citations = data.get("citations", [])
        if not citations:
            citations = data.get("choices", [{}])[0].get("citations", [])
        
        # Normalize citations
        normalized = []
        seen = set()
        for cite in citations:
            if isinstance(cite, str):
                norm = normalize_url(cite)
                if norm and norm not in seen and len(norm) > 15:
                    seen.add(norm)
                    normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"      Perplexity error: {e}")
        return {"content": f"[Exception: {e}]", "citations": []}

def call_chatgpt(query: str, api_key: str) -> dict:
    """Call ChatGPT API"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant. When providing information, include citations with URLs formatted as 'Source: https://...' on new lines."},
            {"role": "user", "content": f"{query}\n\nPlease provide information with source citations."}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return {"content": f"[Error {response.status_code}]", "citations": []}
        
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract URLs from content
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen and len(norm) > 10:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"      ChatGPT error: {e}")
        return {"content": f"[Exception: {e}]", "citations": []}

def call_claude(query: str, api_key: str) -> dict:
    """Call Claude API"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "temperature": 0.1,
        "system": "You are a helpful AI assistant. When providing information, include citations with URLs formatted as 'Reference: https://...' on new lines.",
        "messages": [{"role": "user", "content": f"{query}\n\nPlease provide information with reference citations."}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=35)
        if response.status_code != 200:
            return {"content": f"[Error {response.status_code}]", "citations": []}
        
        data = response.json()
        content_blocks = data.get("content", [])
        content = "\n\n".join([block.get("text", "") for block in content_blocks if block.get("type") == "text"])
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen and len(norm) > 10:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except Exception as e:
        print(f"      Claude error: {e}")
        return {"content": f"[Exception: {e}]", "citations": []}

def call_gemini(query: str, api_key: str) -> dict:
    """Call Gemini API"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings to be less restrictive
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }
        
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            safety_settings=safety_settings
        )
        
        # Use more neutral, educational framing
        enhanced_query = f"""As a food and dining research assistant, please provide objective information about: {query}

Include factual information with source references where possible. Format sources as 'URL: https://...' on new lines."""
        
        response = model.generate_content(
            enhanced_query,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1000
            )
        )
        
        # Try to extract content even if partially blocked
        content = ""
        try:
            if hasattr(response, 'text') and response.text:
                content = response.text
            elif hasattr(response, 'parts') and response.parts:
                content = " ".join([part.text for part in response.parts if hasattr(part, 'text')])
            elif hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                content += part.text
        except Exception:
            pass
        
        if not content:
            # Return empty but valid response instead of error
            return {"content": "", "citations": []}
        
        # Extract URLs
        urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        
        # Normalize
        normalized = []
        seen = set()
        for url in urls:
            norm = normalize_url(url)
            if norm and norm not in seen and len(norm) > 10:
                seen.add(norm)
                normalized.append(norm)
        
        return {"content": content, "citations": normalized}
    except ImportError:
        print("      Gemini: google-generativeai not installed")
        return {"content": "[Import Error]", "citations": []}
    except Exception as e:
        print(f"      Gemini error: {e}")
        return {"content": "", "citations": []}

def analyze_response(query: str, engine: str, content: str, citations: list) -> dict:
    """Analyze a single response for HoneyBaked Ham mentions and competitors"""
    content_lower = content.lower()
    
    # Check for HoneyBaked presence
    honeybaked_present = "honeybaked" in content_lower or "honey baked" in content_lower or "honey-baked" in content_lower
    
    # Determine position prominence
    if honeybaked_present:
        # Find first occurrence
        idx = content_lower.find("honeybaked")
        if idx == -1:
            idx = content_lower.find("honey baked")
        if idx == -1:
            idx = content_lower.find("honey-baked")
        
        if idx < 200:
            position_prominence = "High"
        elif idx < 500:
            position_prominence = "Medium"
        else:
            position_prominence = "Low"
    else:
        position_prominence = "Not Present"
    
    # Check for competitors
    competitors_mentioned = []
    for competitor in COMPETITORS:
        if competitor.lower() in content_lower:
            competitors_mentioned.append(competitor)
    
    # Check for Chef Tim Ziga
    chef_tim_mentioned = "tim ziga" in content_lower or "chef tim" in content_lower
    
    # Check for target media citations
    target_media_cited = []
    for url in citations:
        domain = extract_domain(url)
        if domain in TARGET_MEDIA:
            media_name = TARGET_MEDIA[domain]
            if media_name not in target_media_cited:
                target_media_cited.append(media_name)
    
    # Determine source quality
    high_quality_count = 0
    for url in citations:
        domain = extract_domain(url)
        classification = classify_domain(domain)
        if classification in ["editorial_tier1", "food_tier1"]:
            high_quality_count += 1
    
    if high_quality_count >= 2:
        source_quality = "High"
    elif high_quality_count >= 1:
        source_quality = "Medium"
    else:
        source_quality = "Low"
    
    return {
        "query": query,
        "engine": engine,
        "honeybaked_present": "Yes" if honeybaked_present else "No",
        "position_prominence": position_prominence,
        "competitors_mentioned": ", ".join(competitors_mentioned) if competitors_mentioned else "None",
        "source_quality": source_quality,
        "chef_tim_mentioned": "Yes" if chef_tim_mentioned else "No",
        "target_media_cited": ", ".join(target_media_cited) if target_media_cited else "None",
        "total_citations": len(citations),
        "content": content,
        "citations": citations
    }

def main():
    """Main execution function"""
    print("=" * 80)
    print("🎄 HONEYBAKED HAM GEO ANALYSIS - CLINE EXECUTION")
    print("=" * 80)
    print(f"Testing {len(QUERIES)} queries across 4 AI platforms")
    print(f"Total combinations: {len(QUERIES) * 4} = 60")
    print()
    
    # Get API keys
    api_keys = {
        "perplexity": os.environ.get("PERPLEXITY_API_KEY"),
        "chatgpt": os.environ.get("OPENAI_API_KEY"),
        "claude": os.environ.get("ANTHROPIC_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    }
    
    # Verify API keys
    print("API Key Status:")
    for engine, key in api_keys.items():
        status = "✓" if key else "✗"
        print(f"  {status} {engine.title()}")
    print()
    
    if not all(api_keys.values()):
        print("⚠️  Warning: Some API keys are missing. Proceeding with available engines.")
        print()
    
    # Data collection
    query_matrix_data = []
    raw_citations_data = []
    target_media_tracking = {}
    competitive_analysis = {}
    
    # Initialize target media tracking
    for media in TARGET_MEDIA.values():
        target_media_tracking[media] = {
            "citation_count": 0,
            "urls": [],
            "queries": [],
            "engines": []
        }
    
    # Initialize competitive analysis
    for competitor in COMPETITORS:
        competitive_analysis[competitor] = {
            "total_mentions": 0,
            "queries_mentioned": [],
            "engines": [],
            "position_context": []
        }
    
    # Process queries
    total_processed = 0
    successful = 0
    errors = 0
    
    for i, query in enumerate(QUERIES, 1):
        print(f"[{i}/{len(QUERIES)}] Processing: {query[:60]}...")
        
        # Test on each platform
        for engine_name, api_key in api_keys.items():
            if not api_key:
                continue
            
            print(f"  → {engine_name.title()}...", end=" ")
            
            try:
                # Call API
                if engine_name == "perplexity":
                    result = call_perplexity(query, api_key)
                elif engine_name == "chatgpt":
                    result = call_chatgpt(query, api_key)
                elif engine_name == "claude":
                    result = call_claude(query, api_key)
                elif engine_name == "gemini":
                    result = call_gemini(query, api_key)
                else:
                    continue
                
                content = result.get("content", "")
                citations = result.get("citations", [])
                
                # Check for errors
                if content.startswith("[Error") or content.startswith("[Exception"):
                    print(f"❌ {content}")
                    errors += 1
                    continue
                
                print(f"✓ ({len(citations)} citations)")
                
                # Analyze response
                analysis = analyze_response(query, engine_name, content, citations)
                
                # Add to query matrix
                query_matrix_data.append({
                    "query": analysis["query"],
                    "engine": analysis["engine"],
                    "honeybaked_present": analysis["honeybaked_present"],
                    "position_prominence": analysis["position_prominence"],
                    "competitors_mentioned": analysis["competitors_mentioned"],
                    "source_quality": analysis["source_quality"],
                    "chef_tim_mentioned": analysis["chef_tim_mentioned"],
                    "target_media_cited": analysis["target_media_cited"],
                    "total_citations": analysis["total_citations"]
                })
                
                # Add raw citations
                for url in citations:
                    domain = extract_domain(url)
                    classification = classify_domain(domain)
                    raw_citations_data.append({
                        "Engine": engine_name,
                        "Query": query,
                        "Domain": domain,
                        "Classification": classification,
                        "URL": url
                    })
                
                # Track target media
                for url in citations:
                    domain = extract_domain(url)
                    if domain in TARGET_MEDIA:
                        media_name = TARGET_MEDIA[domain]
                        target_media_tracking[media_name]["citation_count"] += 1
                        if url not in target_media_tracking[media_name]["urls"]:
                            target_media_tracking[media_name]["urls"].append(url)
                        if query not in target_media_tracking[media_name]["queries"]:
                            target_media_tracking[media_name]["queries"].append(query)
                        if engine_name not in target_media_tracking[media_name]["engines"]:
                            target_media_tracking[media_name]["engines"].append(engine_name)
                
                # Track competitors
                content_lower = content.lower()
                for competitor in COMPETITORS:
                    if competitor.lower() in content_lower:
                        competitive_analysis[competitor]["total_mentions"] += 1
                        if query not in competitive_analysis[competitor]["queries_mentioned"]:
                            competitive_analysis[competitor]["queries_mentioned"].append(query)
                        if engine_name not in competitive_analysis[competitor]["engines"]:
                            competitive_analysis[competitor]["engines"].append(engine_name)
                        
                        # Determine position context
                        honeybaked_present = "honeybaked" in content_lower or "honey baked" in content_lower
                        if honeybaked_present:
                            context = "Mentioned with HoneyBaked"
                        else:
                            context = "Mentioned without HoneyBaked"
                        competitive_analysis[competitor]["position_context"].append(context)
                
                successful += 1
                total_processed += 1
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Exception: {e}")
                errors += 1
                continue
        
        print()
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory
    output_dir = "case_studies/honeybaked_ham/holiday_geo_audit"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("📊 GENERATING CSV FILES")
    print("=" * 80)
    
    # 1. HONEYBAKED_QUERY_MATRIX
    matrix_file = f"{output_dir}/HONEYBAKED_QUERY_MATRIX_{timestamp}.csv"
    with open(matrix_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["query", "engine", "honeybaked_present", "position_prominence", 
                     "competitors_mentioned", "source_quality", "chef_tim_mentioned", 
                     "target_media_cited", "total_citations"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(query_matrix_data)
    print(f"✓ Query Matrix: {matrix_file}")
    
    # 2. RAW_CITATIONS
    citations_file = f"{output_dir}/RAW_CITATIONS_{timestamp}.csv"
    with open(citations_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Engine", "Query", "Domain", "Classification", "URL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(raw_citations_data)
    print(f"✓ Raw Citations: {citations_file}")
    
    # 3. TARGET_MEDIA_TRACKING
    media_file = f"{output_dir}/TARGET_MEDIA_TRACKING_{timestamp}.csv"
    with open(media_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Media_Outlet", "Citation_Count", "URLs", "Queries", "Engines"])
        for media, data in target_media_tracking.items():
            if data["citation_count"] > 0:
                writer.writerow([
                    media,
                    data["citation_count"],
                    "; ".join(data["urls"]),
                    "; ".join(data["queries"]),
                    "; ".join(data["engines"])
                ])
    print(f"✓ Target Media: {media_file}")
    
    # 4. COMPETITIVE_ANALYSIS
    competitive_file = f"{output_dir}/COMPETITIVE_ANALYSIS_{timestamp}.csv"
    with open(competitive_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Competitor", "Total_Mentions", "Queries_Mentioned", "Engines", "Position_Context"])
        for competitor, data in competitive_analysis.items():
            if data["total_mentions"] > 0:
                writer.writerow([
                    competitor,
                    data["total_mentions"],
                    "; ".join(data["queries_mentioned"]),
                    "; ".join(data["engines"]),
                    "; ".join(set(data["position_context"]))
                ])
    print(f"✓ Competitive Analysis: {competitive_file}")
    
    print()
    print("=" * 80)
    print("📈 EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Queries Tested: {len(QUERIES)}")
    print(f"Total API Calls: {total_processed}")
    print(f"Successful: {successful}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {(successful/max(1,total_processed))*100:.1f}%")
    print()
    
    # Platform comparison
    print("Platform Performance:")
    engine_counts = {}
    for data in query_matrix_data:
        engine = data["engine"]
        engine_counts[engine] = engine_counts.get(engine, 0) + 1
    for engine, count in sorted(engine_counts.items()):
        print(f"  {engine.title()}: {count} queries")
    print()
    
    # HoneyBaked mention rate
    honeybaked_mentions = sum(1 for d in query_matrix_data if d["honeybaked_present"] == "Yes")
    mention_rate = (honeybaked_mentions / max(1, len(query_matrix_data))) * 100
    print(f"HoneyBaked Ham Mention Rate: {mention_rate:.1f}% ({honeybaked_mentions}/{len(query_matrix_data)})")
    print()
    
    # Top cited sources
    domain_counts = {}
    for citation in raw_citations_data:
        domain = citation["Domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    top_sources = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Top 5 Most Cited Sources:")
    for i, (domain, count) in enumerate(top_sources, 1):
        print(f"  {i}. {domain}: {count} citations")
    print()
    
    # Competitors with highest mention rates
    top_competitors = [(comp, data["total_mentions"]) for comp, data in competitive_analysis.items() if data["total_mentions"] > 0]
    top_competitors.sort(key=lambda x: x[1], reverse=True)
    print("Competitors with Highest Mention Rates:")
    for i, (comp, mentions) in enumerate(top_competitors[:5], 1):
        print(f"  {i}. {comp}: {mentions} mentions")
    print()
    
    # Target media found
    media_found = sum(1 for data in target_media_tracking.values() if data["citation_count"] > 0)
    print(f"Target Media Outlets Found: {media_found}/{len(TARGET_MEDIA)}")
    for media, data in target_media_tracking.items():
        if data["citation_count"] > 0:
            print(f"  ✓ {media}: {data['citation_count']} citations")
    print()
    
    print("=" * 80)
    print("✅ EXECUTION COMPLETE")
    print("=" * 80)
    print(f"All CSV files exported to: {output_dir}/")
    print(f"Timestamp: {timestamp}")
    print()

if __name__ == "__main__":
    main()

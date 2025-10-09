#!/usr/bin/env python3
"""
HoneyBaked Ham Holiday GEO PR Strategy Audit

Comprehensive AI Citation Audit focused on HoneyBaked Ham's Holiday GEO 
(Generative Engine Optimization) PR strategy. Tests how their PR efforts 
are influencing AI-generated responses for holiday shopping queries.

Usage:
    python honeybaked_ham_holiday_geo_audit.py

Features:
- Holiday-focused query set (Thanksgiving, Christmas, gift queries)
- 4-engine audit (Perplexity, ChatGPT, Claude, Gemini)
- PR media target tracking
- GEO-specific analysis and scoring
- Competitive holiday positioning
- Chef Tim Ziga authority tracking
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
from html import escape as html_escape

# Load environment variables
try:
    from load_env import load_env
    load_env()
except ImportError:
    pass

# Holiday-specific PR target media domains
HOLIDAY_PR_TARGET_DOMAINS = {
    "businessinsider.com": "Business Insider",
    "seriouseats.com": "Serious Eats", 
    "allrecipes.com": "AllRecipes",
    "thespruceeats.com": "Spruce Eats",
    "goodhousekeeping.com": "Good Housekeeping",
    "cnn.com": "CNN",
    "consumerreports.org": "Consumer Reports",
    "eater.com": "Eater",
    "southernliving.com": "Southern Living",
    "foodandwine.com": "Food & Wine",
    "bonappetit.com": "Bon Appétit"
}

# Enhanced domain classification for holiday context
FOOD_TIER1_DOMAINS = {
    "foodandwine.com", "bonappetit.com", "saveur.com", "eater.com", 
    "seriouseats.com", "epicurious.com"
}

FOOD_TIER2_DOMAINS = {
    "delish.com", "tastingtable.com", "thekitchn.com", "food52.com",
    "foodnetwork.com", "allrecipes.com", "myrecipes.com", "thespruceeats.com"
}

LIFESTYLE_HOLIDAY_DOMAINS = {
    "goodhousekeeping.com", "southernliving.com", "countryliving.com",
    "realsimple.com", "marthastewart.com", "bhg.com"
}

TIER1_DOMAINS = {
    "nytimes.com", "wsj.com", "washingtonpost.com", "reuters.com",
    "bloomberg.com", "ft.com", "apnews.com", "cnbc.com", "theguardian.com",
    "npr.org", "forbes.com", "time.com", "latimes.com", "abcnews.go.com",
    "nbcnews.com", "usatoday.com", "axios.com", "businessinsider.com", "cnn.com"
}

PR_DOMAINS = {
    "prnewswire.com", "businesswire.com", "globenewswire.com", "prweb.com",
    "newswire.com", "einnews.com"
}

def normalize_url(u: str) -> str:
    """Normalize URL for comparison"""
    try:
        if not u or u.startswith("data:") or u.startswith("#"):
            return ""
        p = urlparse(u)
        netloc = p.netloc.lower()
        path = p.path or ""
        path = path.rstrip("/")
        return f"{p.scheme}://{netloc}{path}"
    except Exception:
        return u or ""

def domain_of(u: str) -> str:
    """Extract domain from URL"""
    try:
        d = urlparse(u).netloc.lower()
        if d.startswith("www."):
            d = d[4:]
        return d.split(":")[0]
    except Exception:
        return ""

def classify_domain_holiday(domain: str) -> str:
    """Enhanced domain classification for holiday context"""
    d = (domain or "").lower()
    if not d:
        return "other"
    
    if d in PR_DOMAINS:
        return "pr"
    if d in FOOD_TIER1_DOMAINS:
        return "food_tier1"
    if d in FOOD_TIER2_DOMAINS:
        return "food_tier2"
    if d in LIFESTYLE_HOLIDAY_DOMAINS:
        return "lifestyle_holiday"
    if d in TIER1_DOMAINS:
        return "editorial_tier1"
    
    return "editorial"

def build_holiday_query_set():
    """Build comprehensive holiday-focused query set"""
    
    # Primary Holiday Queries
    primary_holiday = [
        "What is the best ham for Thanksgiving dinner?",
        "What is the best ham for Christmas dinner?", 
        "Where can I order a holiday meal online?",
        "What should I serve for Christmas dinner if I don't want to cook?",
        "Where can I get a holiday ham quickly?",
        "What's the best food gift for the holidays?"
    ]
    
    # Authority/Expert Queries
    authority_expert = [
        "Who is Chef Tim Ziga?",
        "HoneyBaked Ham chef recommendations"
    ]
    
    # Gift and Convenience Queries
    gift_convenience = [
        "Best mail-order hams 2025",
        "Easiest holiday meal to order online",
        "Last-minute Thanksgiving dinner options", 
        "Best holiday food gifts to ship"
    ]
    
    # Competitive Comparison Queries
    competitive = [
        "HoneyBaked Ham vs Omaha Steaks for holidays",
        "Best spiral cut ham brands for Christmas",
        "Holiday ham delivery comparison"
    ]
    
    all_queries = primary_holiday + authority_expert + gift_convenience + competitive
    
    return {
        'all_queries': all_queries,
        'primary_holiday': primary_holiday,
        'authority_expert': authority_expert, 
        'gift_convenience': gift_convenience,
        'competitive': competitive
    }

def perplexity_chat(prompt: str, api_key: str, model="sonar-pro", timeout=25):
    """Enhanced Perplexity adapter for holiday queries"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "HoneyBaked-Holiday-GEO-Audit/1.0"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": "You are an AI search engine that provides helpful answers about holiday food and dining with citations from reputable, recent sources. Focus on 2024-2025 holiday content when available."
            },
            {"role": "user", "content": f"{prompt} (Please include recent holiday sources from 2024-2025 when available)"}
        ],
        "temperature": 0.1,
        "return_citations": True
    }
    
    try:
        print(f"    Perplexity: Holiday-focused search")
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            print(f"    Perplexity API Error: {resp.status_code}")
            return {"content": f"[perplexity error {resp.status_code}]", "citations": []}
        
        data = resp.json()
        content = ""
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception:
            content = json.dumps(data)[:2000]

        citations = []
        if "citations" in data and isinstance(data["citations"], list):
            citations = [c for c in data["citations"] if isinstance(c, str)]
        else:
            try:
                citations = data["choices"][0].get("citations") or []
            except Exception:
                citations = []

        if not citations:
            urls = re.findall(r"https?://[^\s\]\)]+", content)
            citations = urls

        # Normalize and dedupe
        norm = []
        seen = set()
        for u in citations:
            nu = normalize_url(u)
            if nu and nu not in seen and len(nu) > 15:
                seen.add(nu)
                norm.append(nu)

        return {"content": content, "citations": norm}
        
    except Exception as e:
        print(f"    Perplexity exception: {e}")
        return {"content": f"[perplexity exception: {e}]", "citations": []}

def openai_citations(prompt: str, api_key: str, model: str = "gpt-4o-mini", timeout: int = 30):
    """Enhanced ChatGPT adapter for holiday queries"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a holiday food and dining expert. When providing information, ALWAYS include citations with working URLs to reputable sources. Format each source as 'Source: https://...' on a new line. Focus on recent holiday content from 2024-2025 when possible."
                },
                {"role": "user", "content": f"{prompt}\n\nPlease provide detailed holiday information with at least 5-8 source citations formatted as 'Source: https://...'"}
            ]
        }
        
        print(f"    ChatGPT: Holiday expert with citations")
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if r.status_code != 200:
            print(f"    ChatGPT API Error: {r.status_code}")
            return {"content": f"[openai error {r.status_code}]", "citations": []}
            
        data = r.json()
        content = ""
        try:
            content = data["choices"][0]["message"]["content"] or ""
        except Exception:
            content = json.dumps(data)[:2000]
        
        # Extract URLs
        urls = []
        seen = set()
        
        source_urls = re.findall(r"Source:\s*(https?://[^\s\n\r]+)", content, re.IGNORECASE)
        urls.extend(source_urls)
        
        all_urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        urls.extend(all_urls)
        
        out = []
        for u in urls:
            nu = normalize_url(u)
            if nu and nu not in seen and len(nu) > 10:
                seen.add(nu)
                out.append(nu)
        
        return {"content": content, "citations": out}
        
    except Exception as e:
        print(f"    ChatGPT exception: {e}")
        return {"content": f"[openai exception: {e}]", "citations": []}

def anthropic_citations(prompt: str, api_key: str, model: str = "claude-3-5-sonnet-20241022", timeout: int = 35):
    """Enhanced Claude adapter for holiday queries"""
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "user-agent": "HoneyBaked-Holiday-GEO-Audit/1.0"
        }
        
        payload = {
            "model": model,
            "max_tokens": 1000,
            "temperature": 0.1,
            "system": "You are a holiday food and dining research assistant. When providing information, ALWAYS include citations with working URLs to reputable sources. Format each source as 'Reference: https://...' on a new line. Focus on recent holiday content from 2024-2025 when possible.",
            "messages": [{"role": "user", "content": f"{prompt}\n\nPlease provide detailed holiday information with at least 5-8 reference citations formatted as 'Reference: https://...'"}]
        }
        
        print(f"    Claude: Holiday research with references")
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if r.status_code != 200:
            print(f"    Claude API Error: {r.status_code}")
            return {"content": f"[anthropic error {r.status_code}]", "citations": []}
            
        data = r.json()
        content = ""
        try:
            blocks = data.get("content") or []
            texts = []
            for b in blocks:
                t = b.get("text")
                if isinstance(t, str):
                    texts.append(t)
            content = "\n\n".join(texts) if texts else json.dumps(data)[:2000]
        except Exception:
            content = json.dumps(data)[:2000]
        
        # Extract URLs
        urls = []
        seen = set()
        
        ref_urls = re.findall(r"Reference:\s*(https?://[^\s\n\r]+)", content, re.IGNORECASE)
        urls.extend(ref_urls)
        
        all_urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        urls.extend(all_urls)
        
        out = []
        for u in urls:
            nu = normalize_url(u)
            if nu and nu not in seen and len(nu) > 10:
                seen.add(nu)
                out.append(nu)
        
        return {"content": content, "citations": out}
        
    except Exception as e:
        print(f"    Claude exception: {e}")
        return {"content": f"[anthropic exception: {e}]", "citations": []}

def gemini_citations(prompt: str, api_key: str, model: str = "gemini-1.5-flash", timeout: int = 30):
    """Enhanced Gemini adapter for holiday queries"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        enhanced_prompt = f"""
{prompt}

Please provide detailed holiday information with citations. Format each source as 'URL: https://...' on a new line. 
Focus on recent holiday content from 2024-2025 when possible. Include at least 5-8 source URLs.
"""
        
        print(f"    Gemini: Holiday content with URLs")
        
        response = model_instance.generate_content(
            enhanced_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        content = response.text if response.text else ""
        
        # Extract URLs
        urls = []
        seen = set()
        
        url_formatted = re.findall(r"URL:\s*(https?://[^\s\n\r]+)", content, re.IGNORECASE)
        urls.extend(url_formatted)
        
        all_urls = re.findall(r"https?://[^\s\]\)\n\r]+", content)
        urls.extend(all_urls)
        
        out = []
        for u in urls:
            nu = normalize_url(u)
            if nu and nu not in seen and len(nu) > 10:
                seen.add(nu)
                out.append(nu)
        
        return {"content": content, "citations": out}
        
    except ImportError:
        print("    Gemini: google-generativeai library not installed")
        return {"content": "[gemini import error]", "citations": []}
    except Exception as e:
        print(f"    Gemini exception: {e}")
        return {"content": f"[gemini exception: {e}]", "citations": []}

def analyze_pr_media_targets(citations):
    """Analyze citations against PR target media list"""
    pr_target_hits = {}
    pr_target_contexts = {}
    
    for citation in citations:
        domain = domain_of(citation.get('url', ''))
        if domain in HOLIDAY_PR_TARGET_DOMAINS:
            media_name = HOLIDAY_PR_TARGET_DOMAINS[domain]
            if media_name not in pr_target_hits:
                pr_target_hits[media_name] = 0
                pr_target_contexts[media_name] = []
            
            pr_target_hits[media_name] += 1
            pr_target_contexts[media_name].append({
                'url': citation.get('url', ''),
                'query': citation.get('query', ''),
                'engine': citation.get('engine', '')
            })
    
    return pr_target_hits, pr_target_contexts

def analyze_chef_tim_ziga_mentions(answers):
    """Track Chef Tim Ziga authority mentions"""
    tim_ziga_mentions = []
    
    for answer in answers:
        content = answer.get('content', '').lower()
        if 'tim ziga' in content or 'chef tim' in content:
            tim_ziga_mentions.append({
                'engine': answer.get('engine', ''),
                'query': answer.get('prompt', ''),
                'content_snippet': answer.get('content', '')[:200] + '...',
                'citations': answer.get('citations', [])
            })
    
    return tim_ziga_mentions

def compute_holiday_geo_scores(brand: str, competitors, answers, query_categories):
    """Compute GEO-specific scores for holiday queries"""
    brand_l = brand.lower()
    comp_l = [c.lower() for c in competitors]
    
    # Query Coverage: % of holiday queries where HoneyBaked appears
    total_queries = len([a for a in answers])
    brand_appearances = 0
    
    query_performance = {}
    for category, queries in query_categories.items():
        if category == 'all_queries':
            continue
        query_performance[category] = {'total': 0, 'brand_present': 0}
    
    for answer in answers:
        query = answer.get('prompt', '')
        content = (answer.get('content') or '').lower()
        
        # Determine query category
        for category, queries in query_categories.items():
            if category == 'all_queries':
                continue
            if query in queries:
                query_performance[category]['total'] += 1
                if brand_l in content:
                    query_performance[category]['brand_present'] += 1
                break
        
        if brand_l in content:
            brand_appearances += 1
    
    query_coverage = 100.0 * brand_appearances / max(1, total_queries)
    
    # Position Quality: prominence in responses
    prominence_scores = []
    for answer in answers:
        content = answer.get('content', '')
        idx = content.lower().find(brand_l)
        if idx < 0:
            prominence_scores.append(0.0)
        else:
            L = max(50, len(content))
            prominence_scores.append(max(0.0, 100.0 * (1.0 - (idx / L))))
    
    position_quality = sum(prominence_scores) / max(1, len(prominence_scores))
    
    # Authority Citations: % from high-authority sources
    citation_weights = {
        "editorial_tier1": 1.0,
        "food_tier1": 1.0,
        "food_tier2": 0.8,
        "lifestyle_holiday": 0.9,
        "editorial": 0.7,
        "pr": 0.3,
        "other": 0.2
    }
    
    authority_scores = []
    for answer in answers:
        for url in answer.get('citations', []):
            domain = domain_of(url)
            classification = classify_domain_holiday(domain)
            authority_scores.append(citation_weights.get(classification, 0.2))
    
    authority_citations = 100.0 * (sum(authority_scores) / max(1, len(authority_scores)))
    
    # Competitive Share: brand vs competitors in same responses
    brand_mentions = sum(1 for a in answers if brand_l in (a.get('content') or '').lower())
    comp_mentions = sum(1 for a in answers if any(cl in (a.get('content') or '').lower() for cl in comp_l))
    
    if brand_mentions + comp_mentions == 0:
        competitive_share = 50.0
    else:
        competitive_share = 100.0 * brand_mentions / (brand_mentions + comp_mentions)
    
    # Natural Language Fit: conversational/quotable content (placeholder)
    natural_language_fit = 75.0  # Baseline score
    
    # Overall GEO Score
    weights = {
        'query_coverage': 0.25,
        'position_quality': 0.25, 
        'authority_citations': 0.30,
        'competitive_share': 0.10,
        'natural_language_fit': 0.10
    }
    
    overall_score = (
        weights['query_coverage'] * query_coverage +
        weights['position_quality'] * position_quality +
        weights['authority_citations'] * authority_citations +
        weights['competitive_share'] * competitive_share +
        weights['natural_language_fit'] * natural_language_fit
    )
    
    return {
        'overall_score': round(overall_score, 1),
        'query_coverage': round(query_coverage, 1),
        'position_quality': round(position_quality, 1),
        'authority_citations': round(authority_citations, 1),
        'competitive_share': round(competitive_share, 1),
        'natural_language_fit': round(natural_language_fit, 1),
        'query_performance': query_performance
    }

def generate_holiday_query_matrix(answers, query_categories):
    """Generate detailed query performance matrix"""
    matrix = []
    
    competitors_found = set()
    
    for answer in answers:
        query = answer.get('prompt', '')
        content = answer.get('content', '').lower()
        citations = answer.get('citations', [])
        engine = answer.get('engine', '')
        
        # Check for brand presence
        honeybaked_present = 'honeybaked' in content or 'honey baked' in content
        
        # Check for competitors
        query_competitors = []
        competitor_terms = ['omaha steaks', 'harry & david', 'williams sonoma', 'butterball', 'smithfield', 'dartagnan', 'costco', 'whole foods']
        for comp in competitor_terms:
            if comp in content:
                query_competitors.append(comp.title())
                competitors_found.add(comp.title())
        
        # Determine position/prominence
        if honeybaked_present:
            idx = content.find('honeybaked')
            if idx == -1:
                idx = content.find('honey baked')
            position = "High" if idx < 200 else "Medium" if idx < 500 else "Low"
        else:
            position = "Not Present"
        
        # Source quality
        high_quality_sources = 0
        for url in citations:
            domain = domain_of(url)
            classification = classify_domain_holiday(domain)
            if classification in ['editorial_tier1', 'food_tier1', 'lifestyle_holiday']:
                high_quality_sources += 1
        
        source_quality = "High" if high_quality_sources >= 2 else "Medium" if high_quality_sources >= 1 else "Low"
        
        matrix.append({
            'query': query,
            'engine': engine,
            'honeybaked_present': "Yes" if honeybaked_present else "No",
            'competitors_mentioned': ', '.join(query_competitors) if query_competitors else "None",
            'position_prominence': position,
            'source_quality': source_quality,
            'total_citations': len(citations)
        })
    
    return matrix, list(competitors_found)

def write_holiday_reports(brand, competitors, answers, scores, query_categories, pr_analysis, tim_ziga_mentions, query_matrix, timestamp):
    """Generate comprehensive holiday GEO reports"""
    
    # Create output directory
    output_dir = f"case_studies/honeybaked_ham/holiday_geo_audit"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Executive Summary Report (HTML)
    html_report = generate_executive_html_report(brand, competitors, answers, scores, pr_analysis, tim_ziga_mentions, timestamp)
    html_path = os.path.join(output_dir, f"GEO_AUDIT_RESULTS_{timestamp}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # 2. Holiday Query Matrix (CSV)
    matrix_path = os.path.join(output_dir, f"HOLIDAY_QUERY_MATRIX_{timestamp}.csv")
    with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
        if query_matrix:
            fieldnames = query_matrix[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(query_matrix)
    
    # 3. PR Media Tracking (CSV)
    pr_path = os.path.join(output_dir, f"PR_MEDIA_TRACKING_{timestamp}.csv")
    pr_hits, pr_contexts = pr_analysis
    with open(pr_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Media_Outlet', 'Citation_Count', 'URLs', 'Queries', 'Engines'])
        for media, count in pr_hits.items():
            contexts = pr_contexts[media]
            urls = [c['url'] for c in contexts]
            queries = [c['query'] for c in contexts]
            engines = [c['engine'] for c in contexts]
            writer.writerow([media, count, '; '.join(urls), '; '.join(queries), '; '.join(engines)])
    
    # 4. Raw Citations (CSV)
    citations_path = os.path.join(output_dir, f"RAW_CITATIONS_{timestamp}.csv")
    with open(citations_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Engine', 'Query', 'Domain', 'Classification', 'URL'])
        for answer in answers:
            engine = answer.get('engine', '')
            query = answer.get('prompt', '')
            for url in answer.get('citations', []):
                domain = domain_of(url)
                classification = classify_domain_holiday(domain)
                writer.writerow([engine, query, domain, classification, url])
    
    # 5. Strategic Recommendations (Markdown)
    recommendations = generate_strategic_recommendations(scores, pr_analysis, tim_ziga_mentions, query_matrix)
    rec_path = os.path.join(output_dir, f"STRATEGIC_RECOMMENDATIONS_{timestamp}.md")
    with open(rec_path, 'w', encoding='utf-8') as f:
        f.write(recommendations)
    
    return {
        'html_report': html_path,
        'query_matrix': matrix_path,
        'pr_tracking': pr_path,
        'raw_citations': citations_path,
        'recommendations': rec_path
    }

def generate_executive_html_report(brand, competitors, answers, scores, pr_analysis, tim_ziga_mentions, timestamp):
    """Generate executive HTML report"""
    
    pr_hits, pr_contexts = pr_analysis
    total_citations = sum(len(a.get('citations', [])) for a in answers)
    total_queries = len(set(a.get('prompt', '') for a in answers))
    
    # Engine breakdown
    engine_stats = {}
    for answer in answers:
        engine = answer.get('engine', 'unknown')
        if engine not in engine_stats:
            engine_stats[engine] = {'queries': 0, 'citations': 0}
        engine_stats[engine]['queries'] += 1
        engine_stats[engine]['citations'] += len(answer.get('citations', []))
    
    # Top competitors by mentions
    competitor_mentions = {}
    for answer in answers:
        content = answer.get('content', '').lower()
        for comp in competitors:
            if comp.lower() in content:
                competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
    
    top_competitors = sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HoneyBaked Ham Holiday GEO PR Strategy Audit</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; color: #222; padding: 24px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); color: white; padding: 32px; border-radius: 12px; margin-bottom: 32px; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 700; }}
        .header .subtitle {{ font-size: 1.2em; opacity: 0.9; margin-top: 8px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 32px 0; }}
        .metric-card {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #8B4513; margin-bottom: 8px; }}
        .metric-label {{ font-size: 0.9em; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}
        .section {{ background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 24px; margin: 24px 0; }}
        .section h2 {{ margin-top: 0; color: #8B4513; border-bottom: 2px solid #8B4513; padding-bottom: 8px; }}
        .score-breakdown {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; }}
        .score-item {{ text-align: center; padding: 16px; background: #f8f9fa; border-radius: 6px; }}
        .score-item .score {{ font-size: 1.8em; font-weight: bold; color: #8B4513; }}
        .score-item .label {{ font-size: 0.85em; color: #666; margin-top: 4px; }}
        .pr-targets {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }}
        .pr-target {{ background: #f8f9fa; padding: 16px; border-radius: 6px; border-left: 4px solid #8B4513; }}
        .competitive-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
        .competitor {{ background: #fff3cd; padding: 16px; border-radius: 6px; border: 1px solid #ffeaa7; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e9ecef; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .status-yes {{ color: #28a745; font-weight: bold; }}
        .status-no {{ color: #dc3545; font-weight: bold; }}
        .recommendations {{ background: #e8f5e8; border: 1px solid #c3e6c3; border-radius: 8px; padding: 24px; }}
        .recommendations h3 {{ color: #155724; margin-top: 0; }}
        .recommendations ul {{ margin: 0; }}
        .recommendations li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>HoneyBaked Ham Holiday GEO PR Strategy Audit</h1>
        <div class="subtitle">Comprehensive AI Citation Analysis • {timestamp}</div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{scores.get('overall_score', 0)}</div>
            <div class="metric-label">Overall GEO Score</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_citations}</div>
            <div class="metric-label">Total Citations</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(pr_hits)}</div>
            <div class="metric-label">PR Target Media</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(tim_ziga_mentions)}</div>
            <div class="metric-label">Chef Tim Ziga Mentions</div>
        </div>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Brand:</strong> {html_escape(brand)}</p>
        <p><strong>Competitors Tracked:</strong> {html_escape(', '.join(competitors))}</p>
        <p><strong>Holiday Queries Tested:</strong> {total_queries}</p>
        <p><strong>AI Engines:</strong> {', '.join(engine_stats.keys())}</p>
        
        <div class="score-breakdown">
            <div class="score-item">
                <div class="score">{scores.get('query_coverage', 0)}%</div>
                <div class="label">Query Coverage</div>
            </div>
            <div class="score-item">
                <div class="score">{scores.get('position_quality', 0)}%</div>
                <div class="label">Position Quality</div>
            </div>
            <div class="score-item">
                <div class="score">{scores.get('authority_citations', 0)}%</div>
                <div class="label">Authority Citations</div>
            </div>
            <div class="score-item">
                <div class="score">{scores.get('competitive_share', 0)}%</div>
                <div class="label">Competitive Share</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>PR Media Target Achievement</h2>
        <div class="pr-targets">
"""
    
    # Add PR target results
    for media, count in pr_hits.items():
        html += f"""
            <div class="pr-target">
                <h4>{html_escape(media)}</h4>
                <p><strong>{count}</strong> citations found</p>
            </div>
"""
    
    if not pr_hits:
        html += """
            <div class="pr-target">
                <h4>No PR Target Media Found</h4>
                <p>None of the priority media targets appeared in AI responses</p>
            </div>
"""
    
    html += """
        </div>
    </div>

    <div class="section">
        <h2>Competitive Holiday Analysis</h2>
        <div class="competitive-grid">
"""
    
    # Add competitor analysis
    for comp, mentions in top_competitors:
        html += f"""
            <div class="competitor">
                <h4>{html_escape(comp)}</h4>
                <p><strong>{mentions}</strong> mentions across queries</p>
            </div>
"""
    
    html += """
        </div>
    </div>

    <div class="section">
        <h2>Chef Tim Ziga Authority Presence</h2>
"""
    
    if tim_ziga_mentions:
        html += f"""
        <p><strong>{len(tim_ziga_mentions)}</strong> mentions found across AI responses:</p>
        <ul>
"""
        for mention in tim_ziga_mentions:
            html += f"""
            <li><strong>{html_escape(mention['engine'])}:</strong> {html_escape(mention['content_snippet'])}</li>
"""
        html += """
        </ul>
"""
    else:
        html += """
        <p>No mentions of Chef Tim Ziga found in AI responses. This represents an opportunity to enhance authority positioning.</p>
"""
    
    html += """
    </div>

    <div class="recommendations">
        <h3>Strategic Recommendations</h3>
        <ul>
            <li><strong>Priority Media Outreach:</strong> Target missing PR media outlets that frequently appear in holiday food queries</li>
            <li><strong>Chef Tim Ziga Authority:</strong> Amplify expert positioning through thought leadership content</li>
            <li><strong>Holiday Query Optimization:</strong> Create content specifically targeting high-volume holiday queries</li>
            <li><strong>Competitive Differentiation:</strong> Develop messaging that distinguishes from mass-market competitors</li>
            <li><strong>Gift Category Positioning:</strong> Enhance presence in holiday gift and convenience queries</li>
        </ul>
    </div>

</body>
</html>"""
    
    return html

def generate_strategic_recommendations(scores, pr_analysis, tim_ziga_mentions, query_matrix):
    """Generate strategic recommendations based on audit findings"""
    
    pr_hits, pr_contexts = pr_analysis
    
    recommendations = f"""# HoneyBaked Ham Holiday GEO Strategy Recommendations

## Executive Summary
Based on the comprehensive holiday GEO audit, the following strategic recommendations are prioritized by impact and feasibility.

## Overall Performance
- **GEO Score:** {scores.get('overall_score', 0)}/100
- **Query Coverage:** {scores.get('query_coverage', 0)}%
- **Authority Citations:** {scores.get('authority_citations', 0)}%
- **PR Target Achievement:** {len(pr_hits)} of 11 target media outlets

## High Priority Recommendations (30 Days)

### 1. PR Media Target Outreach
**Missing Target Media:**
"""
    
    # List missing PR targets
    all_targets = set(HOLIDAY_PR_TARGET_DOMAINS.values())
    found_targets = set(pr_hits.keys())
    missing_targets = all_targets - found_targets
    
    for target in sorted(missing_targets):
        recommendations += f"- {target}\n"
    
    recommendations += f"""

**Strategy:** Develop holiday-specific story angles for these outlets focusing on:
- Holiday meal solutions and convenience
- Premium quality differentiation
- Gift category positioning
- Chef Tim Ziga expertise

### 2. Chef Tim Ziga Authority Enhancement
**Current Status:** {len(tim_ziga_mentions)} mentions found
**Opportunity:** Amplify expert positioning through:
- Holiday cooking tips and techniques
- Ham preparation expertise content
- Media interviews and quotes
- Thought leadership articles

### 3. Holiday Query Optimization
**Coverage Gaps Identified:**
"""
    
    # Analyze query performance
    low_performance_queries = []
    for item in query_matrix:
        if item['honeybaked_present'] == 'No':
            low_performance_queries.append(item['query'])
    
    for query in low_performance_queries[:5]:  # Top 5 gaps
        recommendations += f"- {query}\n"
    
    recommendations += f"""

## Medium Priority Recommendations (60-90 Days)

### 4. Competitive Differentiation Strategy
**Key Competitors to Address:**
"""
    
    # Add competitor analysis
    competitor_mentions = {}
    for item in query_matrix:
        if item['competitors_mentioned'] != 'None':
            comps = item['competitors_mentioned'].split(', ')
            for comp in comps:
                competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
    
    top_competitors = sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    for comp, count in top_competitors:
        recommendations += f"- {comp} ({count} mentions)\n"
    
    recommendations += f"""

**Strategy:** Develop content that highlights HoneyBaked's unique advantages:
- Spiral-cut innovation and heritage
- Premium quality vs. mass market
- Convenience and reliability
- Holiday tradition positioning

### 5. Content Gap Analysis
**Underperforming Query Categories:**
"""
    
    # Analyze query performance by category
    query_performance = scores.get('query_performance', {})
    for category, performance in query_performance.items():
        if performance['total'] > 0:
            coverage_rate = (performance['brand_present'] / performance['total']) * 100
            if coverage_rate < 50:
                recommendations += f"- {category.replace('_', ' ').title()}: {coverage_rate:.1f}% coverage\n"
    
    recommendations += f"""

## Long-term Strategic Initiatives (6+ Months)

### 6. Year-Round Relevance Building
- Expand beyond holiday seasonality
- B2B catering and corporate market content
- Everyday occasion positioning
- Regional expansion story amplification

### 7. Digital Authority Enhancement
- SEO-optimized content for holiday queries
- Social media thought leadership
- Influencer partnerships in food space
- Recipe and cooking content development

## Success Metrics to Track

### Monthly KPIs
- PR target media citation count
- Chef Tim Ziga mention frequency
- Holiday query coverage percentage
- Competitive share in AI responses

### Quarterly Goals
- Achieve 70+ overall GEO score
- Secure 5+ PR target media placements
- Increase query coverage to 60%+
- Establish thought leadership positioning

## Implementation Timeline

**Week 1-2:** PR media outreach campaign launch
**Week 3-4:** Chef Tim Ziga content development
**Month 2:** Holiday query optimization content
**Month 3:** Competitive differentiation messaging
**Quarter 2:** Long-term authority building initiatives

## Budget Considerations
- PR agency retainer for media outreach
- Content creation for query optimization
- Thought leadership development
- Ongoing monitoring and optimization

---

*Generated from Holiday GEO Audit Results*
*Recommendations based on objective data analysis*
"""
    
    return recommendations

def main():
    """Main execution function for HoneyBaked Ham Holiday GEO Audit"""
    
    print("🎄 HoneyBaked Ham Holiday GEO PR Strategy Audit")
    print("=" * 60)
    
    # Configuration
    brand = "HoneyBaked Ham"
    competitors = [
        "Omaha Steaks", "Harry & David", "Williams Sonoma", 
        "Butterball", "Smithfield Foods", "D'Artagnan", 
        "Costco", "Whole Foods"
    ]
    
    # Get API keys
    pplx_key = os.environ.get("PERPLEXITY_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if not pplx_key:
        print("❌ ERROR: PERPLEXITY_API_KEY not set in environment.")
        sys.exit(1)
    
    # Build holiday query set
    print("\n📋 Building holiday-focused query set...")
    query_categories = build_holiday_query_set()
    all_queries = query_categories['all_queries']
    print(f"✅ Generated {len(all_queries)} holiday queries across 4 categories")
    
    # Run 4-engine audit
    print(f"\n🔍 Running 4-engine audit across {len(all_queries)} queries...")
    print(f"Engines available:")
    print(f"  - Perplexity: {'✓' if pplx_key else '✗'}")
    print(f"  - ChatGPT: {'✓' if openai_key else '✗'}")
    print(f"  - Claude: {'✓' if anthropic_key else '✗'}")
    print(f"  - Gemini: {'✓' if gemini_key else '✗'}")
    
    answers = []
    
    for i, query in enumerate(all_queries):
        print(f"\n🔎 Processing query {i+1}/{len(all_queries)}: {query[:50]}...")
        
        # Perplexity
        if pplx_key:
            result = perplexity_chat(query, pplx_key)
            answers.append({
                "engine": "perplexity",
                "prompt": query,
                "content": result.get("content", ""),
                "citations": result.get("citations", [])
            })
            time.sleep(1.0)
        
        # ChatGPT
        if openai_key:
            result = openai_citations(query, openai_key)
            answers.append({
                "engine": "chatgpt", 
                "prompt": query,
                "content": result.get("content", ""),
                "citations": result.get("citations", [])
            })
            time.sleep(1.0)
        
        # Claude
        if anthropic_key:
            result = anthropic_citations(query, anthropic_key)
            answers.append({
                "engine": "claude",
                "prompt": query, 
                "content": result.get("content", ""),
                "citations": result.get("citations", [])
            })
            time.sleep(1.0)
        
        # Gemini (limited to first 4 queries due to rate limits)
        if gemini_key and i < 4:
            result = gemini_citations(query, gemini_key)
            answers.append({
                "engine": "gemini",
                "prompt": query,
                "content": result.get("content", ""),
                "citations": result.get("citations", [])
            })
            time.sleep(4.0)  # Gemini rate limiting
    
    print(f"\n✅ Audit complete! Collected {len(answers)} responses")
    
    # Process citations for PR media analysis
    print("\n📊 Analyzing PR media targets...")
    citation_data = []
    for answer in answers:
        for url in answer.get('citations', []):
            citation_data.append({
                'url': url,
                'query': answer.get('prompt', ''),
                'engine': answer.get('engine', '')
            })
    
    pr_analysis = analyze_pr_media_targets(citation_data)
    pr_hits, pr_contexts = pr_analysis
    
    # Analyze Chef Tim Ziga mentions
    print("👨‍🍳 Tracking Chef Tim Ziga authority mentions...")
    tim_ziga_mentions = analyze_chef_tim_ziga_mentions(answers)
    
    # Compute GEO scores
    print("🎯 Computing GEO performance metrics...")
    scores = compute_holiday_geo_scores(brand, competitors, answers, query_categories)
    
    # Generate query performance matrix
    print("📈 Generating holiday query matrix...")
    query_matrix, competitors_found = generate_holiday_query_matrix(answers, query_categories)
    
    # Generate reports
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    print(f"\n📄 Generating comprehensive reports...")
    
    report_paths = write_holiday_reports(
        brand, competitors, answers, scores, query_categories,
        pr_analysis, tim_ziga_mentions, query_matrix, timestamp
    )
    
    # Console output summary
    print("\n" + "="*60)
    print("🎄 HONEYBAKED HAM HOLIDAY GEO AUDIT RESULTS")
    print("="*60)
    
    total_citations = sum(len(a.get('citations', [])) for a in answers)
    print(f"📊 Total Citations: {total_citations}")
    print(f"🎯 Overall GEO Score: {scores.get('overall_score', 0)}/100")
    print(f"📺 PR Target Media Found: {len(pr_hits)}/11")
    print(f"👨‍🍳 Chef Tim Ziga Mentions: {len(tim_ziga_mentions)}")
    
    print(f"\n🏆 Top 3 Competitors by Mentions:")
    competitor_mentions = {}
    for answer in answers:
        content = answer.get('content', '').lower()
        for comp in competitors:
            if comp.lower() in content:
                competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
    
    top_competitors = sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (comp, count) in enumerate(top_competitors, 1):
        print(f"  {i}. {comp}: {count} mentions")
    
    print(f"\n📁 Reports Generated:")
    for report_type, path in report_paths.items():
        print(f"  - {report_type}: {path}")
    
    print(f"\n✅ Holiday GEO audit complete!")
    print(f"📈 Next steps: Review strategic recommendations in {report_paths['recommendations']}")

if __name__ == "__main__":
    main()

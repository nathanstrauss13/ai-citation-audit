#!/usr/bin/env python3
"""
Citation Explorer Engine — Transit Map Visualization.

Generates an interactive, self-contained HTML page that visualizes citation
data as a subway/transit-map-style tree. Users drill from high-level categories
(persona → intent → prompt → platform → presence → citation type → domain → URL)
down to individual citation URLs.

Design direction: colorful branching lines on a dark background with 90° bends,
inspired by transit system maps. Each hierarchy level has a distinct line color.

Usage:
    from engines.citation_tree_engine import CitationTreeEngine
    html = CitationTreeEngine().generate(rows, "Lululemon")
"""

import json
import logging
import os
import re
from collections import Counter, OrderedDict
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# ── Domain classification heuristics (lightweight, no LLM needed) ─────────

EDITORIAL_DOMAINS = {
    'forbes.com', 'nytimes.com', 'wsj.com', 'bloomberg.com', 'reuters.com',
    'cnn.com', 'bbc.com', 'bbc.co.uk', 'theguardian.com', 'washingtonpost.com',
    'usatoday.com', 'techcrunch.com', 'wired.com', 'theverge.com', 'arstechnica.com',
    'engadget.com', 'zdnet.com', 'cnet.com', 'mashable.com', 'businessinsider.com',
    'insider.com', 'vox.com', 'vice.com', 'buzzfeed.com', 'huffpost.com',
    'cnbc.com', 'fortune.com', 'fastcompany.com', 'inc.com', 'entrepreneur.com',
    'gq.com', 'vogue.com', 'elle.com', 'harpersbazaar.com', 'cosmopolitan.com',
    'glamour.com', 'allure.com', 'instyle.com', 'people.com', 'rollingstone.com',
    'variety.com', 'hollywoodreporter.com', 'deadline.com', 'vulture.com',
    'esquire.com', 'vanityfair.com', 'newyorker.com', 'theatlantic.com',
    'slate.com', 'salon.com', 'politico.com', 'time.com', 'newsweek.com',
    'npr.org', 'apnews.com', 'latimes.com', 'chicagotribune.com',
    'nypost.com', 'foxnews.com', 'msnbc.com', 'abc.com', 'nbcnews.com',
    'cbsnews.com', 'axios.com', 'thehill.com', 'thedailybeast.com',
    'buzzfeednews.com', 'propublica.org', 'theintercept.com',
}

SOCIAL_DOMAINS = {
    'reddit.com', 'twitter.com', 'x.com', 'youtube.com', 'instagram.com',
    'facebook.com', 'tiktok.com', 'linkedin.com', 'pinterest.com',
    'quora.com', 'medium.com', 'tumblr.com', 'threads.net',
}

RETAIL_DOMAINS = {
    'amazon.com', 'walmart.com', 'target.com', 'ebay.com', 'etsy.com',
    'bestbuy.com', 'costco.com', 'nordstrom.com', 'macys.com',
    'sephora.com', 'ulta.com', 'wayfair.com', 'zappos.com',
    'rei.com', 'dickssportinggoods.com', 'kohls.com',
    'shop.lululemon.com', 'nike.com', 'adidas.com',
    'bloomingdales.com', 'saksfifthavenue.com', 'neimanmarcus.com',
}

REFERENCE_DOMAINS = {
    'wikipedia.org', 'en.wikipedia.org', 'wikihow.com', 'britannica.com',
    'merriam-webster.com', 'dictionary.com', 'investopedia.com',
    'healthline.com', 'webmd.com', 'mayoclinic.org', 'nih.gov',
    'cdc.gov', 'fda.gov', 'epa.gov', 'nasa.gov',
}

REVIEW_DOMAINS = {
    'yelp.com', 'tripadvisor.com', 'g2.com', 'trustpilot.com',
    'glassdoor.com', 'consumerreports.org', 'pcmag.com',
    'tomsguide.com', 'wirecutter.com', 'thespruce.com',
    'goodhousekeeping.com', 'runnersworld.com', 'outsideonline.com',
}


def _extract_domain(url: str) -> str:
    try:
        d = urlparse(url).netloc.replace('www.', '').lower()
        return d if d else url.lower().replace('www.', '').split('/')[0]
    except Exception:
        return url.lower()


def _classify_domain(domain: str) -> str:
    d = domain.lower().replace('www.', '')
    if d in EDITORIAL_DOMAINS:
        return 'Editorial'
    if d in SOCIAL_DOMAINS:
        return 'Social'
    if d in RETAIL_DOMAINS:
        return 'Retail'
    if d in REFERENCE_DOMAINS:
        return 'Reference'
    if d in REVIEW_DOMAINS:
        return 'Review'
    if d.endswith('.gov'):
        return 'Government'
    if d.endswith('.edu'):
        return 'Academic'
    if d.endswith('.org'):
        return 'Non-Profit'
    # Heuristics
    if any(k in d for k in ['blog', 'wordpress', 'substack', 'ghost']):
        return 'Blog'
    if any(k in d for k in ['news', 'times', 'post', 'herald', 'tribune', 'journal', 'gazette']):
        return 'Editorial'
    if any(k in d for k in ['shop', 'store', 'buy', 'market']):
        return 'Retail'
    return 'Other'


def _detect_presence(full_output: str, brand_name: str) -> str:
    """Determine brand presence level from response text."""
    if not full_output or not brand_name:
        return 'Unknown'
    text = full_output.lower()
    brand = brand_name.lower()
    if brand not in text:
        return 'Absent'
    # Check if featured/recommended prominently
    featured_patterns = [
        rf'(?:recommend|top pick|best overall|#\s*1|number one|first choice).*{re.escape(brand)}',
        rf'{re.escape(brand)}.*(?:recommend|top pick|best overall|#\s*1|number one|first choice)',
        rf'(?:^|\n)\s*(?:1\.|1\)|\*\*1)\s*.*{re.escape(brand)}',
    ]
    for pat in featured_patterns:
        if re.search(pat, text):
            return 'Featured'
    # Check position in lists
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if brand in line.lower():
            # Check if it's in a numbered list
            num_match = re.match(r'\s*(\d+)[.\)]\s', line)
            if num_match:
                pos = int(num_match.group(1))
                if pos <= 2:
                    return 'Featured'
                return 'Mentioned'
    return 'Mentioned'


class CitationTreeEngine:
    """Generates interactive transit-map Citation Explorer HTML."""

    # Level colors — subway line palette
    LEVEL_COLORS = {
        'persona':  '#00BCD4',  # Cyan
        'intent':   '#E91E63',  # Magenta
        'prompt':   '#FFC107',  # Yellow/Amber
        'platform': '#4CAF50',  # Green
        'presence': '#FF9800',  # Orange (dynamic: orange=featured, red=absent)
        'response': '#E0E0E0',  # Light gray — full output / AI response
        'type':     '#2196F3',  # Blue
        'domain':   '#9C27B0',  # Purple
        'url':      '#FFFFFF',  # White
    }

    PRESENCE_COLORS = {
        'Featured': '#FF9800',
        'Mentioned': '#FFC107',
        'Absent': '#F44336',
        'Unknown': '#666666',
    }

    def generate(self, rows: List[Dict], brand_name: str,
                 has_persona: bool = False,
                 competitors: Optional[List[str]] = None) -> str:
        """Generate standalone Citation Explorer HTML.

        Produces a horizontal column-based tree (macOS Finder style) with
        transit-map colored lines flowing left (trunk) → right (leaves).
        Lines get thinner as you approach URL leaf nodes.

        Args:
            rows: Parsed CSV rows (list of dicts). Expected keys:
                  query_id, query, category, engine, full_output,
                  citation_urls, citation_domains, and optionally
                  persona, intent
            brand_name: Brand name for title and presence detection
            has_persona: Whether persona/intent columns should be used
            competitors: Optional list of competitor brand names

        Returns:
            Complete self-contained HTML string
        """
        # Pre-classify all domains using adaptive classifier (rule-based + Claude)
        domain_map = self._classify_all_domains(rows, brand_name, competitors)
        tree = self._build_tree(rows, brand_name, has_persona, domain_map)
        tree_json = json.dumps(tree, indent=None, ensure_ascii=False)

        levels_json = json.dumps(
            list(self.LEVEL_COLORS.keys()) if has_persona
            else [k for k in self.LEVEL_COLORS.keys() if k not in ('persona', 'intent')]
        )
        colors_json = json.dumps(self.LEVEL_COLORS)
        presence_colors_json = json.dumps(self.PRESENCE_COLORS)

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} Citation Explorer</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
{self._get_styles()}
    </style>
</head>
<body>
    <div class="explorer-header">
        <div class="header-left">
            <h1 class="header-title">Citation Explorer</h1>
            <span class="header-brand">{brand_name}</span>
        </div>
        <div class="header-right">
            <div class="legend" id="legend"></div>
        </div>
    </div>

    <div class="breadcrumb-bar" id="breadcrumb">
        <span class="crumb crumb-root crumb-active" data-depth="-1" onclick="navigateToDepth(-1)">&#x25C0; {brand_name}</span>
    </div>

    <div class="explorer-canvas" id="canvas">
        <div class="columns-viewport" id="columns-viewport">
            <!-- Columns render here left-to-right -->
        </div>
    </div>

    <div class="zoom-controls">
        <button class="zoom-btn" onclick="zoomIn()" title="Zoom in">+</button>
        <button class="zoom-btn" onclick="zoomOut()" title="Zoom out">&minus;</button>
        <button class="zoom-btn zoom-fit" onclick="fitView()" title="Fit to view">&#x2922;</button>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
    // ── Embedded Data ──
    const treeData = {tree_json};
    const brandName = {json.dumps(brand_name)};
    const levelOrder = {levels_json};
    const levelColors = {colors_json};
    const presenceColors = {presence_colors_json};
    const hasPersona = {json.dumps(has_persona)};

{self._get_scripts()}
    </script>
</body>
</html>'''

    def _classify_all_domains(
        self,
        rows: List[Dict],
        brand_name: str,
        competitors: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Pre-classify all citation domains using adaptive classifier.

        Collects every unique domain from the CSV, runs them through the
        2-phase classifier (rule-based → Claude LLM), and returns a
        domain→category lookup map.

        Falls back to the simple heuristic classifier if the adaptive
        classifier is unavailable.
        """
        # Collect all unique domains with counts
        domain_counter: Counter = Counter()
        for row in rows:
            urls_raw = row.get('citation_urls', '') or ''
            if '|' in urls_raw:
                urls = [u.strip() for u in urls_raw.split('|') if u.strip()]
            else:
                urls = [u.strip() for u in urls_raw.split('\n') if u.strip()]
            for url in urls:
                domain = _extract_domain(url)
                if domain:
                    domain_counter[domain] += 1

        domain_counts = [(d, c) for d, c in domain_counter.most_common()]

        if not domain_counts:
            return {}

        # Try the adaptive classifier (imports citation_classifier)
        domain_map: Dict[str, str] = {}
        try:
            from engines.citation_classifier import classify_citations_adaptive

            api_key = os.environ.get('ANTHROPIC_API_KEY')
            classified = classify_citations_adaptive(
                domain_counts=domain_counts,
                brand_name=brand_name,
                competitor_names=competitors,
                api_key=api_key,
            )

            # Build domain→category lookup
            for category, entries in classified.items():
                for entry in entries:
                    domain_map[entry['domain'].lower()] = category

            total_classified = len(domain_map)
            total_domains = len(domain_counts)
            logger.info(
                f"Adaptive classifier: {total_classified}/{total_domains} domains "
                f"classified into {len(classified)} categories"
            )

        except ImportError:
            logger.info("citation_classifier not available — using simple heuristics")
        except Exception as e:
            logger.warning(f"Adaptive classification failed: {e} — using simple heuristics")

        # Fill in any unclassified domains with simple heuristics
        for domain, _ in domain_counts:
            if domain.lower() not in domain_map:
                domain_map[domain.lower()] = _classify_domain(domain)

        return domain_map

    def _build_tree(self, rows: List[Dict], brand_name: str,
                    has_persona: bool, domain_map: Optional[Dict[str, str]] = None) -> Dict:
        """Build nested tree structure from CSV rows.

        Returns a dict with the structure:
        {{
            "name": "Brand",
            "type": "root",
            "children": [
                {{
                    "name": "Prompt text",
                    "type": "prompt",
                    "id": "Q001",
                    "count": 47,
                    "children": [
                        {{
                            "name": "ChatGPT",
                            "type": "platform",
                            "count": 8,
                            "children": [...]
                        }}
                    ]
                }}
            ]
        }}
        """
        # Group by hierarchy
        # Level 1: persona (optional) → Level 2: intent (optional) →
        # Level 3: prompt → Level 4: platform → Level 5: presence →
        # Level 6: citation type → Level 7: domain → Level 8: url

        tree = {
            'name': brand_name,
            'type': 'root',
            'children': [],
            'count': 0,
        }

        # Index rows by prompt + platform
        prompt_platform = {}
        for row in rows:
            query = row.get('query', '').strip()
            engine = row.get('engine', '').strip()
            if not query or not engine:
                continue

            key = (
                row.get('persona', '').strip() if has_persona else '',
                row.get('intent', '').strip() if has_persona else '',
                query,
                engine,
            )

            urls_raw = row.get('citation_urls', '') or ''
            # Support both pipe-separated (legacy) and newline-separated URLs
            if '|' in urls_raw:
                urls = [u.strip() for u in urls_raw.split('|') if u.strip()]
            else:
                urls = [u.strip() for u in urls_raw.split('\n') if u.strip()]

            full_output = row.get('full_output', '') or ''
            presence = _detect_presence(full_output, brand_name)
            category = row.get('category', 'General')
            raw_qid = row.get('query_id', '') or row.get('id', '')
            # Strip platform suffix if present (e.g., "Q001-chatgpt" → "Q001")
            query_id = re.sub(r'-(?:chatgpt|claude|perplexity|gemini|grok|meta_llama|deepseek|copilot|google_ai_studio|youcom)$', '', raw_qid, flags=re.IGNORECASE)

            prompt_platform[key] = {
                'urls': urls,
                'presence': presence,
                'category': category,
                'query_id': query_id,
                'query_type': row.get('query_type', 'unbranded'),
                'full_output': full_output,
            }

        # Build nested structure
        def _ensure_child(parent, name, node_type, **extra):
            """Find or create a child node."""
            for child in parent['children']:
                if child['name'] == name and child['type'] == node_type:
                    return child
            node = {'name': name, 'type': node_type, 'children': [], 'count': 0, **extra}
            parent['children'].append(node)
            return node

        total_urls = 0
        for key, data in prompt_platform.items():
            persona, intent, query, engine = key
            urls = data['urls']
            presence = data['presence']

            # Navigate/create hierarchy
            current = tree

            if has_persona and persona:
                current = _ensure_child(current, persona, 'persona')

            if has_persona and intent:
                current = _ensure_child(current, intent, 'intent')

            prompt_node = _ensure_child(
                current, query, 'prompt',
                query_id=data['query_id'],
                category=data['category'],
                query_type=data['query_type'],
            )

            platform_node = _ensure_child(prompt_node, engine, 'platform')

            presence_node = _ensure_child(platform_node, presence, 'presence')

            # Insert response node between presence and types
            # One response node per presence status (carries the full_output)
            response_label = f'{engine} Response'
            response_node = _ensure_child(presence_node, response_label, 'response')
            if data.get('full_output'):
                response_node['full_output'] = data['full_output']

            # Group URLs by type → domain
            for url in urls:
                domain = _extract_domain(url)
                ctype = (domain_map or {}).get(domain.lower()) or _classify_domain(domain)

                type_node = _ensure_child(response_node, ctype, 'type')
                domain_node = _ensure_child(type_node, domain, 'domain')

                # Add URL as leaf
                url_exists = any(
                    c['name'] == url for c in domain_node['children']
                )
                if not url_exists:
                    domain_node['children'].append({
                        'name': url,
                        'type': 'url',
                        'children': [],
                        'count': 1,
                    })
                    total_urls += 1

        # Propagate counts bottom-up
        def _count(node):
            if node['type'] == 'url':
                node['count'] = 1
                return 1
            total = 0
            for child in node['children']:
                total += _count(child)
            node['count'] = total
            return total

        _count(tree)

        # Sort children at each level by count (descending)
        def _sort(node):
            if node['children']:
                node['children'].sort(key=lambda x: x['count'], reverse=True)
                for child in node['children']:
                    _sort(child)

        _sort(tree)

        return tree

    def _get_styles(self) -> str:
        return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: #000;
            color: #eee;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            user-select: none;
        }

        /* ── Header ── */
        .explorer-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 64px;
            background: #0a0a0a;
            border-bottom: 1px solid #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 100;
        }
        .header-left { display: flex; align-items: baseline; gap: 12px; }
        .header-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
            letter-spacing: -0.02em;
        }
        .header-brand {
            font-size: 14px;
            font-weight: 400;
            color: #666;
            padding-left: 12px;
            border-left: 1px solid #333;
        }
        .header-right { display: flex; align-items: center; }
        .legend {
            display: flex;
            gap: 16px;
            font-size: 11px;
            color: #888;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .legend-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        /* ── Breadcrumb ── */
        .breadcrumb-bar {
            position: fixed;
            top: 64px;
            left: 0;
            right: 0;
            height: 44px;
            background: #0d0d0d;
            border-bottom: 1px solid #1a1a1a;
            display: flex;
            align-items: center;
            padding: 0 24px;
            gap: 4px;
            z-index: 99;
            overflow-x: auto;
        }
        .crumb {
            font-size: 12px;
            font-weight: 400;
            color: #888;
            cursor: pointer;
            padding: 4px 10px;
            border-radius: 12px;
            background: #1a1a1a;
            white-space: nowrap;
            transition: all 0.2s;
            max-width: 320px;
            overflow: hidden;
            text-overflow: ellipsis;
            flex-shrink: 1;
            min-width: 48px;
        }
        .crumb:hover { background: #252525; color: #fff; }
        .crumb-active {
            background: #222;
            color: #fff;
            font-weight: 500;
        }
        .crumb-separator {
            color: #444;
            font-size: 11px;
            user-select: none;
            flex-shrink: 0;
        }

        /* ── Canvas: horizontal columns ── */
        .explorer-canvas {
            position: fixed;
            top: 108px;
            left: 0;
            right: 0;
            bottom: 0;
            overflow-x: auto;
            overflow-y: hidden;
            background:
                radial-gradient(circle at 10% 50%, rgba(0,188,212,0.04) 0%, transparent 40%),
                radial-gradient(circle at 90% 50%, rgba(156,39,176,0.04) 0%, transparent 40%),
                #000;
        }

        .columns-viewport {
            display: flex;
            height: 100%;
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: 0 0;
        }

        /* ── Column ── */
        .tree-column {
            flex-shrink: 0;
            width: 280px;
            height: 100%;
            border-right: 1px solid #111;
            display: flex;
            flex-direction: column;
            position: relative;
            animation: columnSlideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        @keyframes columnSlideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .tree-column-wide { width: 360px; }

        .column-header {
            padding: 12px 16px 8px;
            border-bottom: 1px solid #1a1a1a;
            flex-shrink: 0;
        }
        .column-type-label {
            font-size: 10px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--col-color, #666);
        }
        .column-count {
            font-size: 10px;
            color: #555;
            margin-left: 6px;
        }

        .column-items {
            flex: 1;
            overflow-y: auto;
            padding: 4px 0;
        }

        /* ── Column item (a node) ── */
        .col-item {
            display: flex;
            align-items: center;
            padding: 8px 16px;
            cursor: pointer;
            transition: all 0.15s;
            position: relative;
            gap: 10px;
            border-left: 3px solid transparent;
        }
        .col-item:hover {
            background: #111;
        }
        .col-item-selected {
            background: #141414;
            border-left-color: var(--col-color, #555);
        }
        .col-item-selected::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--col-color, #555);
        }

        /* Transit line dot */
        .col-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--col-color, #555);
            flex-shrink: 0;
            transition: all 0.2s;
            box-shadow: 0 0 0 2px #000;
        }
        .col-item-selected .col-dot {
            width: 14px;
            height: 14px;
            box-shadow: 0 0 6px var(--col-color, #555);
        }

        /* Vertical line connecting dots */
        .col-item::before {
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: var(--line-width, 2px);
            background: var(--col-color, #333);
            opacity: 0.2;
        }
        .col-item:first-child::before { top: 50%; }
        .col-item:last-child::before { bottom: 50%; }
        .col-item:only-child::before { display: none; }

        .col-label {
            flex: 1;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 13px;
            color: #ccc;
        }
        .col-item-selected .col-label { color: #fff; font-weight: 500; }

        .col-count {
            font-size: 10px;
            color: #555;
            flex-shrink: 0;
            padding: 1px 6px;
            background: #111;
            border-radius: 8px;
        }
        .col-item-selected .col-count { color: #888; background: #1a1a1a; }

        .col-badge {
            font-size: 9px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            flex-shrink: 0;
        }

        .col-arrow {
            color: #333;
            font-size: 10px;
            flex-shrink: 0;
            transition: color 0.15s;
        }
        .col-item-selected .col-arrow { color: var(--col-color, #888); }
        .col-item-leaf .col-arrow { display: none; }

        /* URL leaf items */
        .col-item-url {
            border-left-color: transparent;
        }
        .col-item-url .col-label {
            color: #0077CC;
            font-size: 12px;
        }
        .col-item-url:hover .col-label {
            color: #3399DD;
            text-decoration: underline;
        }

        /* ── Response items (full output expandable) ── */
        .col-item-response {
            flex-direction: column;
            align-items: stretch;
            padding: 12px 12px 12px 40px;
            gap: 0;
        }
        .col-item-response .col-dot {
            position: absolute;
            left: 14px;
            top: 18px;
        }
        .response-item-content {
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 100%;
        }
        .response-item-top {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .response-item-top .col-label {
            flex: 1;
            min-width: 0;
        }
        .response-snippet {
            font-size: 11px;
            color: #777;
            line-height: 1.5;
            font-style: italic;
            padding: 6px 0 2px;
        }
        .response-expand-toggle,
        .response-collapse-toggle {
            font-size: 11px;
            color: #E0E0E0;
            cursor: pointer;
            padding: 4px 0;
            opacity: 0.7;
            transition: opacity 0.15s;
            user-select: none;
        }
        .response-expand-toggle:hover,
        .response-collapse-toggle:hover {
            opacity: 1;
        }
        .expand-icon {
            font-size: 9px;
            display: inline-block;
            margin-right: 4px;
        }
        .response-full-text {
            margin-top: 8px;
            border-top: 1px solid #1a1a1a;
            padding-top: 10px;
        }
        .response-full-content {
            font-size: 12px;
            line-height: 1.7;
            color: #bbb;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
            padding: 8px 12px;
            background: #0a0a0a;
            border-radius: 6px;
            border: 1px solid #1a1a1a;
            margin-bottom: 8px;
        }

        /* Horizontal connector lines between columns (SVG overlay) */
        .connector-svg {
            position: absolute;
            top: 0;
            right: -24px;
            width: 24px;
            height: 100%;
            pointer-events: none;
            z-index: 5;
            overflow: visible;
        }

        /* (Output panel removed — full output is now inline in the response column) */

        /* ── Zoom controls ── */
        .zoom-controls {
            position: fixed;
            bottom: 24px;
            right: 24px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            z-index: 100;
        }
        .zoom-btn {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #1a1a1a;
            border: 1px solid #333;
            color: #aaa;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            font-family: 'Poppins', sans-serif;
        }
        .zoom-btn:hover { background: #252525; color: #fff; }
        .zoom-fit { font-size: 14px; }

        /* ── Tooltip ── */
        .tooltip {
            position: fixed;
            display: none;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 12px;
            color: #ccc;
            max-width: 320px;
            z-index: 200;
            pointer-events: none;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }
        .tooltip-title {
            font-size: 13px;
            font-weight: 500;
            color: #fff;
            margin-bottom: 6px;
        }
        .tooltip-stat {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            padding: 2px 0;
        }
        .tooltip-stat-label { color: #888; }
        .tooltip-stat-value { color: #ddd; font-weight: 500; }

        /* ── Summary bar ── */
        .summary-bar {
            display: flex;
            gap: 24px;
            padding: 16px 0 24px;
            border-bottom: 1px solid #1a1a1a;
            margin-bottom: 24px;
        }
        .summary-stat {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .summary-value {
            font-size: 28px;
            font-weight: 600;
            color: #fff;
            letter-spacing: -0.02em;
        }
        .summary-label {
            font-size: 11px;
            font-weight: 400;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        /* Empty state */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 60vh;
            color: #555;
            font-size: 16px;
            gap: 8px;
        }
        .empty-state-icon { font-size: 48px; opacity: 0.3; }

        /* Scrollbar styling */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
        '''

    def _get_scripts(self) -> str:
        return '''
    // ── State ──
    let currentScale = 1;
    let selectedPath = [];   // Array of {node, depth} representing current drill path
    let columns = [];        // DOM references to column elements

    // Line widths thin out as depth increases (trunk → branches → twigs)
    const LINE_WIDTHS = [4, 3, 3, 2, 2, 2, 2, 1, 1];

    // ── Initialize ──
    document.addEventListener('DOMContentLoaded', () => {
        renderLegend();
        renderColumn(treeData.children, 0, treeData);
    });

    // ── Legend ──
    function renderLegend() {
        const legend = document.getElementById('legend');
        const levels = hasPersona ? levelOrder : levelOrder.filter(l => l !== 'persona' && l !== 'intent');
        legend.innerHTML = levels.map(level =>
            `<span class="legend-item">
                <span class="legend-dot" style="background:${levelColors[level]}"></span>
                ${capitalize(level)}
            </span>`
        ).join('');
    }

    // ── Render a single column ──
    function renderColumn(children, depth, parentNode) {
        if (!children || children.length === 0) return;

        const viewport = document.getElementById('columns-viewport');

        // Remove columns to the right of this depth
        removeColumnsFrom(depth);

        const nodeType = children[0].type || 'prompt';
        const color = getColorForType(nodeType, children[0]);
        const lineWidth = LINE_WIDTHS[Math.min(depth, LINE_WIDTHS.length - 1)];
        const isWide = nodeType === 'prompt' || nodeType === 'url' || nodeType === 'response';

        const col = document.createElement('div');
        col.className = 'tree-column' + (isWide ? ' tree-column-wide' : '');
        col.setAttribute('data-depth', depth);
        col.style.setProperty('--col-color', color);
        col.style.setProperty('--line-width', lineWidth + 'px');

        // Column header
        col.innerHTML = `
            <div class="column-header">
                <span class="column-type-label" style="color:${color}">${capitalize(nodeType)}</span>
                <span class="column-count">${children.length} item${children.length !== 1 ? 's' : ''}</span>
            </div>
            <div class="column-items"></div>
        `;

        const itemsContainer = col.querySelector('.column-items');

        children.forEach((node, idx) => {
            const isUrl = node.type === 'url';
            const isResponse = node.type === 'response';
            const hasKids = node.children && node.children.length > 0;
            const badge = getBadgeHtml(node);

            const item = document.createElement('div');
            item.className = 'col-item'
                + (isUrl ? ' col-item-url col-item-leaf' : '')
                + (isResponse ? ' col-item-response' : '')
                + (!hasKids && !isUrl ? ' col-item-leaf' : '');
            item.style.setProperty('--col-color', getColorForType(node.type, node));
            item.style.setProperty('--line-width', lineWidth + 'px');

            if (isResponse && node.full_output) {
                // Response nodes show a preview snippet + expandable full text
                const snippet = truncate(node.full_output.replace(/\\n/g, ' ').replace(/\\s+/g, ' ').trim(), 120);
                item.innerHTML = `
                    <div class="col-dot"></div>
                    <div class="response-item-content">
                        <div class="response-item-top">
                            <span class="col-label" title="${escapeHtml(node.name)}">${escapeHtml(node.name)}</span>
                            ${badge}
                            <span class="col-count">${node.count}</span>
                            <span class="col-arrow">&#x25B6;</span>
                        </div>
                        <div class="response-snippet">${escapeHtml(snippet)}</div>
                        <div class="response-expand-toggle" data-node-idx="${idx}">
                            <span class="expand-icon">&#x25BC;</span> Expand full response
                        </div>
                        <div class="response-full-text" id="response-full-${depth}-${idx}" style="display:none">
                            <div class="response-full-content">${escapeHtml(node.full_output)}</div>
                            <div class="response-collapse-toggle" data-node-idx="${idx}">
                                <span class="expand-icon">&#x25B2;</span> Collapse
                            </div>
                        </div>
                    </div>
                `;
            } else {
                item.innerHTML = `
                    <div class="col-dot"></div>
                    <span class="col-label" title="${escapeHtml(node.name)}">${escapeHtml(isUrl ? truncateUrl(node.name) : truncate(node.name, 40))}</span>
                    ${badge}
                    ${!isUrl ? '<span class="col-count">' + node.count + '</span>' : ''}
                    <span class="col-arrow">&#x25B6;</span>
                `;
            }

            // Click handler
            item.addEventListener('click', () => {
                if (isUrl) {
                    window.open(node.name, '_blank', 'noopener,noreferrer');
                    return;
                }
                // Deselect siblings
                itemsContainer.querySelectorAll('.col-item-selected').forEach(el => el.classList.remove('col-item-selected'));
                item.classList.add('col-item-selected');

                // Update selected path
                selectedPath = selectedPath.slice(0, depth);
                selectedPath.push({ node, depth, name: node.name });

                // (Full output is shown inline in response column nodes)

                // Render children as next column
                if (hasKids) {
                    renderColumn(node.children, depth + 1, node);
                } else {
                    removeColumnsFrom(depth + 1);
                }
                updateBreadcrumb();
                scrollToColumn(depth + 1);
            });

            // Expand/collapse toggle for response nodes
            if (isResponse && node.full_output) {
                const expandToggle = item.querySelector('.response-expand-toggle');
                const collapseToggle = item.querySelector('.response-collapse-toggle');
                const fullTextEl = item.querySelector('.response-full-text');

                if (expandToggle) {
                    expandToggle.addEventListener('click', (e) => {
                        e.stopPropagation();
                        fullTextEl.style.display = 'block';
                        expandToggle.style.display = 'none';
                    });
                }
                if (collapseToggle) {
                    collapseToggle.addEventListener('click', (e) => {
                        e.stopPropagation();
                        fullTextEl.style.display = 'none';
                        expandToggle.style.display = '';
                    });
                }
            }

            // Hover tooltip
            item.addEventListener('mouseenter', (e) => showTooltip(e, node));
            item.addEventListener('mouseleave', hideTooltip);

            itemsContainer.appendChild(item);
        });

        viewport.appendChild(col);
        columns.push(col);
    }

    // ── Remove columns from a given depth onward ──
    function removeColumnsFrom(depth) {
        const viewport = document.getElementById('columns-viewport');
        while (columns.length > depth) {
            const col = columns.pop();
            col.style.opacity = '0';
            col.style.transform = 'translateX(20px)';
            setTimeout(() => col.remove(), 200);
        }
    }

    // ── Scroll to make a column visible ──
    function scrollToColumn(depth) {
        const viewport = document.getElementById('columns-viewport');
        const canvas = document.getElementById('canvas');
        // Calculate target scroll position
        let targetX = 0;
        for (let i = 0; i < Math.min(depth, columns.length); i++) {
            targetX += columns[i].offsetWidth;
        }
        // Keep at least 1 column visible on the left for context
        const maxScroll = Math.max(0, targetX - canvas.offsetWidth * 0.4);
        canvas.scrollTo({ left: maxScroll, behavior: 'smooth' });
    }

    // ── Breadcrumb ──
    function updateBreadcrumb() {
        const bar = document.getElementById('breadcrumb');
        let html = `<span class="crumb crumb-root ${selectedPath.length === 0 ? 'crumb-active' : ''}" data-depth="-1" onclick="navigateToDepth(-1)">&#x25C0; ${escapeHtml(brandName)}</span>`;

        selectedPath.forEach((step, idx) => {
            const isActive = idx === selectedPath.length - 1;
            const color = getColorForType(step.node.type, step.node);
            html += `<span class="crumb-separator" style="color:${color}">&#x25B6;</span>`;
            html += `<span class="crumb ${isActive ? 'crumb-active' : ''}" style="border-left:3px solid ${color};padding-left:8px" onclick="navigateToDepth(${idx})" title="${escapeHtml(step.name)}">${escapeHtml(truncate(step.name, 30))}</span>`;
        });

        bar.innerHTML = html;
    }

    function navigateToDepth(depth) {
        if (depth < 0) {
            // Reset to root
            selectedPath = [];
            removeColumnsFrom(0);
            renderColumn(treeData.children, 0, treeData);
            updateBreadcrumb();
            document.getElementById('canvas').scrollTo({ left: 0, behavior: 'smooth' });
            return;
        }

        // Navigate back to a specific depth
        const step = selectedPath[depth];
        selectedPath = selectedPath.slice(0, depth + 1);
        removeColumnsFrom(depth + 1);

        // Re-render next column if the selected node has children
        if (step.node.children && step.node.children.length > 0) {
            renderColumn(step.node.children, depth + 1, step.node);
        }
        updateBreadcrumb();
        scrollToColumn(depth);
    }

    // ── Tooltip ──
    function showTooltip(event, node) {
        const tip = document.getElementById('tooltip');
        let html = `<div class="tooltip-title">${escapeHtml(truncate(node.name, 60))}</div>`;
        html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Type</span><span class="tooltip-stat-value">${capitalize(node.type)}</span></div>`;
        html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Citations</span><span class="tooltip-stat-value">${node.count}</span></div>`;

        if (node.query_id) {
            html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Query ID</span><span class="tooltip-stat-value">${node.query_id}</span></div>`;
        }
        if (node.category && node.category !== 'General') {
            html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Category</span><span class="tooltip-stat-value">${node.category}</span></div>`;
        }
        if (node.type !== 'url' && node.type !== 'domain') {
            const stats = subtreeStats(node);
            if (stats.domains > 0) html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Domains</span><span class="tooltip-stat-value">${stats.domains}</span></div>`;
            if (stats.platforms > 0) html += `<div class="tooltip-stat"><span class="tooltip-stat-label">Platforms</span><span class="tooltip-stat-value">${stats.platforms}</span></div>`;
        }
        if (node.type === 'url') {
            html += `<div style="margin-top:6px;color:#0077CC;font-size:11px">Click to open in new tab</div>`;
        }

        tip.innerHTML = html;
        tip.style.display = 'block';
        const rect = tip.getBoundingClientRect();
        let x = event.clientX + 16;
        let y = event.clientY - 8;
        if (x + rect.width > window.innerWidth - 16) x = event.clientX - rect.width - 16;
        if (y + rect.height > window.innerHeight - 16) y = window.innerHeight - rect.height - 16;
        if (y < 8) y = 8;
        tip.style.left = x + 'px';
        tip.style.top = y + 'px';
    }

    function hideTooltip() {
        document.getElementById('tooltip').style.display = 'none';
    }

    function subtreeStats(node) {
        const domains = new Set();
        const platforms = new Set();
        function walk(n) {
            if (n.type === 'domain') domains.add(n.name);
            if (n.type === 'platform') platforms.add(n.name);
            (n.children || []).forEach(walk);
        }
        walk(node);
        return { domains: domains.size, platforms: platforms.size };
    }

    // (Output panel removed — full output is inline in response column)

    // ── Zoom ──
    function zoomIn() {
        currentScale = Math.min(currentScale * 1.15, 2.5);
        applyZoom();
    }
    function zoomOut() {
        currentScale = Math.max(currentScale / 1.15, 0.4);
        applyZoom();
    }
    function fitView() {
        currentScale = 1;
        applyZoom();
        document.getElementById('canvas').scrollTo({ left: 0, top: 0, behavior: 'smooth' });
    }
    function applyZoom() {
        document.getElementById('columns-viewport').style.transform = `scale(${currentScale})`;
    }

    // ── Helpers ──
    function getColorForType(type, node) {
        if (type === 'presence' && node) {
            return presenceColors[node.name] || levelColors.presence;
        }
        return levelColors[type] || '#555';
    }

    function getBadgeHtml(node) {
        if (node.type === 'presence') {
            const styles = {
                'Featured': 'background:#FF9800;color:#000',
                'Mentioned': 'background:#FFC107;color:#000',
                'Absent': 'background:#F44336;color:#fff',
                'Unknown': 'background:#444;color:#aaa',
            };
            return `<span class="col-badge" style="${styles[node.name] || ''}">${node.name}</span>`;
        }
        if (node.type === 'platform') {
            return `<span class="col-badge" style="background:#4CAF50;color:#000">${node.name}</span>`;
        }
        if (node.type === 'response') {
            return `<span class="col-badge" style="background:#333;color:#bbb">&#x1f4c4; response</span>`;
        }
        if (node.query_type === 'branded') {
            return `<span class="col-badge" style="background:#2196F3;color:#fff">branded</span>`;
        }
        return '';
    }

    function capitalize(s) {
        return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    function truncate(str, max) {
        if (!str) return '';
        return str.length > max ? str.substring(0, max - 1) + '\\u2026' : str;
    }

    function truncateUrl(url) {
        try {
            const u = new URL(url);
            const path = u.pathname.length > 50 ? u.pathname.substring(0, 50) + '\\u2026' : u.pathname;
            return u.hostname + path;
        } catch {
            return url.length > 70 ? url.substring(0, 70) + '\\u2026' : url;
        }
    }
    '''

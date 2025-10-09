#!/usr/bin/env python3
"""
Live Enhanced Typeform Auditor with Dashboard Generation
Runs actual API calls and generates a complete analysis report
Also supports rendering a dashboard from an existing saved analysis JSON
"""

import os
import json
import csv
from datetime import datetime
from collections import defaultdict
from enhanced_typeform_auditor import (
    EnhancedTypeformAuditor,
    generate_pr_focused_queries
)
from load_env import load_env

# Load environment variables
load_env()

def export_csvs_from_analysis(analysis, brand, timestamp, pr_targets_path=None):
    """Export PR Targets, All Outlets, and Raw Results CSVs from analysis dict."""
    # File paths
    pr_targets_file = pr_targets_path or f"pr_targets_{brand}_{timestamp}.csv"
    all_outlets_file = f"all_outlets_{brand}_{timestamp}.csv"
    raw_results_file = f"raw_results_{brand}_{timestamp}.csv"

    # Ensure analysis keys exist
    all_outlets = analysis.get('all_outlets', []) or []
    pr_targets = analysis.get('top_pr_targets', []) or []
    raw_results = analysis.get('raw_results', []) or []

    # 1) PR Targets CSV
    with open(pr_targets_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'rank', 'outlet', 'category', 'pr_opportunity_score',
            'total_citations', 'platforms_citing', 'recommended_count',
            'brand_mentions', 'action_required', 'sample_context'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, target in enumerate(pr_targets, 1):
            writer.writerow({
                'rank': i,
                'outlet': target.get('domain', ''),
                'category': target.get('category', ''),
                'pr_opportunity_score': target.get('pr_opportunity_score', 0),
                'total_citations': target.get('total_citations', 0),
                'platforms_citing': ', '.join(target.get('platforms_citing', [])) if isinstance(target.get('platforms_citing'), list) else '',
                'recommended_count': target.get('recommended_count', 0),
                'brand_mentions': target.get('brand_mentions', 0),
                'action_required': 'High Priority - No current coverage' if target.get('brand_mentions', 0) == 0 else 'Monitor',
                'sample_context': (target.get('sample_context') or '')[:200]
            })

    # 2) All Outlets CSV
    with open(all_outlets_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'rank', 'outlet', 'category', 'pr_opportunity_score',
            'total_citations', 'platforms_citing', 'platform_count',
            'brand_mentions', 'competitor_mentions', 'recommended_count',
            'is_pr_target', 'sample_context'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, o in enumerate(all_outlets, 1):
            competitors = o.get('competitor_mentions') or {}
            writer.writerow({
                'rank': i,
                'outlet': o.get('domain', ''),
                'category': o.get('category', ''),
                'pr_opportunity_score': o.get('pr_opportunity_score', 0),
                'total_citations': o.get('total_citations', 0),
                'platforms_citing': ', '.join(o.get('platforms_citing', [])) if isinstance(o.get('platforms_citing'), list) else '',
                'platform_count': o.get('platform_count', 0),
                'brand_mentions': o.get('brand_mentions', 0),
                'competitor_mentions': json.dumps(competitors, ensure_ascii=False),
                'recommended_count': o.get('recommended_count', 0),
                'is_pr_target': o.get('is_pr_target', False),
                'sample_context': (o.get('sample_context') or '')[:400]
            })

    # 3) Raw Results CSV
    with open(raw_results_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'platform', 'query', 'brand_mentioned', 'competitors_mentioned',
            'actual_urls', 'inferred_sources', 'recommended_resources',
            'sample_context'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in raw_results:
            q = r.get('query')
            if isinstance(q, dict):
                q_str = q.get('query', json.dumps(q, ensure_ascii=False))
            else:
                q_str = str(q)
            writer.writerow({
                'platform': r.get('platform', ''),
                'query': q_str,
                'brand_mentioned': r.get('brand_mentioned', False),
                'competitors_mentioned': ', '.join(r.get('competitors_mentioned', [])) if isinstance(r.get('competitors_mentioned'), list) else '',
                'actual_urls': ', '.join(r.get('actual_urls', [])) if isinstance(r.get('actual_urls'), list) else '',
                'inferred_sources': ', '.join(r.get('inferred_sources', [])) if isinstance(r.get('inferred_sources'), list) else '',
                'recommended_resources': ', '.join(r.get('recommended_resources', [])) if isinstance(r.get('recommended_resources'), list) else '',
                'sample_context': (r.get('sample_context') or '')[:400]
            })

    return {
        'pr_targets': pr_targets_file,
        'all_outlets': all_outlets_file,
        'raw_results': raw_results_file
    }


def generate_html_dashboard(analysis, brand, downloads=None):
    """Generate an HTML dashboard from the analysis with robust methodology sections"""

    downloads = downloads or {}

    # Derive computed metrics for robust sections
    raw_results = analysis.get('raw_results', [])
    outlets_by_category = analysis.get('outlets_by_category', {}) or {}
    all_outlets = analysis.get('all_outlets', []) or []
    pr_targets = analysis.get('top_pr_targets', []) or []
    total_queries = analysis.get('total_queries', 0)

    platforms_present = sorted({r.get('platform') for r in raw_results if r.get('platform')})
    platform_count_actual = len(platforms_present) if platforms_present else len(analysis.get('methodology', {}).get('platforms_tested', [])) or 4
    expected_results = total_queries * max(1, platform_count_actual)
    total_results = analysis.get('total_results', len(raw_results))
    completion_rate = round((total_results / expected_results) * 100, 1) if expected_results else 0.0

    editorial_count = len(outlets_by_category.get('EDITORIAL_TIER1', [])) + len(outlets_by_category.get('EDITORIAL_TIER2', []))
    pr_targets_count = len(pr_targets)
    total_outlets = len(all_outlets)

    # Platform breakdown
    platform_stats = {}
    for r in raw_results:
        p = r.get('platform')
        if not p:
            continue
        ps = platform_stats.setdefault(p, {
            'responses': 0,
            'brand_mentions': 0,
            'total_links': 0,
            'unique_domains': set(),
        })
        ps['responses'] += 1
        if r.get('brand_mentioned'):
            ps['brand_mentions'] += 1
        for d in r.get('actual_urls', []) or []:
            if d:
                ps['unique_domains'].add(d)
                ps['total_links'] += 1

    # Competitor mentions (sum across all outlets)
    competitor_totals = defaultdict(int)
    for o in all_outlets:
        for comp, cnt in (o.get('competitor_mentions') or {}).items():
            competitor_totals[comp] += cnt
    competitor_rows = sorted(competitor_totals.items(), key=lambda x: (-x[1], x[0]))

    # Recommended resources summary
    rec_counts = defaultdict(int)
    for r in raw_results:
        for d in r.get('recommended_resources', []) or []:
            if d:
                rec_counts[d] += 1
    recommended_rows = sorted(rec_counts.items(), key=lambda x: (-x[1], x[0]))[:10]

    # Sample citation contexts (non-empty, unique)
    sample_contexts = []
    seen_contexts = set()
    for o in all_outlets:
        ctx = (o.get('sample_context') or '').strip()
        if ctx and ctx not in seen_contexts:
            seen_contexts.add(ctx)
            sample_contexts.append(ctx)
        if len(sample_contexts) >= 3:
            break
    if not sample_contexts:
        # Fallback to raw_results if outlet contexts are empty
        for r in raw_results:
            ctx = (r.get('sample_context') or '').strip()
            if ctx and ctx not in seen_contexts:
                seen_contexts.add(ctx)
                sample_contexts.append(ctx)
            if len(sample_contexts) >= 3:
                break

    def category_badge_class(category: str) -> str:
        return {
            'EDITORIAL_TIER1': 'editorial',
            'EDITORIAL_TIER2': 'editorial',
            'SOCIAL_COMMUNITY': 'social',
            'INFORMATIONAL': 'info',
            'ECOMMERCE': 'ecommerce',
            'PR_WIRE': 'pr',
        }.get(category, 'other')

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand} - AI Citation Audit Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .subtitle {{ opacity: 0.9; font-size: 1.1rem; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2.2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .downloads a {{
            color: #2b6cb0;
            text-decoration: none;
        }}
        .downloads a:hover {{
            text-decoration: underline;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: top;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .badge-editorial {{ background: #28a745; color: white; }}
        .badge-social {{ background: #17a2b8; color: white; }}
        .badge-info {{ background: #ffc107; color: #333; }}
        .badge-ecommerce {{ background: #6c757d; color: white; }}
        .badge-pr {{ background: #dc3545; color: white; }}
        .badge-other {{ background: #868e96; color: white; }}
        
        .score {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1rem;
        }}
        
        .high-priority {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ffc107;
            margin-bottom: 20px;
        }}
        
        .methodology {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 6px;
            margin-top: 30px;
        }}

        .split-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}

        .small-note {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 8px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{brand} AI Citation Audit</h1>
            <div class="subtitle">Enhanced PR-Focused Analysis • {datetime.now().strftime('%B %d, %Y')}</div>
        </div>
"""
    # Downloads section (links to CSVs if provided)
    if any(downloads.values()):
        html += """
        <div class="section downloads">
            <h2 class="section-title">⬇️ Downloads</h2>
            <ul>
"""
        if downloads.get('pr_targets'):
            html += f"""                <li><a href="{downloads['pr_targets']}" download>PR Targets CSV</a></li>
"""
        if downloads.get('all_outlets'):
            html += f"""                <li><a href="{downloads['all_outlets']}" download>All Outlets CSV</a></li>
"""
        if downloads.get('raw_results'):
            html += f"""                <li><a href="{downloads['raw_results']}" download>Raw Results CSV</a></li>
"""
        html += """            </ul>
        </div>
"""

    html += f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Brand Mention Rate</div>
                <div class="metric-value">{analysis.get('brand_mention_rate', 0)}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Queries</div>
                <div class="metric-value">{total_queries}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Platforms Tested</div>
                <div class="metric-value">{platform_count_actual}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Outlets Identified</div>
                <div class="metric-value">{total_outlets}</div>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Editorial Outlets</div>
                <div class="metric-value">{editorial_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">PR Targets Identified</div>
                <div class="metric-value">{pr_targets_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Completion Rate</div>
                <div class="metric-value">{completion_rate}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Platforms</div>
                <div class="metric-value">{", ".join(platforms_present) if platforms_present else "N/A"}</div>
            </div>
        </div>
"""
    # PR Targets (always show section; indicate if none)
    html += """
        <div class="section">
            <h2 class="section-title">🎯 Top PR Targets (Editorial Outlets Without Brand Coverage)</h2>
"""
    if pr_targets:
        html += """
            <div class="high-priority">
                <strong>Action Required:</strong> These editorial outlets are frequently cited by AI platforms but don't currently mention your brand. They represent the highest-value PR opportunities.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Outlet</th>
                        <th>Category</th>
                        <th>PR Score</th>
                        <th>Citations</th>
                        <th>Platforms</th>
                        <th>Recommended</th>
                    </tr>
                </thead>
                <tbody>
"""
        for i, target in enumerate(pr_targets[:10], 1):
            cat_class = category_badge_class(target.get('category', 'OTHER'))
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{target.get('domain','')}</strong></td>
                        <td><span class="badge badge-{cat_class}">{(target.get('category','OTHER') or 'OTHER').replace('_', ' ')}</span></td>
                        <td><span class="score">{target.get('pr_opportunity_score', 0)}</span></td>
                        <td>{target.get('total_citations', 0)}</td>
                        <td>{target.get('platform_count', 0)}</td>
                        <td>{'✓' if target.get('recommended_count', 0) > 0 else '-'}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
"""
    else:
        html += """
            <div class="small-note">No editorial PR gaps detected in this run. All high-value editorial outlets that appeared also mentioned the brand.</div>
"""
    html += """
        </div>
"""

    # Platform breakdown
    html += """
        <div class="section">
            <h2 class="section-title">🧭 Platform Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Responses</th>
                        <th>Brand Mention Rate</th>
                        <th>Unique Outlets</th>
                        <th>Total Links Extracted</th>
                    </tr>
                </thead>
                <tbody>
"""
    if platform_stats:
        for p in sorted(platform_stats.keys()):
            ps = platform_stats[p]
            rate = round((ps['brand_mentions'] / ps['responses']) * 100, 1) if ps['responses'] else 0.0
            html += f"""
                    <tr>
                        <td><strong>{p}</strong></td>
                        <td>{ps['responses']}</td>
                        <td>{rate}%</td>
                        <td>{len(ps['unique_domains'])}</td>
                        <td>{ps['total_links']}</td>
                    </tr>
"""
    else:
        html += """
                    <tr><td colspan="5">No platform data available.</td></tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Top outlets overall
    html += """
        <div class="section">
            <h2 class="section-title">🏆 Top Outlets Overall</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Outlet</th>
                        <th>Category</th>
                        <th>PR Score</th>
                        <th>Citations</th>
                        <th>Platforms</th>
                        <th>Brand Mentions</th>
                        <th>Recommended</th>
                    </tr>
                </thead>
                <tbody>
"""
    if all_outlets:
        for i, o in enumerate(all_outlets[:10], 1):
            cat_class = category_badge_class(o.get('category', 'OTHER'))
            platforms_citing = ", ".join(o.get('platforms_citing') or [])
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td><strong>{o.get('domain','')}</strong></td>
                        <td><span class="badge badge-{cat_class}">{(o.get('category','OTHER') or 'OTHER').replace('_', ' ')}</span></td>
                        <td><span class="score">{o.get('pr_opportunity_score', 0)}</span></td>
                        <td>{o.get('total_citations', 0)}</td>
                        <td>{platforms_citing}</td>
                        <td>{o.get('brand_mentions', 0)}</td>
                        <td>{'✓' if (o.get('recommended_count') or 0) > 0 else '-'}</td>
                    </tr>
"""
    else:
        html += """
                    <tr><td colspan="8">No outlets found.</td></tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Top by type (editorial, social, informational)
    top_editorial = analysis.get('top_editorial') or []
    top_social = analysis.get('top_social') or []
    top_info = analysis.get('top_informational') or []
    if top_editorial or top_social or top_info:
        html += """
        <div class="section">
            <h2 class="section-title">📚 Top Outlets by Type</h2>
            <div class="split-grid">
"""
        def render_top_table(title, rows):
            nonlocal html
            html += f"""
                <div>
                    <h3 style="margin-bottom: 12px;">{title}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Outlet</th>
                                <th>PR Score</th>
                                <th>Citations</th>
                                <th>Platforms</th>
                            </tr>
                        </thead>
                        <tbody>
"""
            if rows:
                for o in rows[:5]:
                    platforms_citing = ", ".join(o.get('platforms_citing') or [])
                    html += f"""
                            <tr>
                                <td><strong>{o.get('domain','')}</strong></td>
                                <td><span class="score">{o.get('pr_opportunity_score', 0)}</span></td>
                                <td>{o.get('total_citations', 0)}</td>
                                <td>{platforms_citing}</td>
                            </tr>
"""
            else:
                html += """
                            <tr><td colspan="4">No data.</td></tr>
"""
            html += """
                        </tbody>
                    </table>
                </div>
"""

        render_top_table("Editorial", top_editorial)
        render_top_table("Social/Community", top_social)
        render_top_table("Informational", top_info)

        html += """
            </div>
        </div>
"""

    # Outlets by category (original section kept)
    html += """
        <div class="section">
            <h2 class="section-title">📊 Outlets by Category</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                        <th>Top Outlets</th>
                        <th>Avg PR Score</th>
                    </tr>
                </thead>
                <tbody>
"""
    for category, outlets in outlets_by_category.items():
        if outlets:
            avg_score = sum((o.get('pr_opportunity_score') or 0) for o in outlets) / max(1, len(outlets))
            top_outlets = ', '.join([o.get('domain','') for o in outlets[:3]])
            cat_class = category_badge_class(category)
            html += f"""
                    <tr>
                        <td><span class="badge badge-{cat_class}">{(category or 'OTHER').replace('_', ' ')}</span></td>
                        <td>{len(outlets)}</td>
                        <td>{top_outlets}</td>
                        <td>{avg_score:.1f}</td>
                    </tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Competitor mentions summary
    html += """
        <div class="section">
            <h2 class="section-title">🆚 Competitor Mentions Across Outlets</h2>
            <table>
                <thead>
                    <tr>
                        <th>Competitor</th>
                        <th>Total Mentions</th>
                    </tr>
                </thead>
                <tbody>
"""
    if competitor_rows:
        for comp, cnt in competitor_rows:
            html += f"""
                    <tr>
                        <td><strong>{comp}</strong></td>
                        <td>{cnt}</td>
                    </tr>
"""
    else:
        html += """
                    <tr><td colspan="2">No competitor mentions detected.</td></tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Recommended resources summary
    html += """
        <div class="section">
            <h2 class="section-title">🔗 Recommended Resources Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
"""
    if recommended_rows:
        for dom, cnt in recommended_rows:
            html += f"""
                    <tr>
                        <td><strong>{dom}</strong></td>
                        <td>{cnt}</td>
                    </tr>
"""
    else:
        html += """
                    <tr><td colspan="2">No recommended resources detected.</td></tr>
"""
    html += """
                </tbody>
            </table>
        </div>
"""

    # Sample citation contexts
    html += """
        <div class="section">
            <h2 class="section-title">📝 Sample Citation Contexts</h2>
"""
    if sample_contexts:
        for ctx in sample_contexts:
            safe_ctx = ctx.replace("&", "&").replace("<", "<").replace(">", ">")
            html += f"""
            <div class="small-note" style="background:#f8f9fa;border-left:3px solid #667eea;padding:10px 12px;margin-bottom:10px;">
                {safe_ctx}
            </div>
"""
    else:
        html += """
            <div class="small-note">No sample contexts available.</div>
"""
    html += """
        </div>
"""

    # Methodology
    html += f"""
        <div class="methodology">
            <h3>Methodology</h3>
            <ul>
                <li><strong>Platforms Tested:</strong> {", ".join(analysis.get('methodology', {}).get('platforms_tested', platforms_present) or platforms_present or ['ChatGPT','Claude','Perplexity','Gemini'])}</li>
                <li><strong>Citation Extraction:</strong> {analysis.get('methodology', {}).get('citation_extraction', 'Enhanced with URL extraction and recommendation detection')}</li>
                <li><strong>Scoring Formula:</strong> {analysis.get('methodology', {}).get('scoring_factors', 'Tier weight × Citation frequency × Platform breadth × Recommendation bonus × Brand gap')}</li>
                <li><strong>Classification:</strong> {analysis.get('methodology', {}).get('classification', 'Editorial Tier 1/2, Social, Informational, Ecommerce, PR Wire')}</li>
                <li><strong>Completion Rate:</strong> {completion_rate}% ({total_results} / {expected_results} expected)</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Enhanced Typeform Auditor v1.0 • Turning AI visibility gaps into PR wins</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def main():
    print("=" * 60)
    print("Enhanced Typeform Auditor - Live Test with API Calls")
    print("=" * 60)

    # Non-interactive render-from-JSON path via env var
    json_path_env = os.getenv('ANALYSIS_JSON_PATH')
    if json_path_env and os.path.exists(json_path_env):
        try:
            with open(json_path_env, 'r') as f:
                analysis = json.load(f)
            brand = analysis.get('brand', 'Brand')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            # Export CSVs from saved analysis
            downloads = export_csvs_from_analysis(analysis, brand, timestamp)

            # Generate HTML dashboard (with download links)
            html_file = f"dashboard_{brand}_{timestamp}.html"
            html_content = generate_html_dashboard(analysis, brand, downloads=downloads)
            with open(html_file, 'w') as f:
                f.write(html_content)
            print(f"✓ Dashboard rendered from JSON: {json_path_env}")
            print(f"✓ Dashboard saved to: {html_file}")
            print(f"✓ CSVs saved: {downloads['pr_targets']}, {downloads['all_outlets']}, {downloads['raw_results']}")
            # Optional auto-open
            if os.getenv('OPEN_DASHBOARD') == '1':
                os.system(f"open {html_file}")
            return
        except Exception as e:
            print(f"❌ Failed to render from ANALYSIS_JSON_PATH: {e}")
            # Fall through to interactive mode

    # Interactive mode (original behavior)
    brand = input("\nEnter brand name (or press Enter for 'Tesla'): ").strip() or "Tesla"
    
    # Default competitors
    default_competitors = {
        "Tesla": ["Rivian", "Lucid Motors", "Ford"],
        "Apple": ["Samsung", "Google", "Microsoft"],
        "Nike": ["Adidas", "Puma", "Under Armour"]
    }
    
    competitors_input = input(f"Enter competitors (comma-separated, or press Enter for defaults): ").strip()
    if competitors_input:
        competitors = [c.strip() for c in competitors_input.split(',')]
    else:
        competitors = default_competitors.get(brand, ["Competitor 1", "Competitor 2", "Competitor 3"])
    
    general_query = input(f"Enter test query (or press Enter for default): ").strip()
    if not general_query:
        if brand.lower() == "tesla":
            general_query = "What are the best electric vehicles for families?"
        else:
            general_query = f"What are the best {brand.lower()} alternatives?"
    
    print(f"\n📋 Configuration:")
    print(f"  Brand: {brand}")
    print(f"  Competitors: {', '.join(competitors)}")
    print(f"  Query: {general_query}")
    
    # Check API keys
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_perplexity = bool(os.getenv('PERPLEXITY_API_KEY') or os.getenv('PPLX_API_KEY'))
    has_gemini = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY'))
    
    print(f"\n🔑 API Keys Available:")
    print(f"  OpenAI (ChatGPT): {'✓' if has_openai else '✗'}")
    print(f"  Anthropic (Claude): {'✓' if has_anthropic else '✗'}")
    print(f"  Perplexity: {'✓' if has_perplexity else '✗'}")
    print(f"  Gemini: {'✓' if has_gemini else '✗'}")
    
    available_platforms = sum([has_openai, has_anthropic, has_perplexity, has_gemini])
    if available_platforms == 0:
        print("\n❌ No API keys found. Please set at least one API key in your .env file, or set ANALYSIS_JSON_PATH to render from an existing JSON.")
        return
    
    print(f"\n✓ {available_platforms} platforms available for testing")
    
    # Generate queries
    print("\n🤖 Generating test queries...")
    queries = generate_pr_focused_queries(
        brand, 
        general_query, 
        competitors, 
        os.getenv('OPENAI_API_KEY')
    )
    
    print("\nGenerated queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    
    # Limit queries for testing
    num_queries = input(f"\nHow many queries to test? (1-{len(queries)}, default 2): ").strip()
    try:
        num_queries = min(max(1, int(num_queries)), len(queries))
    except:
        num_queries = 2
    
    queries = queries[:num_queries]
    
    # Confirm before running
    total_api_calls = num_queries * available_platforms
    print(f"\n⚠️  This will make approximately {total_api_calls} API calls")
    confirm = input("Proceed? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Run the audit
    print(f"\n🚀 Starting audit with {num_queries} queries across {available_platforms} platforms...")
    print("This may take 2-3 minutes...\n")
    
    auditor = EnhancedTypeformAuditor(brand, competitors, queries)
    
    try:
        analysis = auditor.run_audit()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Save JSON analysis
        analysis_file = f"enhanced_audit_{brand}_{timestamp}.json"
        auditor.save_analysis(analysis_file)
        print(f"\n✓ Analysis saved to: {analysis_file}")
        
        # Save PR targets CSV (existing behavior)
        pr_targets_file = f"pr_targets_{brand}_{timestamp}.csv"
        auditor.export_pr_targets_csv(pr_targets_file)
        print(f"✓ PR targets CSV saved to: {pr_targets_file}")

        # Export remaining CSVs from current analysis for download links
        downloads = export_csvs_from_analysis(analysis, brand, timestamp, pr_targets_path=pr_targets_file)
        print(f"✓ CSVs saved: {downloads['pr_targets']}, {downloads['all_outlets']}, {downloads['raw_results']}")
        
        # Generate HTML dashboard with download links
        html_file = f"dashboard_{brand}_{timestamp}.html"
        html_content = generate_html_dashboard(analysis, brand, downloads=downloads)
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"✓ Dashboard saved to: {html_file}")
        
        # Display summary
        print("\n" + "=" * 60)
        print("AUDIT RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Overall Metrics:")
        print(f"  • Brand Mention Rate: {analysis['brand_mention_rate']}%")
        print(f"  • Total Outlets Found: {len(analysis['all_outlets'])}")
        print(f"  • Editorial Outlets: {len(analysis['outlets_by_category'].get('EDITORIAL_TIER1', [])) + len(analysis['outlets_by_category'].get('EDITORIAL_TIER2', []))}")
        print(f"  • PR Targets Identified: {len(analysis['top_pr_targets'])}")
        
        if analysis['top_pr_targets']:
            print(f"\n🎯 Top 5 PR Targets (Editorial outlets without brand coverage):")
            for i, target in enumerate(analysis['top_pr_targets'][:5], 1):
                print(f"  {i}. {target['domain']}")
                print(f"     Score: {target['pr_opportunity_score']} | Citations: {target['total_citations']} | Platforms: {target['platform_count']}")
        
        print(f"\n📁 Files Generated:")
        print(f"  • Analysis: {analysis_file}")
        print(f"  • PR Targets: {downloads['pr_targets']}")
        print(f"  • All Outlets: {downloads['all_outlets']}")
        print(f"  • Raw Results: {downloads['raw_results']}")
        print(f"  • Dashboard: {html_file}")
        
        # Open dashboard
        open_dashboard = input(f"\n🌐 Open dashboard in browser? (y/n): ").strip().lower()
        if open_dashboard == 'y':
            os.system(f"open {html_file}")
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

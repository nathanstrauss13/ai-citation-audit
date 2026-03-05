"""
AEO Intelligence Platform - Dashboard Engine

Generates interactive HTML dashboards from analysis insights.

Supports three dashboard variants:
- Head-to-Head: Two-brand direct comparison (Tech)
- Brand/Corporate: Single brand vs competitive field (Retail)
- Hospitality/Portfolio: Multi-property analysis

Dashboard Features:
- Score rings visualization
- Competitor rankings (discovered)
- Citation tier analysis
- Platform comparison
- Segment breakdowns
- Content Conversion metrics

Usage:
    from engines.dashboard_engine import DashboardEngine
    from engines.analysis_engine import AnalysisEngine

    insights = analysis_engine.analyze_study(study_id)
    dashboard_engine = DashboardEngine()

    # Generate dashboard
    html = dashboard_engine.generate_dashboard(insights)

    # Save to file
    with open('dashboard.html', 'w') as f:
        f.write(html)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .analysis_engine import StudyInsights

logger = logging.getLogger(__name__)


# Color schemes
BRAND_COLORS = {
    "primary": "#0066cc",
    "secondary": "#00cc66",
    "accent": "#ff6600",
    "warning": "#ffcc00",
    "danger": "#cc0000",
    "muted": "#666666",
    "light": "#f5f5f5",
    "dark": "#333333"
}

PLATFORM_COLORS = {
    "chatgpt": "#10a37f",
    "claude": "#d4a373",
    "perplexity": "#20b2aa",
    "gemini": "#4285f4",
    "meta_llama": "#0668E1"
}

PROMINENCE_COLORS = {
    "featured_first": "#00cc66",
    "recommended": "#66cc00",
    "listed": "#ffcc00",
    "mentioned": "#ff9900",
    "not_mentioned": "#cc0000"
}


class DashboardEngine:
    """
    Generates interactive HTML dashboards from analysis insights.
    """

    def __init__(self):
        """Initialize dashboard engine."""
        pass

    def generate_dashboard(
        self,
        insights: StudyInsights,
        variant: str = "auto",
        title: Optional[str] = None,
        include_raw_data: bool = False
    ) -> str:
        """
        Generate an interactive HTML dashboard.

        Args:
            insights: StudyInsights from AnalysisEngine
            variant: Dashboard variant (auto, head_to_head, brand_corporate, hospitality)
            title: Custom title (default: brand name)
            include_raw_data: Include JSON data in dashboard for export

        Returns:
            Complete HTML document as string
        """
        # Auto-detect variant
        if variant == "auto":
            variant = self._detect_variant(insights)

        title = title or f"{insights.brand_name} AI Visibility Analysis"

        # Build dashboard components
        html_parts = [
            self._generate_head(title, insights.brand_name),
            self._generate_header(title, insights),
            self._generate_summary_cards(insights),
            self._generate_prominence_chart(insights),
            self._generate_platform_comparison(insights),
            self._generate_competitor_table(insights),
            self._generate_citation_analysis(insights),
            self._generate_segment_charts(insights),
            self._generate_insights_panel(insights),
            self._generate_footer(insights),
        ]

        if include_raw_data:
            html_parts.append(self._generate_data_export(insights))

        return self._wrap_html(html_parts)

    def _detect_variant(self, insights: StudyInsights) -> str:
        """Detect appropriate variant based on study type."""
        study_type = insights.study_type

        if study_type == "head_to_head":
            return "head_to_head"
        elif study_type in ["organic_visibility", "brand_perception", "comprehensive"]:
            return "brand_corporate"
        else:
            return "brand_corporate"

    def _wrap_html(self, parts: List[str]) -> str:
        """Wrap all parts in complete HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
{parts[0]}
</head>
<body>
<div class="dashboard-container">
{''.join(parts[1:])}
</div>
</body>
</html>"""

    def _generate_head(self, title: str, brand_name: str) -> str:
        """Generate HTML head with styles and scripts."""
        return f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            line-height: 1.6;
        }}

        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Header */
        .dashboard-header {{
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .dashboard-header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00cc66, #0066cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .dashboard-header .subtitle {{
            color: #888;
            font-size: 1.1rem;
        }}

        .dashboard-header .meta {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}

        .dashboard-header .meta-item {{
            background: rgba(255,255,255,0.05);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
        }}

        /* Cards Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}

        .metric-card .label {{
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .metric-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00cc66, #0066cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .metric-card .delta {{
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        .metric-card .delta.positive {{
            color: #00cc66;
        }}

        .metric-card .delta.negative {{
            color: #cc0000;
        }}

        /* Sections */
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .section-title {{
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-title .icon {{
            font-size: 1.5rem;
        }}

        /* Charts Container */
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .chart-container {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .chart-container h3 {{
            margin-bottom: 1rem;
            font-size: 1.1rem;
            color: #ccc;
        }}

        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}

        /* Score Ring */
        .score-ring-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}

        .score-ring {{
            position: relative;
            width: 200px;
            height: 200px;
        }}

        .score-ring svg {{
            transform: rotate(-90deg);
        }}

        .score-ring .ring-bg {{
            fill: none;
            stroke: rgba(255,255,255,0.1);
            stroke-width: 12;
        }}

        .score-ring .ring-fill {{
            fill: none;
            stroke-width: 12;
            stroke-linecap: round;
            transition: stroke-dashoffset 1s ease-out;
        }}

        .score-ring .score-value {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .score-ring .score-value .number {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00cc66, #0066cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .score-ring .score-value .label {{
            color: #888;
            font-size: 0.9rem;
        }}

        /* Tables */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        .data-table th,
        .data-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .data-table th {{
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 1px;
        }}

        .data-table tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        .data-table .rank {{
            color: #00cc66;
            font-weight: 700;
        }}

        /* Progress Bar */
        .progress-bar {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}

        .progress-bar .fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease-out;
        }}

        /* Insights Panel */
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}

        .insight-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.25rem;
            border-left: 4px solid;
        }}

        .insight-card.insight {{
            border-color: #0066cc;
        }}

        .insight-card.opportunity {{
            border-color: #00cc66;
        }}

        .insight-card.threat {{
            border-color: #cc0000;
        }}

        .insight-card .insight-type {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        .insight-card.insight .insight-type {{
            color: #0066cc;
        }}

        .insight-card.opportunity .insight-type {{
            color: #00cc66;
        }}

        .insight-card.threat .insight-type {{
            color: #cc0000;
        }}

        /* Platform Colors */
        .platform-chatgpt {{ background: {PLATFORM_COLORS['chatgpt']}; }}
        .platform-claude {{ background: {PLATFORM_COLORS['claude']}; }}
        .platform-perplexity {{ background: {PLATFORM_COLORS['perplexity']}; }}
        .platform-gemini {{ background: {PLATFORM_COLORS['gemini']}; }}
        .platform-meta_llama {{ background: {PLATFORM_COLORS['meta_llama']}; }}

        /* Footer */
        .dashboard-footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.85rem;
        }}

        .dashboard-footer a {{
            color: #0066cc;
            text-decoration: none;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .dashboard-container {{
                padding: 1rem;
            }}

            .dashboard-header h1 {{
                font-size: 1.8rem;
            }}

            .charts-row {{
                grid-template-columns: 1fr;
            }}

            .metric-card .value {{
                font-size: 2rem;
            }}
        }}
    </style>"""

    def _generate_header(self, title: str, insights: StudyInsights) -> str:
        """Generate dashboard header."""
        generated_date = datetime.now().strftime("%B %d, %Y")

        return f"""
    <header class="dashboard-header">
        <h1>{insights.brand_name}</h1>
        <p class="subtitle">AI Visibility & Citation Intelligence Analysis</p>
        <div class="meta">
            <span class="meta-item">📊 Study Type: {insights.study_type.replace('_', ' ').title()}</span>
            <span class="meta-item">📅 Generated: {generated_date}</span>
            <span class="meta-item">💬 {insights.brand_metrics.total_responses} Responses Analyzed</span>
        </div>
    </header>"""

    def _generate_summary_cards(self, insights: StudyInsights) -> str:
        """Generate summary metric cards."""
        bm = insights.brand_metrics

        cards_html = f"""
    <div class="cards-grid">
        <div class="metric-card">
            <div class="label">Visibility Score</div>
            <div class="value">{bm.visibility_score:.0f}</div>
            <div class="delta">Composite AI visibility index</div>
        </div>

        <div class="metric-card">
            <div class="label">Mention Rate</div>
            <div class="value">{bm.mention_rate:.0f}%</div>
            <div class="delta">{bm.mention_count} of {bm.total_responses} responses</div>
        </div>

        <div class="metric-card">
            <div class="label">Featured First</div>
            <div class="value">{bm.featured_first_rate:.0f}%</div>
            <div class="delta">{bm.featured_first_count} times as top recommendation</div>
        </div>

        <div class="metric-card">
            <div class="label">Prominence Score</div>
            <div class="value">{bm.prominence_score:.0f}</div>
            <div class="delta">Weighted position strength</div>
        </div>
    </div>"""

        return cards_html

    def _generate_prominence_chart(self, insights: StudyInsights) -> str:
        """Generate prominence distribution visualization."""
        bm = insights.brand_metrics

        # Calculate ring progress (visibility score out of 100)
        score = bm.visibility_score
        circumference = 2 * 3.14159 * 80  # radius = 80
        offset = circumference * (1 - score / 100)

        # Prominence data for bar chart
        prominence_data = {
            "Featured First": bm.featured_first_count,
            "Recommended": bm.recommended_count,
            "Listed": bm.listed_count,
            "Mentioned Only": bm.mentioned_only_count,
            "Not Mentioned": bm.not_mentioned_count
        }

        return f"""
    <div class="charts-row">
        <div class="chart-container">
            <h3>📈 Visibility Score</h3>
            <div class="score-ring-container">
                <div class="score-ring">
                    <svg width="200" height="200" viewBox="0 0 200 200">
                        <circle class="ring-bg" cx="100" cy="100" r="80"/>
                        <circle class="ring-fill" cx="100" cy="100" r="80"
                            stroke="url(#gradient)"
                            stroke-dasharray="{circumference}"
                            stroke-dashoffset="{offset}"/>
                        <defs>
                            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#00cc66"/>
                                <stop offset="100%" stop-color="#0066cc"/>
                            </linearGradient>
                        </defs>
                    </svg>
                    <div class="score-value">
                        <div class="number">{score:.0f}</div>
                        <div class="label">out of 100</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="chart-container">
            <h3>📊 Prominence Distribution</h3>
            <div class="chart-wrapper">
                <canvas id="prominenceChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Prominence Chart
        new Chart(document.getElementById('prominenceChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(prominence_data.keys()))},
                datasets: [{{
                    label: 'Responses',
                    data: {json.dumps(list(prominence_data.values()))},
                    backgroundColor: ['#00cc66', '#66cc00', '#ffcc00', '#ff9900', '#cc0000'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#888' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#888' }}
                    }}
                }}
            }}
        }});
    </script>"""

    def _generate_platform_comparison(self, insights: StudyInsights) -> str:
        """Generate platform comparison chart."""
        platforms = insights.platform_metrics

        if not platforms:
            return ""

        labels = [p.platform.title() for p in platforms]
        mention_data = [p.mention_rate for p in platforms]
        featured_data = [p.featured_rate for p in platforms]
        colors = [PLATFORM_COLORS.get(p.platform, '#666666') for p in platforms]

        return f"""
    <div class="section">
        <h2 class="section-title"><span class="icon">🤖</span> Platform Comparison</h2>
        <div class="charts-row">
            <div class="chart-container">
                <h3>Mention Rate by Platform</h3>
                <div class="chart-wrapper">
                    <canvas id="platformMentionChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>Featured Rate by Platform</h3>
                <div class="chart-wrapper">
                    <canvas id="platformFeaturedChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Platform Mention Chart
        new Chart(document.getElementById('platformMentionChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Mention Rate %',
                    data: {json.dumps(mention_data)},
                    backgroundColor: {json.dumps(colors)},
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        max: 100,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#888', callback: v => v + '%' }}
                    }},
                    y: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#ccc' }}
                    }}
                }}
            }}
        }});

        // Platform Featured Chart
        new Chart(document.getElementById('platformFeaturedChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Featured Rate %',
                    data: {json.dumps(featured_data)},
                    backgroundColor: {json.dumps(colors)},
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        max: 100,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#888', callback: v => v + '%' }}
                    }},
                    y: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#ccc' }}
                    }}
                }}
            }}
        }});
    </script>"""

    def _generate_competitor_table(self, insights: StudyInsights) -> str:
        """Generate competitor ranking table."""
        competitors = insights.discovered_competitors

        if not competitors:
            return ""

        rows = ""
        for i, comp in enumerate(competitors[:10], 1):
            h2h = f"{comp.head_to_head_wins}W / {comp.head_to_head_losses}L"
            win_rate_width = min(comp.win_rate, 100)
            rows += f"""
                <tr>
                    <td class="rank">#{i}</td>
                    <td><strong>{comp.brand_name}</strong></td>
                    <td>{comp.mention_count}</td>
                    <td>{comp.featured_count}</td>
                    <td>
                        {comp.win_rate:.1f}%
                        <div class="progress-bar">
                            <div class="fill" style="width: {win_rate_width}%; background: linear-gradient(90deg, #00cc66, #0066cc);"></div>
                        </div>
                    </td>
                    <td>{h2h}</td>
                </tr>"""

        return f"""
    <div class="section">
        <h2 class="section-title"><span class="icon">🏆</span> Competitive Landscape (Discovered)</h2>
        <p style="color: #888; margin-bottom: 1rem;">Competitors discovered organically from AI responses, not pre-specified.</p>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Competitor</th>
                    <th>Mentions</th>
                    <th>Featured</th>
                    <th>Win Rate</th>
                    <th>vs {insights.brand_name}</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""

    def _generate_citation_analysis(self, insights: StudyInsights) -> str:
        """Generate citation tier analysis."""
        cm = insights.citation_metrics

        if cm.total_citations == 0:
            return """
    <div class="section">
        <h2 class="section-title"><span class="icon">🔗</span> Citation Analysis</h2>
        <p style="color: #888;">No citation data available. Ensure RAG/web search is enabled during data collection.</p>
    </div>"""

        # Citation tier data
        tier_data = {
            "Owned": cm.owned_citations,
            "Editorial": cm.editorial_citations,
            "Retail": cm.retail_citations,
            "Social": cm.social_citations,
            "Other": cm.other_citations + cm.affiliate_citations + cm.reference_citations
        }

        # Top domains table
        domain_rows = ""
        for domain, count in cm.top_domains[:8]:
            pct = count / cm.total_citations * 100
            domain_rows += f"""
                <tr>
                    <td>{domain}</td>
                    <td>{count}</td>
                    <td>{pct:.1f}%</td>
                </tr>"""

        return f"""
    <div class="section">
        <h2 class="section-title"><span class="icon">🔗</span> Citation Intelligence</h2>
        <div class="charts-row">
            <div class="chart-container">
                <h3>Citation Tiers</h3>
                <div class="chart-wrapper">
                    <canvas id="citationTierChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3>Content Conversion</h3>
                <div style="padding: 2rem; text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; background: linear-gradient(90deg, #00cc66, #0066cc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        {cm.content_conversion_rate:.1f}%
                    </div>
                    <div style="color: #888; margin-top: 0.5rem;">Content Conversion Rate</div>
                    <div style="margin-top: 1rem; color: #ccc;">
                        When {insights.brand_name}'s content is cited,<br/>
                        <strong>{cm.wins_when_cited}</strong> of <strong>{cm.times_brand_cited}</strong> times the brand was featured.
                    </div>
                </div>
            </div>
        </div>

        <div style="margin-top: 1.5rem;">
            <h3 style="margin-bottom: 1rem;">Top Citing Domains</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>Citations</th>
                        <th>Share</th>
                    </tr>
                </thead>
                <tbody>
                    {domain_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Citation Tier Chart
        new Chart(document.getElementById('citationTierChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(tier_data.keys()))},
                datasets: [{{
                    data: {json.dumps(list(tier_data.values()))},
                    backgroundColor: ['#00cc66', '#0066cc', '#ff9900', '#9966ff', '#666666'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{ color: '#ccc' }}
                    }}
                }}
            }}
        }});
    </script>"""

    def _generate_segment_charts(self, insights: StudyInsights) -> str:
        """Generate segment performance charts."""
        segments = insights.segment_metrics

        if not segments:
            return ""

        charts_html = """
    <div class="section">
        <h2 class="section-title"><span class="icon">📂</span> Segment Analysis</h2>
        <div class="charts-row">"""

        chart_id = 0
        for seg_type, metrics_list in segments.items():
            if not metrics_list:
                continue

            labels = [m.segment_value for m in metrics_list[:8]]
            scores = [m.prominence_score for m in metrics_list[:8]]

            charts_html += f"""
            <div class="chart-container">
                <h3>{seg_type.replace('_', ' ').title()}</h3>
                <div class="chart-wrapper">
                    <canvas id="segmentChart{chart_id}"></canvas>
                </div>
            </div>

            <script>
                new Chart(document.getElementById('segmentChart{chart_id}'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            label: 'Prominence Score',
                            data: {json.dumps(scores)},
                            backgroundColor: 'rgba(0, 102, 204, 0.7)',
                            borderRadius: 6
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        plugins: {{
                            legend: {{ display: false }}
                        }},
                        scales: {{
                            x: {{
                                beginAtZero: true,
                                max: 100,
                                grid: {{ color: 'rgba(255,255,255,0.1)' }},
                                ticks: {{ color: '#888' }}
                            }},
                            y: {{
                                grid: {{ display: false }},
                                ticks: {{ color: '#ccc' }}
                            }}
                        }}
                    }}
                }});
            </script>"""
            chart_id += 1

        charts_html += """
        </div>
    </div>"""

        return charts_html

    def _generate_insights_panel(self, insights: StudyInsights) -> str:
        """Generate key insights panel."""
        cards_html = ""

        for insight in insights.key_insights:
            cards_html += f"""
            <div class="insight-card insight">
                <div class="insight-type">💡 Key Insight</div>
                <p>{insight}</p>
            </div>"""

        for opp in insights.opportunities:
            cards_html += f"""
            <div class="insight-card opportunity">
                <div class="insight-type">🎯 Opportunity</div>
                <p>{opp}</p>
            </div>"""

        for threat in insights.threats:
            cards_html += f"""
            <div class="insight-card threat">
                <div class="insight-type">⚠️ Threat</div>
                <p>{threat}</p>
            </div>"""

        if not cards_html:
            return ""

        return f"""
    <div class="section">
        <h2 class="section-title"><span class="icon">💡</span> Strategic Insights</h2>
        <div class="insights-grid">
            {cards_html}
        </div>
    </div>"""

    def _generate_footer(self, insights: StudyInsights) -> str:
        """Generate dashboard footer."""
        return f"""
    <footer class="dashboard-footer">
        <p>Generated by AEO Intelligence Platform</p>
        <p>Study ID: {insights.study_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>"""

    def _generate_data_export(self, insights: StudyInsights) -> str:
        """Generate hidden data export section."""
        json_data = insights.to_json()

        return f"""
    <script type="application/json" id="raw-analysis-data">
    {json_data}
    </script>

    <script>
        // Enable data export
        window.exportAnalysisData = function() {{
            const data = document.getElementById('raw-analysis-data').textContent;
            const blob = new Blob([data], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{insights.brand_name.lower().replace(" ", "_")}_analysis.json';
            a.click();
            URL.revokeObjectURL(url);
        }};
    </script>"""

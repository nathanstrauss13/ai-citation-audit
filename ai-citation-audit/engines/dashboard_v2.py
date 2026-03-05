"""
AEO Intelligence Platform - Dashboard Engine v2

Production-quality dashboard matching innatec3.com design standards.

Features:
- Dark theme with gradient background
- Concentric score rings
- Section navigation dots
- Interactive platform filters
- Category cards with status badges
- Citation tier analysis
- Query appendix with filtering
- Smooth animations

Usage:
    from engines.dashboard_v2 import DashboardEngineV2
    engine = DashboardEngineV2()
    html = engine.generate(insights)
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class DashboardEngineV2:
    """Production-quality dashboard generator."""

    # Brand color (can be customized per brand)
    BRAND_COLOR = "#dc2626"  # Red for retail brands
    BRAND_COLOR_LIGHT = "#fca5a5"

    # Platform colors
    PLATFORM_COLORS = {
        "chatgpt": "#10a37f",
        "claude": "#d4a373",
        "perplexity": "#20b2aa",
        "gemini": "#4285f4",
        "meta_llama": "#0668E1"
    }

    def generate(
        self,
        insights: Any,
        brand_color: str = None,
        include_appendix: bool = True
    ) -> str:
        """Generate complete dashboard HTML."""

        if brand_color:
            self.BRAND_COLOR = brand_color

        sections = [
            self._section_hero(insights),
            self._section_executive_summary(insights),
            self._section_competitive_position(insights),
            self._section_category_performance(insights),
            self._section_platform_comparison(insights),
            self._section_position_analysis(insights),
            self._section_content_authority(insights),
            self._section_citation_analysis(insights),
        ]

        if include_appendix:
            sections.append(self._section_query_appendix(insights))

        nav_dots = self._generate_nav_dots(len(sections))

        return self._wrap_document(
            brand_name=insights.brand_name,
            sections=sections,
            nav_dots=nav_dots,
            insights=insights
        )

    def _wrap_document(self, brand_name: str, sections: List[str], nav_dots: str, insights: Any) -> str:
        """Wrap sections in complete HTML document."""

        sections_html = "\n".join(sections)

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} AI Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
{self._get_styles()}
    </style>
</head>
<body>
    <div class="dashboard">
        {nav_dots}
        <div class="main-content">
            {sections_html}
        </div>
    </div>
    <script>
{self._get_scripts(insights)}
    </script>
</body>
</html>'''

    def _get_styles(self) -> str:
        """Get all CSS styles."""
        return f'''
        :root {{
            --brand-primary: {self.BRAND_COLOR};
            --brand-light: {self.BRAND_COLOR_LIGHT};
            --bg-dark: #0a0a0f;
            --bg-card: rgba(255, 255, 255, 0.03);
            --bg-card-hover: rgba(255, 255, 255, 0.06);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --text-muted: #666666;
            --success: #22c55e;
            --warning: #eab308;
            --danger: #ef4444;
            --info: #3b82f6;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(180deg, #0a0a0f 0%, #111118 50%, #0a0a0f 100%);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}

        .dashboard {{
            display: flex;
            min-height: 100vh;
        }}

        /* Navigation Dots */
        .nav-dots {{
            position: fixed;
            right: 24px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 12px;
            z-index: 1000;
        }}

        .nav-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }}

        .nav-dot:hover {{
            background: rgba(255, 255, 255, 0.5);
            transform: scale(1.2);
        }}

        .nav-dot.active {{
            background: var(--brand-primary);
            box-shadow: 0 0 10px var(--brand-primary);
        }}

        /* Nav dot tooltips */
        .nav-dot::before {{
            content: attr(data-label);
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            pointer-events: none;
        }}

        .nav-dot::after {{
            content: '';
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            border: 5px solid transparent;
            border-left-color: rgba(0, 0, 0, 0.9);
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
        }}

        .nav-dot:hover::before,
        .nav-dot:hover::after {{
            opacity: 1;
            visibility: visible;
        }}

        /* Main Content */
        .main-content {{
            flex: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 60px;
            padding-right: 80px;
        }}

        /* Sections */
        .section {{
            margin-bottom: 60px;
            scroll-margin-top: 40px;
        }}

        .section-label {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--brand-primary);
            margin-bottom: 8px;
        }}

        .section-title {{
            font-size: 28px;
            font-weight: 300;
            color: var(--text-primary);
            margin-bottom: 12px;
        }}

        .section-subtitle {{
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }}

        /* Hero Section */
        .hero {{
            text-align: center;
            padding: 60px 0;
        }}

        .hero-logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 24px;
            background: var(--brand-primary);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 700;
        }}

        .hero-title {{
            font-size: 42px;
            font-weight: 300;
            margin-bottom: 8px;
        }}

        .hero-title .brand {{
            color: var(--brand-primary);
            font-weight: 500;
        }}

        .hero-subtitle {{
            font-size: 16px;
            color: var(--text-secondary);
            margin-bottom: 32px;
        }}

        /* Stats Bar */
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 48px;
            padding: 20px 32px;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 40px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 20px;
            font-weight: 600;
            color: var(--brand-primary);
        }}

        .stat-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        /* Platform Filters */
        .platform-filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid var(--border-color);
            background: transparent;
            color: var(--text-secondary);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover {{
            border-color: var(--text-secondary);
            color: var(--text-primary);
        }}

        .filter-btn.active {{
            background: var(--brand-primary);
            border-color: var(--brand-primary);
            color: white;
        }}

        /* Score Ring */
        .score-ring-container {{
            display: flex;
            align-items: center;
            gap: 40px;
            padding: 24px;
            background: var(--bg-card);
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }}

        .score-ring {{
            position: relative;
            width: 180px;
            height: 180px;
            flex-shrink: 0;
        }}

        .score-ring svg {{
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }}

        .score-ring .ring {{
            fill: none;
            stroke-width: 10;
            stroke-linecap: round;
            transition: stroke-dashoffset 1.5s ease-out;
        }}

        .score-ring .ring-bg {{
            stroke: rgba(255, 255, 255, 0.1);
        }}

        .score-ring .ring-mention {{
            stroke: #22d3ee;
        }}

        .score-ring .ring-top {{
            stroke: #22c55e;
        }}

        .score-ring .ring-featured {{
            stroke: var(--brand-primary);
        }}

        .score-value {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .score-value .number {{
            font-size: 48px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .score-value .label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .score-legend {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        .legend-label {{
            font-size: 14px;
            color: var(--text-secondary);
            flex: 1;
        }}

        .legend-value {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s ease;
        }}

        .kpi-card:hover {{
            background: var(--bg-card-hover);
            transform: translateY(-2px);
        }}

        .kpi-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 32px;
            font-weight: 600;
            color: var(--brand-primary);
        }}

        .kpi-value.success {{
            color: var(--success);
        }}

        .kpi-value.text {{
            font-size: 24px;
            color: var(--brand-primary);
        }}

        .kpi-detail {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        /* Executive Summary */
        .exec-summary {{
            background: var(--bg-card);
            border-left: 3px solid var(--brand-primary);
            border-radius: 0 12px 12px 0;
            padding: 24px 28px;
        }}

        .exec-summary h3 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--brand-primary);
            margin-bottom: 16px;
        }}

        .exec-item {{
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            line-height: 1.6;
        }}

        .exec-item::before {{
            content: "→";
            color: var(--brand-primary);
            flex-shrink: 0;
        }}

        .exec-item strong {{
            color: var(--text-primary);
        }}

        /* Charts Grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
        }}

        .chart-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
        }}

        .chart-card h4 {{
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 20px;
            color: var(--text-primary);
        }}

        .chart-wrapper {{
            height: 280px;
            position: relative;
        }}

        /* Category Cards */
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}

        .category-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }}

        .category-card:hover {{
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }}

        .category-card::after {{
            content: '▼';
            position: absolute;
            bottom: 8px;
            right: 12px;
            font-size: 8px;
            color: var(--text-muted);
            transition: transform 0.3s ease;
        }}

        .category-card.expanded::after {{
            transform: rotate(180deg);
        }}

        .category-card.expanded {{
            background: var(--bg-card-hover);
        }}

        /* Expandable detail section */
        .card-details {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease, margin 0.3s ease;
            margin-top: 0;
            padding-top: 0;
            border-top: 0 solid var(--border-color);
        }}

        .category-card.expanded .card-details {{
            max-height: 300px;
            margin-top: 16px;
            padding-top: 16px;
            border-top-width: 1px;
        }}

        .card-details-content {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.7;
        }}

        .card-details-content strong {{
            color: var(--text-primary);
        }}

        .metric-definition {{
            margin-bottom: 8px;
        }}

        .metric-definition .metric-name {{
            color: var(--brand-primary);
            font-weight: 500;
        }}

        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }}

        .category-name {{
            font-size: 16px;
            font-weight: 500;
            color: var(--text-primary);
        }}

        .category-badge {{
            font-size: 10px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-leading {{
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }}

        .badge-competitive {{
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }}

        .badge-developing {{
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
        }}

        .badge-opportunity {{
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
        }}

        .category-query {{
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .category-metrics {{
            display: flex;
            gap: 16px;
        }}

        .category-metric {{
            text-align: center;
        }}

        .category-metric-value {{
            font-size: 20px;
            font-weight: 600;
            color: var(--brand-primary);
        }}

        .category-metric-label {{
            font-size: 10px;
            text-transform: uppercase;
            color: var(--text-muted);
        }}

        .category-progress {{
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            margin-top: 12px;
            overflow: hidden;
        }}

        .category-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--brand-primary), #f97316);
            border-radius: 2px;
            transition: width 0.5s ease;
        }}

        /* Platform Cards */
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }}

        .platform-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            position: relative;
            transition: all 0.2s ease;
        }}

        .platform-card:hover {{
            background: var(--bg-card-hover);
        }}

        .platform-card .best-badge {{
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--success);
            color: white;
            font-size: 9px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}

        .platform-name {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}

        .platform-value {{
            font-size: 28px;
            font-weight: 600;
            color: var(--brand-primary);
        }}

        .platform-label {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .platform-detail {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
        }}

        /* Competitor Table */
        .competitor-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .competitor-table th {{
            text-align: left;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}

        .competitor-table td {{
            padding: 16px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }}

        .competitor-table tr:hover {{
            background: var(--bg-card);
        }}

        .competitor-rank {{
            font-weight: 700;
            color: var(--brand-primary);
        }}

        .competitor-name {{
            font-weight: 500;
        }}

        /* Citation Tabs */
        .citation-tabs {{
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 24px;
        }}

        .citation-tab {{
            padding: 12px 24px;
            font-size: 14px;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
        }}

        .citation-tab:hover {{
            color: var(--text-primary);
        }}

        .citation-tab.active {{
            color: var(--brand-primary);
            border-bottom-color: var(--brand-primary);
        }}

        /* Citation Bars */
        .citation-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .citation-row {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .citation-domain {{
            width: 180px;
            font-size: 13px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .citation-tag {{
            font-size: 9px;
            padding: 2px 6px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-muted);
        }}

        .citation-bar {{
            flex: 1;
            height: 24px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            display: flex;
        }}

        .citation-bar-fill {{
            height: 100%;
            background: var(--success);
            transition: width 0.5s ease;
        }}

        .citation-bar-other {{
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
        }}

        .citation-stats {{
            width: 120px;
            text-align: right;
            font-size: 13px;
        }}

        .citation-count {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .citation-percent {{
            color: var(--text-secondary);
        }}

        /* Data Table */
        .data-table-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        .data-table th {{
            text-align: left;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            padding: 16px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid var(--border-color);
        }}

        .data-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}

        .data-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        .data-table .yes {{
            color: var(--success);
        }}

        .data-table .no {{
            color: var(--text-muted);
        }}

        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes scaleIn {{
            from {{
                opacity: 0;
                transform: scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        @keyframes countUp {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        .animate-on-scroll {{
            opacity: 0;
        }}

        .animate-on-scroll.visible {{
            animation: fadeInUp 0.6s ease forwards;
        }}

        .animate-on-scroll.visible:nth-child(2) {{ animation-delay: 0.1s; }}
        .animate-on-scroll.visible:nth-child(3) {{ animation-delay: 0.2s; }}
        .animate-on-scroll.visible:nth-child(4) {{ animation-delay: 0.3s; }}
        .animate-on-scroll.visible:nth-child(5) {{ animation-delay: 0.4s; }}
        .animate-on-scroll.visible:nth-child(6) {{ animation-delay: 0.5s; }}

        .score-ring.animate .ring {{
            animation: ringFill 1.5s ease-out forwards;
        }}

        /* KPI card hover effects */
        .kpi-card {{
            cursor: pointer;
        }}

        .kpi-card .kpi-tooltip {{
            display: none;
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.5;
            width: 220px;
            text-align: left;
            z-index: 100;
            margin-bottom: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}

        .kpi-card:hover .kpi-tooltip {{
            display: block;
        }}

        /* Platform card interactivity */
        .platform-card {{
            cursor: pointer;
        }}

        .platform-card .platform-tooltip {{
            display: none;
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 11px;
            line-height: 1.5;
            width: 180px;
            text-align: left;
            z-index: 100;
            margin-bottom: 8px;
        }}

        .platform-card:hover .platform-tooltip {{
            display: block;
        }}

        /* Responsive */
        @media (max-width: 1024px) {{
            .main-content {{
                padding: 24px;
                padding-right: 60px;
            }}

            .charts-grid,
            .category-grid {{
                grid-template-columns: 1fr;
            }}

            .platform-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .nav-dots {{
                right: 12px;
            }}
        }}

        @media (max-width: 768px) {{
            .stats-bar {{
                flex-wrap: wrap;
                gap: 24px;
            }}

            .platform-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .nav-dots {{
                display: none;
            }}

            .main-content {{
                padding-right: 24px;
            }}
        }}
'''

    def _generate_nav_dots(self, section_count: int) -> str:
        """Generate navigation dots with tooltip labels."""
        section_labels = [
            "Overview",
            "Executive Summary",
            "Competitive Position",
            "Category Performance",
            "Platform Comparison",
            "Position Analysis",
            "Content Authority",
            "Citation Analysis",
            "Query Appendix"
        ]

        dots = []
        for i in range(section_count):
            active = "active" if i == 0 else ""
            label = section_labels[i] if i < len(section_labels) else f"Section {i+1}"
            dots.append(f'<div class="nav-dot {active}" data-section="{i}" data-label="{label}"></div>')

        return f'''
        <nav class="nav-dots">
            {"".join(dots)}
        </nav>'''

    def _section_hero(self, insights: Any) -> str:
        """Generate hero section."""
        bm = insights.brand_metrics

        # Calculate ring percentages
        mention_pct = bm.mention_rate
        top3_pct = bm.featured_first_rate + bm.recommended_rate + bm.listed_rate
        featured_pct = bm.featured_first_rate

        # SVG circle calculations (radius 70, circumference ≈ 440)
        circumference = 440
        mention_offset = circumference * (1 - mention_pct / 100)
        top3_offset = circumference * (1 - top3_pct / 100)
        featured_offset = circumference * (1 - featured_pct / 100)

        return f'''
        <section class="section hero" id="section-0">
            <div class="hero-logo">{insights.brand_name[0].upper()}</div>
            <h1 class="hero-title">
                <span class="brand">{insights.brand_name}</span> AI Intelligence
            </h1>
            <p class="hero-subtitle">Answer Engine Optimization Analysis</p>

            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{datetime.now().strftime("%b %Y")}</div>
                    <div class="stat-label">Date</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{bm.total_queries}</div>
                    <div class="stat-label">Queries</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(insights.platform_metrics)}</div>
                    <div class="stat-label">Platforms</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{bm.total_responses}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(insights.segment_metrics)}</div>
                    <div class="stat-label">Segments</div>
                </div>
            </div>

            <div class="platform-filters">
                <button class="filter-btn active" data-platform="all">All Platforms</button>
                <button class="filter-btn" data-platform="chatgpt">ChatGPT</button>
                <button class="filter-btn" data-platform="claude">Claude</button>
                <button class="filter-btn" data-platform="perplexity">Perplexity</button>
                <button class="filter-btn" data-platform="gemini">Gemini</button>
                <button class="filter-btn" data-platform="meta_llama">Meta Llama</button>
            </div>

            <div class="score-ring-container">
                <div class="score-ring">
                    <svg viewBox="0 0 180 180">
                        <!-- Background rings -->
                        <circle class="ring ring-bg" cx="90" cy="90" r="70"/>
                        <circle class="ring ring-bg" cx="90" cy="90" r="55"/>
                        <circle class="ring ring-bg" cx="90" cy="90" r="40"/>
                        <!-- Data rings - start hidden, animate to target -->
                        <circle class="ring ring-mention" cx="90" cy="90" r="70"
                            stroke-dasharray="{circumference}"
                            stroke-dashoffset="{circumference}"
                            data-target="{mention_offset}"
                            data-circumference="{circumference}"/>
                        <circle class="ring ring-top" cx="90" cy="90" r="55"
                            stroke-dasharray="{circumference * 55/70}"
                            stroke-dashoffset="{circumference * 55/70}"
                            data-target="{circumference * 55/70 * (1 - top3_pct / 100)}"
                            data-circumference="{circumference * 55/70}"/>
                        <circle class="ring ring-featured" cx="90" cy="90" r="40"
                            stroke-dasharray="{circumference * 40/70}"
                            stroke-dashoffset="{circumference * 40/70}"
                            data-target="{circumference * 40/70 * (1 - featured_pct / 100)}"
                            data-circumference="{circumference * 40/70}"/>
                    </svg>
                    <div class="score-value">
                        <div class="number">{bm.visibility_score:.0f}</div>
                        <div class="label">AEO Score</div>
                    </div>
                </div>
                <div class="score-legend">
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #22d3ee;"></div>
                        <span class="legend-label">Mention Rate</span>
                        <span class="legend-value">{mention_pct:.1f}%</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #22c55e;"></div>
                        <span class="legend-label">Top-3 Position</span>
                        <span class="legend-value">{top3_pct:.1f}%</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: var(--brand-primary);"></div>
                        <span class="legend-label">Featured First</span>
                        <span class="legend-value">{featured_pct:.1f}%</span>
                    </div>
                </div>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Mention Rate</div>
                    <div class="kpi-value">{bm.mention_rate:.1f}%</div>
                    <div class="kpi-detail">{bm.mention_count} of {bm.total_responses} responses</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Featured First</div>
                    <div class="kpi-value">{bm.featured_first_rate:.1f}%</div>
                    <div class="kpi-detail">{bm.featured_first_count} top recommendations</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Prominence Score</div>
                    <div class="kpi-value">{bm.prominence_score:.1f}</div>
                    <div class="kpi-detail">Weighted position strength</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Strongest Segment</div>
                    <div class="kpi-value text">{self._get_strongest_segment(insights)}</div>
                    <div class="kpi-detail">Highest prominence</div>
                </div>
            </div>
        </section>'''

    def _get_strongest_segment(self, insights: Any) -> str:
        """Get the strongest performing segment."""
        best_segment = "N/A"
        best_score = 0

        for seg_type, metrics in insights.segment_metrics.items():
            if metrics and metrics[0].prominence_score > best_score:
                best_score = metrics[0].prominence_score
                best_segment = metrics[0].segment_value

        return best_segment

    def _section_executive_summary(self, insights: Any) -> str:
        """Generate executive summary section."""
        items = []

        for insight in insights.key_insights[:4]:
            items.append(f'<div class="exec-item">{insight}</div>')

        for opp in insights.opportunities[:2]:
            items.append(f'<div class="exec-item">{opp}</div>')

        return f'''
        <section class="section" id="section-1">
            <div class="exec-summary">
                <h3>Executive Summary</h3>
                {"".join(items)}
            </div>
        </section>'''

    def _section_competitive_position(self, insights: Any) -> str:
        """Generate competitive position section."""
        competitors = insights.discovered_competitors[:10]

        # Build table rows
        rows = []
        for i, comp in enumerate(competitors, 1):
            h2h = f"{comp.head_to_head_wins}W / {comp.head_to_head_losses}L"
            rows.append(f'''
                <tr>
                    <td class="competitor-rank">#{i}</td>
                    <td class="competitor-name">{comp.brand_name}</td>
                    <td>{comp.mention_count}</td>
                    <td>{comp.featured_count}</td>
                    <td>{comp.win_rate:.1f}%</td>
                    <td>{h2h}</td>
                </tr>''')

        return f'''
        <section class="section" id="section-2">
            <div class="section-label">Competitive Intelligence</div>
            <h2 class="section-title">Competitive Position</h2>
            <p class="section-subtitle">Competitors discovered organically from AI responses, not pre-specified.</p>

            <div class="charts-grid">
                <div class="chart-card">
                    <h4>Mention Count Ranking</h4>
                    <div class="chart-wrapper">
                        <canvas id="mentionChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h4>Featured Count Ranking</h4>
                    <div class="chart-wrapper">
                        <canvas id="featuredChart"></canvas>
                    </div>
                </div>
            </div>

            <div style="margin-top: 32px;">
                <table class="competitor-table">
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
                        {"".join(rows)}
                    </tbody>
                </table>
            </div>
        </section>'''

    def _section_category_performance(self, insights: Any) -> str:
        """Generate category performance section."""
        cards = []

        # Flatten all segments
        all_segments = []
        for seg_type, metrics in insights.segment_metrics.items():
            for m in metrics:
                all_segments.append((seg_type, m))

        # Sort by prominence
        all_segments.sort(key=lambda x: x[1].prominence_score, reverse=True)

        for seg_type, m in all_segments[:12]:
            # Determine badge
            if m.prominence_score >= 60:
                badge_class = "badge-leading"
                badge_text = "Leading"
            elif m.prominence_score >= 40:
                badge_class = "badge-competitive"
                badge_text = "Competitive"
            elif m.prominence_score >= 20:
                badge_class = "badge-developing"
                badge_text = "Developing"
            else:
                badge_class = "badge-opportunity"
                badge_text = "Opportunity"

            cards.append(f'''
                <div class="category-card">
                    <div class="category-header">
                        <span class="category-name">{m.segment_value}</span>
                        <span class="category-badge {badge_class}">{badge_text}</span>
                    </div>
                    <div class="category-query">"{seg_type.replace('_', ' ').title()}" segment</div>
                    <div class="category-metrics">
                        <div class="category-metric">
                            <div class="category-metric-value">{m.mention_rate:.1f}%</div>
                            <div class="category-metric-label">Mention</div>
                        </div>
                        <div class="category-metric">
                            <div class="category-metric-value">{m.featured_rate:.1f}%</div>
                            <div class="category-metric-label">Featured</div>
                        </div>
                        <div class="category-metric">
                            <div class="category-metric-value">{m.response_count}</div>
                            <div class="category-metric-label">Tests</div>
                        </div>
                    </div>
                    <div class="category-progress">
                        <div class="category-progress-fill" style="width: {min(m.prominence_score, 100)}%;"></div>
                    </div>
                    <div class="card-details">
                        <div class="card-details-content">
                            <div class="metric-definition">
                                <span class="metric-name">Mention Rate:</span> Percentage of queries where the brand appears anywhere in the response.
                            </div>
                            <div class="metric-definition">
                                <span class="metric-name">Featured Rate:</span> Percentage of queries where the brand is the #1 recommendation.
                            </div>
                            <div class="metric-definition">
                                <span class="metric-name">Prominence Score:</span> Weighted composite ({m.prominence_score:.0f}/100) factoring position, frequency, and citation quality.
                            </div>
                            <div class="metric-definition">
                                <span class="metric-name">Status:</span> <strong>{badge_text}</strong> — {"Market leader in this segment" if badge_text == "Leading" else "Strong competitive position" if badge_text == "Competitive" else "Emerging presence, room for growth" if badge_text == "Developing" else "Significant opportunity for improvement"}.
                            </div>
                        </div>
                    </div>
                </div>''')

        return f'''
        <section class="section" id="section-3">
            <div class="section-label">Segment Analysis</div>
            <h2 class="section-title">Category Performance</h2>
            <p class="section-subtitle">Performance breakdown by segment with status indicators.</p>

            <div class="platform-filters" style="margin-bottom: 24px;">
                <button class="filter-btn active">All Platforms</button>
                <button class="filter-btn">ChatGPT</button>
                <button class="filter-btn">Claude</button>
                <button class="filter-btn">Perplexity</button>
                <button class="filter-btn">Gemini</button>
                <button class="filter-btn">Meta Llama</button>
                <span style="margin-left: auto;"></span>
                <button class="filter-btn active">By Mention Rate</button>
                <button class="filter-btn">By Featured Rate</button>
                <button class="filter-btn">Alphabetical</button>
            </div>

            <div class="category-grid">
                {"".join(cards)}
            </div>
        </section>'''

    def _section_platform_comparison(self, insights: Any) -> str:
        """Generate platform comparison section."""
        platforms = sorted(insights.platform_metrics, key=lambda x: x.prominence_score, reverse=True)

        cards = []
        for i, p in enumerate(platforms):
            best_badge = '<span class="best-badge">Best</span>' if i == 0 else ""
            cards.append(f'''
                <div class="platform-card">
                    {best_badge}
                    <div class="platform-name">{p.platform.replace('_', ' ').title()}</div>
                    <div class="platform-value">{p.mention_rate:.1f}%</div>
                    <div class="platform-label">Mention Rate</div>
                    <div class="platform-detail">{p.response_count} tests · {p.featured_rate:.1f}% featured</div>
                </div>''')

        # Find variance
        if platforms:
            variance = platforms[0].prominence_score - platforms[-1].prominence_score
            variance_note = f"Platform Variance: Performance varies by {variance:.0f} percentage points between highest and lowest performing platforms."
        else:
            variance_note = ""

        return f'''
        <section class="section" id="section-4">
            <div class="section-label">Platform Analysis</div>
            <h2 class="section-title">Performance by AI Platform</h2>
            <p class="section-subtitle">{variance_note}</p>

            <div class="platform-grid">
                {"".join(cards)}
            </div>
        </section>'''

    def _section_position_analysis(self, insights: Any) -> str:
        """Generate position analysis section."""
        bm = insights.brand_metrics

        # Calculate position distribution
        total = bm.total_responses
        if total > 0:
            first_pct = bm.featured_first_count / total * 100
            second_pct = bm.recommended_count / total * 100
            third_pct = bm.listed_count / total * 100
            other_pct = bm.mentioned_only_count / total * 100
        else:
            first_pct = second_pct = third_pct = other_pct = 0

        # Win rate (when mentioned, how often featured first)
        mention_count = int(bm.mention_count) if bm.mention_count else 0
        featured_first_count = int(bm.featured_first_count) if bm.featured_first_count else 0
        if mention_count > 0:
            win_rate = featured_first_count / mention_count * 100
        else:
            win_rate = 0

        top3_rate = first_pct + second_pct + third_pct

        return f'''
        <section class="section" id="section-5">
            <div class="section-label">Position Analysis</div>
            <h2 class="section-title">Position Distribution</h2>
            <p class="section-subtitle">When {insights.brand_name} is mentioned, where does it appear in the response?</p>

            <div class="charts-grid">
                <div class="chart-card">
                    <h4>Position Distribution</h4>
                    <div style="margin-top: 20px;">
                        <div style="display: flex; height: 32px; border-radius: 8px; overflow: hidden; margin-bottom: 16px;">
                            <div style="width: {first_pct}%; background: #22c55e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">{first_pct:.1f}%</div>
                            <div style="width: {second_pct}%; background: #84cc16; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">{second_pct:.1f}%</div>
                            <div style="width: {third_pct}%; background: #eab308; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">{third_pct:.1f}%</div>
                            <div style="width: {other_pct}%; background: #f97316; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">{other_pct:.1f}%</div>
                        </div>
                        <div style="display: flex; gap: 24px; justify-content: center;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #22c55e; border-radius: 2px;"></div>
                                <span style="font-size: 13px; color: var(--text-secondary);">1st</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #84cc16; border-radius: 2px;"></div>
                                <span style="font-size: 13px; color: var(--text-secondary);">2nd</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #eab308; border-radius: 2px;"></div>
                                <span style="font-size: 13px; color: var(--text-secondary);">3rd</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #f97316; border-radius: 2px;"></div>
                                <span style="font-size: 13px; color: var(--text-secondary);">4th+</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="chart-card">
                    <h4>Conversion Metrics</h4>
                    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Click each metric to see definition.</p>
                    <div style="display: flex; gap: 40px;">
                        <div style="text-align: center;">
                            <div style="font-size: 42px; font-weight: 600; color: var(--brand-primary);">{win_rate:.1f}%</div>
                            <div style="font-size: 13px; color: var(--text-secondary);">Visibility → Win Rate</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 42px; font-weight: 600; color: #22c55e;">{top3_rate:.1f}%</div>
                            <div style="font-size: 13px; color: var(--text-secondary);">Top-3 Placement</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>'''

    def _section_content_authority(self, insights: Any) -> str:
        """Generate content authority analysis section."""
        cm = insights.citation_metrics

        # Build competitor conversion cards
        comp_cards = []
        for comp in insights.discovered_competitors[:10]:
            # Ensure numeric types
            mention_count = int(comp.mention_count) if comp.mention_count else 0
            featured_count = int(comp.featured_count) if comp.featured_count else 0

            if mention_count > 0:
                conv_rate = featured_count / mention_count * 100
            else:
                conv_rate = 0

            comp_cards.append(f'''
                <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center;">
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">{comp.brand_name}</div>
                    <div style="font-size: 24px; font-weight: 600; color: var(--text-primary);">{conv_rate:.1f}%</div>
                    <div style="font-size: 11px; color: var(--text-muted);">{featured_count}/{mention_count}</div>
                </div>''')

        return f'''
        <section class="section" id="section-6">
            <div class="section-label">Content Authority Analysis</div>
            <h2 class="section-title">Content Conversion Rate</h2>

            <div class="exec-summary" style="margin-bottom: 24px;">
                <h3>Key Insight</h3>
                <div class="exec-item">A citation indicates a source the AI <em>consulted</em>, not necessarily a source that drove the recommendation. When a brand's website is cited but that brand doesn't win, it reveals a gap between brand awareness and content authority.</div>
                <div class="exec-item"><strong>Content Conversion Rate</strong> = When a brand's owned domain is cited in a response, how often is that brand featured as the #1 recommendation?</div>
            </div>

            <div style="margin-bottom: 16px;">
                <h4 style="font-size: 16px; margin-bottom: 16px;">Content Conversion Rate by Brand</h4>
                <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
                    {insights.brand_name}'s conversion rate: <strong>{cm.content_conversion_rate:.1f}%</strong>
                    ({cm.wins_when_cited} wins when cited {cm.times_brand_cited} times)
                </p>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px;">
                {"".join(comp_cards[:10])}
            </div>
        </section>'''

    def _section_citation_analysis(self, insights: Any) -> str:
        """Generate citation analysis section."""
        cm = insights.citation_metrics

        # Classify domains into tiers
        editorial_domains = []
        retail_domains = []
        owned_domains = []
        social_domains = []
        other_domains = []

        brand_lower = insights.brand_name.lower().replace(' ', '')

        for domain, count in cm.top_domains:
            total = cm.total_citations
            pct = count / total * 100 if total > 0 else 0
            row_html = f'''
                <div class="citation-row">
                    <div class="citation-domain">{domain}</div>
                    <div class="citation-bar">
                        <div class="citation-bar-fill" style="width: {min(pct * 2, 100)}%;"></div>
                    </div>
                    <div class="citation-stats">
                        <span class="citation-count">{count}</span> citations
                        <span class="citation-percent">{pct:.1f}%</span>
                    </div>
                </div>'''

            # Classify
            if brand_lower in domain.lower():
                owned_domains.append(row_html)
            elif any(x in domain for x in ['forbes', 'gq', 'esquire', 'menshealth', 'womenshealth', 'runnersworld', 'self', 'vogue', 'nytimes', 'wsj', 'cnn', 'businessinsider', 'wired']):
                editorial_domains.append(row_html)
            elif any(x in domain for x in ['nordstrom', 'rei', 'amazon', 'zappos', 'dickssportinggoods', 'target', 'walmart', 'macys']):
                retail_domains.append(row_html)
            elif any(x in domain for x in ['reddit', 'youtube', 'instagram', 'tiktok', 'twitter', 'facebook']):
                social_domains.append(row_html)
            else:
                other_domains.append(row_html)

        # All domains for the default view
        all_rows = []
        for domain, count in cm.top_domains[:10]:
            total = cm.total_citations
            pct = count / total * 100 if total > 0 else 0
            all_rows.append(f'''
                <div class="citation-row">
                    <div class="citation-domain">{domain}</div>
                    <div class="citation-bar">
                        <div class="citation-bar-fill" style="width: {min(pct * 2, 100)}%;"></div>
                    </div>
                    <div class="citation-stats">
                        <span class="citation-count">{count}</span> citations
                        <span class="citation-percent">{pct:.1f}%</span>
                    </div>
                </div>''')

        return f'''
        <section class="section" id="section-7">
            <div class="section-label">Earned Media Analysis</div>
            <h2 class="section-title">Citation Analysis</h2>
            <p class="section-subtitle">Sources cited by AI platforms. Higher {insights.brand_name} share indicates stronger presence.</p>

            <div class="citation-tabs">
                <div class="citation-tab active" data-tab="all">All Sources</div>
                <div class="citation-tab" data-tab="editorial">Editorial ({len(editorial_domains)})</div>
                <div class="citation-tab" data-tab="retail">Retail ({len(retail_domains)})</div>
                <div class="citation-tab" data-tab="owned">Owned ({len(owned_domains)})</div>
                <div class="citation-tab" data-tab="social">Social ({len(social_domains)})</div>
            </div>

            <div class="citation-content" data-content="all" style="display: block;">
                <div class="citation-list">
                    {"".join(all_rows) if all_rows else '<p style="color: var(--text-muted);">No citation data available.</p>'}
                </div>
            </div>
            <div class="citation-content" data-content="editorial" style="display: none;">
                <div class="citation-list">
                    {"".join(editorial_domains[:10]) if editorial_domains else '<p style="color: var(--text-muted);">No editorial citations found.</p>'}
                </div>
            </div>
            <div class="citation-content" data-content="retail" style="display: none;">
                <div class="citation-list">
                    {"".join(retail_domains[:10]) if retail_domains else '<p style="color: var(--text-muted);">No retail citations found.</p>'}
                </div>
            </div>
            <div class="citation-content" data-content="owned" style="display: none;">
                <div class="citation-list">
                    {"".join(owned_domains[:10]) if owned_domains else '<p style="color: var(--text-muted);">No owned media citations found.</p>'}
                </div>
            </div>
            <div class="citation-content" data-content="social" style="display: none;">
                <div class="citation-list">
                    {"".join(social_domains[:10]) if social_domains else '<p style="color: var(--text-muted);">No social media citations found.</p>'}
                </div>
            </div>

            <div style="margin-top: 32px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px;">
                <div class="kpi-card">
                    <div class="kpi-label">Total Citations</div>
                    <div class="kpi-value">{cm.total_citations}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Owned</div>
                    <div class="kpi-value">{cm.owned_citations}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Editorial</div>
                    <div class="kpi-value">{cm.editorial_citations}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Retail</div>
                    <div class="kpi-value">{cm.retail_citations}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Social</div>
                    <div class="kpi-value">{cm.social_citations}</div>
                </div>
            </div>
        </section>'''

    def _section_query_appendix(self, insights: Any) -> str:
        """Generate query appendix section."""
        # Build table rows from query_data if available
        table_rows = []
        query_data = getattr(insights, 'query_data', [])

        if query_data:
            for row in query_data[:100]:  # Limit to 100 rows for performance
                query_text = row.get('query_text', '')[:50] + ('...' if len(row.get('query_text', '')) > 50 else '')
                platform = row.get('platform', '')
                mentioned = row.get('new_focal_brand_found', False)
                prominence = row.get('new_prominence', 'not_mentioned')
                position = row.get('new_focal_position', '')

                mentioned_class = 'yes' if mentioned else 'no'
                mentioned_text = 'Yes' if mentioned else 'No'
                featured = prominence == 'featured_first'
                featured_class = 'yes' if featured else 'no'
                featured_text = 'Yes' if featured else 'No'

                table_rows.append(f'''
                    <tr data-platform="{platform}" data-mentioned="{str(mentioned).lower()}" data-featured="{str(featured).lower()}">
                        <td>{query_text}</td>
                        <td>{prominence.replace('_', ' ').title()}</td>
                        <td>{platform.replace('_', ' ').title()}</td>
                        <td class="{mentioned_class}">{mentioned_text}</td>
                        <td>{position if position else '-'}</td>
                        <td class="{featured_class}">{featured_text}</td>
                    </tr>''')

        if not table_rows:
            table_rows = ['''
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: var(--text-muted);">
                        No query data available. Run analysis with CSV data to populate this section.
                    </td>
                </tr>''']

        return f'''
        <section class="section" id="section-8">
            <div class="section-label">Data Explorer</div>
            <h2 class="section-title">Query Appendix</h2>

            <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; align-items: center;">
                <div class="appendix-filters" style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="filter-btn active" data-filter-platform="all">All Platforms</button>
                    <button class="filter-btn" data-filter-platform="chatgpt">ChatGPT</button>
                    <button class="filter-btn" data-filter-platform="claude">Claude</button>
                    <button class="filter-btn" data-filter-platform="perplexity">Perplexity</button>
                    <button class="filter-btn" data-filter-platform="gemini">Gemini</button>
                    <button class="filter-btn" data-filter-platform="meta_llama">Meta Llama</button>
                </div>
                <div style="margin-left: auto; display: flex; gap: 12px;">
                    <div>
                        <label style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); display: block; margin-bottom: 4px;">Mentioned</label>
                        <select id="filter-mentioned" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 12px; color: var(--text-primary); font-size: 13px;">
                            <option value="all">All</option>
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); display: block; margin-bottom: 4px;">Featured</label>
                        <select id="filter-featured" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 12px; color: var(--text-primary); font-size: 13px;">
                            <option value="all">All</option>
                            <option value="true">Yes</option>
                            <option value="false">No</option>
                        </select>
                    </div>
                </div>
            </div>

            <p id="results-count" style="color: var(--text-muted); margin-bottom: 16px;">Showing {len(query_data) if query_data else 0} results</p>

            <div class="data-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Query</th>
                            <th>Prominence</th>
                            <th>Platform</th>
                            <th>Mentioned</th>
                            <th>Position</th>
                            <th>Featured</th>
                        </tr>
                    </thead>
                    <tbody id="query-table-body">
                        {"".join(table_rows)}
                    </tbody>
                </table>
            </div>
        </section>'''

    def _get_scripts(self, insights: Any) -> str:
        """Get JavaScript for interactivity."""

        # Prepare chart data (ensure numeric types)
        competitors = insights.discovered_competitors[:8]
        comp_names = [c.brand_name for c in competitors]
        comp_mentions = [int(c.mention_count) if c.mention_count else 0 for c in competitors]
        comp_featured = [int(c.featured_count) if c.featured_count else 0 for c in competitors]

        # Add brand to the data
        bm = insights.brand_metrics
        all_names = [insights.brand_name] + comp_names
        all_mentions = [int(bm.mention_count) if bm.mention_count else 0] + comp_mentions
        all_featured = [int(bm.featured_first_count) if bm.featured_first_count else 0] + comp_featured

        return f'''
        // Navigation dots
        const navDots = document.querySelectorAll('.nav-dot');
        const sections = document.querySelectorAll('.section');

        // Intersection Observer for nav dots
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    const index = Array.from(sections).indexOf(entry.target);
                    navDots.forEach((dot, i) => {{
                        dot.classList.toggle('active', i === index);
                    }});
                }}
            }});
        }}, {{ threshold: 0.5 }});

        sections.forEach(section => observer.observe(section));

        // Click navigation
        navDots.forEach((dot, index) => {{
            dot.addEventListener('click', () => {{
                sections[index].scrollIntoView({{ behavior: 'smooth' }});
            }});
        }});

        // Platform filter buttons
        document.querySelectorAll('.platform-filters').forEach(container => {{
            container.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    container.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                }});
            }});
        }});

        // Citation tabs with content switching
        document.querySelectorAll('.citation-tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                const targetTab = tab.getAttribute('data-tab');
                // Update active tab
                document.querySelectorAll('.citation-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                // Show corresponding content
                document.querySelectorAll('.citation-content').forEach(content => {{
                    content.style.display = content.getAttribute('data-content') === targetTab ? 'block' : 'none';
                }});
            }});
        }});

        // Query appendix filtering
        function filterQueryTable() {{
            const platformFilter = document.querySelector('.appendix-filters .filter-btn.active')?.getAttribute('data-filter-platform') || 'all';
            const mentionedFilter = document.getElementById('filter-mentioned')?.value || 'all';
            const featuredFilter = document.getElementById('filter-featured')?.value || 'all';

            const rows = document.querySelectorAll('#query-table-body tr[data-platform]');
            let visibleCount = 0;

            rows.forEach(row => {{
                const platform = row.getAttribute('data-platform');
                const mentioned = row.getAttribute('data-mentioned');
                const featured = row.getAttribute('data-featured');

                const platformMatch = platformFilter === 'all' || platform === platformFilter;
                const mentionedMatch = mentionedFilter === 'all' || mentioned === mentionedFilter;
                const featuredMatch = featuredFilter === 'all' || featured === featuredFilter;

                if (platformMatch && mentionedMatch && featuredMatch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            const countEl = document.getElementById('results-count');
            if (countEl) {{
                countEl.textContent = `Showing ${{visibleCount}} results`;
            }}
        }}

        // Appendix platform filter buttons
        document.querySelectorAll('.appendix-filters .filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.appendix-filters .filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filterQueryTable();
            }});
        }});

        // Appendix dropdown filters
        document.getElementById('filter-mentioned')?.addEventListener('change', filterQueryTable);
        document.getElementById('filter-featured')?.addEventListener('change', filterQueryTable);

        // Score ring animation on scroll
        const scoreRing = document.querySelector('.score-ring');
        if (scoreRing) {{
            const ringObserver = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting && !entry.target.classList.contains('animated')) {{
                        entry.target.classList.add('animated');
                        animateScoreRings();
                    }}
                }});
            }}, {{ threshold: 0.3 }});
            ringObserver.observe(scoreRing);
        }}

        function animateScoreRings() {{
            document.querySelectorAll('.score-ring .ring:not(.ring-bg)').forEach(ring => {{
                const target = parseFloat(ring.getAttribute('data-target') || ring.style.strokeDashoffset);
                const circumference = parseFloat(ring.getAttribute('data-circumference') || 377);
                // Animate from full offset to target
                ring.style.strokeDashoffset = circumference;
                setTimeout(() => {{
                    ring.style.strokeDashoffset = target;
                }}, 100);
            }});
        }}

        // Expandable category cards
        document.querySelectorAll('.category-card').forEach(card => {{
            card.addEventListener('click', (e) => {{
                // Toggle expanded state
                const wasExpanded = card.classList.contains('expanded');
                // Close all other cards
                document.querySelectorAll('.category-card.expanded').forEach(c => {{
                    if (c !== card) c.classList.remove('expanded');
                }});
                // Toggle this card
                card.classList.toggle('expanded', !wasExpanded);
            }});
        }});

        // Entrance animations for elements
        const animateObserver = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, {{ threshold: 0.1 }});

        document.querySelectorAll('.animate-on-scroll').forEach(el => {{
            animateObserver.observe(el);
        }});

        // Animate category cards on load
        document.querySelectorAll('.category-card').forEach((card, i) => {{
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {{
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }}, 100 + (i * 80));
        }});

        // Animate KPI cards
        document.querySelectorAll('.kpi-card').forEach((card, i) => {{
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {{
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }}, 200 + (i * 100));
        }});

        // Animate platform cards
        document.querySelectorAll('.platform-card').forEach((card, i) => {{
            card.style.opacity = '0';
            card.style.transform = 'translateY(15px)';
            setTimeout(() => {{
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }}, 300 + (i * 100));
        }});

        // Charts
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {{
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{
                    beginAtZero: true,
                    grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                    ticks: {{ color: '#666' }}
                }},
                y: {{
                    grid: {{ display: false }},
                    ticks: {{ color: '#a0a0a0' }}
                }}
            }}
        }};

        // Mention Chart
        new Chart(document.getElementById('mentionChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(all_names)},
                datasets: [{{
                    data: {json.dumps(all_mentions)},
                    backgroundColor: {json.dumps([self.BRAND_COLOR] + ['rgba(255,255,255,0.3)'] * len(comp_names))},
                    borderRadius: 4
                }}]
            }},
            options: chartOptions
        }});

        // Featured Chart
        new Chart(document.getElementById('featuredChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(all_names)},
                datasets: [{{
                    data: {json.dumps(all_featured)},
                    backgroundColor: {json.dumps([self.BRAND_COLOR] + ['rgba(255,255,255,0.3)'] * len(comp_names))},
                    borderRadius: 4
                }}]
            }},
            options: chartOptions
        }});
        '''

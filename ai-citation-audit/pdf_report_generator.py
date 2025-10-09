#!/usr/bin/env python3
"""
PDF Report Generator for AI Citation Audit System

Generates professional PDF reports that mirror the HTML report structure
with executive summaries, score dashboards, charts, and detailed citation analysis.
"""

import os
import datetime
from urllib.parse import urlparse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class PDFReportGenerator:
    """Professional PDF report generator for AI Citation Audit results"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Define custom paragraph styles for consistent formatting"""

        # Custom styles based on HoneyBaked Ham color scheme
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#8B2635'),
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='BrandSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#D2691E'),
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#8B2635'),
            borderWidth=0,
            borderColor=colors.HexColor('#D2691E'),
            borderPadding=5
        ))

        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=10,
            leftIndent=20,
            borderWidth=1,
            borderColor=colors.HexColor('#D2691E'),
            borderPadding=15,
            backgroundColor=colors.HexColor('#FFF8E7')
        ))

        self.styles.add(ParagraphStyle(
            name='KeyMetric',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))

        self.styles.add(ParagraphStyle(
            name='RecommendationHigh',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            leftIndent=10,
            backgroundColor=colors.HexColor('#FED4D4'),
            borderWidth=1,
            borderColor=colors.HexColor('#8B2635'),
            borderPadding=8
        ))

        self.styles.add(ParagraphStyle(
            name='RecommendationMedium',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            leftIndent=10,
            backgroundColor=colors.HexColor('#FFE4B5'),
            borderWidth=1,
            borderColor=colors.HexColor('#B8860B'),
            borderPadding=8
        ))

    def generate_report(self, brand_name, audit_data, output_path):
        """
        Generate a complete PDF report from audit data

        Args:
            brand_name: The brand being audited
            audit_data: Dictionary containing all audit results
            output_path: Full path where PDF should be saved
        """

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build the report content
        story = []

        # Header section
        story.extend(self._build_header(brand_name, audit_data))

        # Executive Summary
        story.extend(self._build_executive_summary(audit_data))

        # Score Dashboard
        story.extend(self._build_score_dashboard(audit_data))

        # Platform Performance
        story.extend(self._build_platform_performance(audit_data))

        # Citation Quality Analysis
        story.extend(self._build_citation_quality(audit_data))

        # Competitive Analysis
        story.extend(self._build_competitive_analysis(audit_data))

        # Key Findings
        story.extend(self._build_key_findings(audit_data))

        # Recommendations
        story.extend(self._build_recommendations(audit_data))

        # Methodology
        story.extend(self._build_methodology())

        # Appendix - detailed citation data
        story.extend(self._build_citation_appendix(audit_data))

        # Build the PDF
        doc.build(story)

        return output_path

    def _build_header(self, brand_name, audit_data):
        """Build the report header section"""
        story = []

        # Title
        story.append(Paragraph("AI Citation Visibility Analysis", self.styles['CustomTitle']))
        story.append(Paragraph(brand_name, self.styles['BrandSubtitle']))

        # Date and metadata
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Analysis Date: {current_date}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Horizontal rule
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#D2691E')))
        story.append(Spacer(1, 20))

        return story

    def _build_executive_summary(self, audit_data):
        """Build executive summary section"""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Extract key metrics for summary
        total_citations = audit_data.get('total_citations', 0)
        overall_score = audit_data.get('overall_score', 0)
        active_platforms = len([p for p in audit_data.get('platforms', {}).values() if p.get('citations', 0) > 0])

        summary_text = f"""
        <b>{audit_data.get('brand_name', 'Brand')} demonstrates {'strong' if overall_score > 65 else 'moderate' if overall_score > 50 else 'developing'} AI visibility performance with {total_citations} total citations across {active_platforms} AI platforms, achieving a {overall_score}/100 visibility score.</b>
        <br/><br/>
        The comprehensive analysis reveals {audit_data.get('top_platform', 'Perplexity')} as the leading citation source, with significant opportunities in premium food media and competitive positioning. The enhanced multi-strategy extraction system provides robust coverage across editorial, industry trade, and food media sources.
        """

        story.append(Paragraph(summary_text, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 20))

        return story

    def _build_score_dashboard(self, audit_data):
        """Build the score dashboard with key metrics"""
        story = []

        story.append(Paragraph("Performance Dashboard", self.styles['SectionHeader']))

        # Create score table
        scores = audit_data.get('scores', {})

        data = [
            ['Metric', 'Score', 'Performance Level'],
            ['Overall AI Visibility', f"{scores.get('overall', 0)}/100", self._get_performance_level(scores.get('overall', 0))],
            ['Presence', f"{scores.get('presence', 0)}", self._get_component_description('presence')],
            ['Prominence', f"{scores.get('prominence', 0)}", self._get_component_description('prominence')],
            ['Citation Quality', f"{scores.get('quality', 0)}", self._get_component_description('quality')],
            ['Competitive Delta', f"{scores.get('competitive_delta', 0)}", self._get_component_description('competitive')],
            ['Freshness', f"{scores.get('freshness', 50)}", self._get_component_description('freshness')]
        ]

        table = Table(data, colWidths=[2*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B2635')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        story.append(table)
        story.append(Spacer(1, 20))

        return story

    def _build_platform_performance(self, audit_data):
        """Build platform performance chart and analysis"""
        story = []

        story.append(Paragraph("Citation Performance by AI Platform", self.styles['SectionHeader']))

        # Platform performance table
        platforms = audit_data.get('platforms', {})

        data = [['Platform', 'Citations', 'Prompts Run', 'Success Rate']]

        for platform_name, platform_data in platforms.items():
            citations = platform_data.get('citations', 0)
            prompts = platform_data.get('prompts_run', 0)
            success_rate = f"{(citations/prompts*100):.1f}%" if prompts > 0 else "N/A"
            data.append([platform_name.title(), str(citations), str(prompts), success_rate])

        table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D2691E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(table)
        story.append(Spacer(1, 15))

        return story

    def _build_citation_quality(self, audit_data):
        """Build citation quality distribution analysis"""
        story = []

        story.append(Paragraph("Citation Source Quality Distribution", self.styles['SectionHeader']))

        # Citation quality breakdown
        quality_data = audit_data.get('citation_quality', {})

        data = [['Source Tier', 'Citations', 'Examples', 'Weight']]

        tiers = [
            ('Editorial Tier-1', quality_data.get('editorial_tier1', 0), 'Forbes, Reuters, Bloomberg', '1.0x'),
            ('Food Media Tier-1', quality_data.get('food_tier1', 0), 'Food & Wine, Bon Appétit', '1.0x'),
            ('Food Media Tier-2', quality_data.get('food_tier2', 0), 'Delish, The Kitchn', '0.8x'),
            ('Industry Trade', quality_data.get('industry_trade', 0), 'QSR Magazine, Nation\'s Restaurant News', '0.7x'),
            ('General Editorial', quality_data.get('editorial', 0), 'Business Insider, MarketWatch', '0.7x'),
            ('PR/Corporate', quality_data.get('pr', 0), 'PR Newswire, Business Wire', '0.3x')
        ]

        for tier_name, count, examples, weight in tiers:
            data.append([tier_name, str(count), examples, weight])

        table = Table(data, colWidths=[1.8*inch, 0.8*inch, 2.5*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B2635')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        story.append(table)
        story.append(Spacer(1, 15))

        return story

    def _build_competitive_analysis(self, audit_data):
        """Build competitive intelligence analysis"""
        story = []

        story.append(Paragraph("Competitive Intelligence Analysis", self.styles['SectionHeader']))

        competitors = audit_data.get('competitors', [])
        if competitors:
            data = [['Competitor', 'Market Segment', 'AI Citations', 'Threat Level']]

            for competitor in competitors:
                threat_level = competitor.get('threat_level', 'Unknown')
                data.append([
                    competitor.get('name', ''),
                    competitor.get('segment', ''),
                    'Tracked' if competitor.get('citations', 0) > 0 else 'Monitored',
                    threat_level.title()
                ])

            table = Table(data, colWidths=[1.5*inch, 1.3*inch, 1.2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D2691E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            story.append(table)
        else:
            story.append(Paragraph("No competitive analysis data available.", self.styles['Normal']))

        story.append(Spacer(1, 15))

        return story

    def _build_key_findings(self, audit_data):
        """Build key findings section"""
        story = []

        story.append(Paragraph("Key Findings", self.styles['SectionHeader']))

        # Extract key findings from audit data
        strengths = audit_data.get('strengths', [
            "Strong industry trade media presence",
            "Established brand recognition in AI responses",
            "Quality source citations when mentioned"
        ])

        opportunities = audit_data.get('opportunities', [
            "Limited premium food media coverage",
            "Opportunity to dominate category-specific queries",
            "Potential for enhanced competitive positioning"
        ])

        # Strengths
        story.append(Paragraph("<b>Strengths:</b>", self.styles['Heading3']))
        for strength in strengths:
            story.append(Paragraph(f"• {strength}", self.styles['Normal']))
        story.append(Spacer(1, 10))

        # Opportunities
        story.append(Paragraph("<b>Opportunities:</b>", self.styles['Heading3']))
        for opportunity in opportunities:
            story.append(Paragraph(f"• {opportunity}", self.styles['Normal']))
        story.append(Spacer(1, 15))

        return story

    def _build_recommendations(self, audit_data):
        """Build strategic recommendations section"""
        story = []

        story.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))

        recommendations = [
            {
                'title': 'Amplify Premium Food Media Presence',
                'priority': 'high',
                'description': 'Target tier-1 food publications with artisanal process stories and heritage content.'
            },
            {
                'title': 'Own Category-Specific Queries',
                'priority': 'high',
                'description': 'Create definitive content for spiral-cut ham and holiday meat categories.'
            },
            {
                'title': 'Enhance Competitive Positioning',
                'priority': 'medium',
                'description': 'Develop content that directly addresses value propositions vs competitors.'
            }
        ]

        for i, rec in enumerate(recommendations, 1):
            priority_style = 'RecommendationHigh' if rec['priority'] == 'high' else 'RecommendationMedium'

            rec_text = f"<b>{i}. {rec['title']}</b> [{rec['priority'].upper()} PRIORITY]<br/>{rec['description']}"
            story.append(Paragraph(rec_text, self.styles[priority_style]))
            story.append(Spacer(1, 10))

        return story

    def _build_methodology(self):
        """Build scoring methodology section"""
        story = []

        story.append(PageBreak())
        story.append(Paragraph("AI Visibility Scoring Methodology", self.styles['SectionHeader']))

        methodology_text = """
        <b>Score Components & Weights:</b><br/>
        • Presence (35%): Frequency of brand mentions across all queries<br/>
        • Prominence (20%): Position and context quality of citations<br/>
        • Citation Quality (20%): Authority of sources (Tier-1, Food Media, etc.)<br/>
        • Competitive Delta (15%): Brand citations vs. competitor citations<br/>
        • Freshness (10%): Recency of cited content (< 6 months)<br/><br/>

        <b>Performance Scale:</b><br/>
        • 80-100: Excellent - Dominant AI visibility, category leader<br/>
        • 65-79: Strong - Above average, competitive positioning<br/>
        • 50-64: Moderate - Average visibility, improvement needed<br/>
        • 35-49: Weak - Below average, significant gaps<br/>
        • 0-34: Critical - Minimal visibility, urgent action needed<br/>
        """

        story.append(Paragraph(methodology_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

        return story

    def _build_citation_appendix(self, audit_data):
        """Build detailed citation data appendix"""
        story = []

        story.append(Paragraph("Appendix: Citation Data", self.styles['SectionHeader']))

        # Detailed citation table (limited to prevent overly long reports)
        citations = audit_data.get('all_citations', [])[:50]  # Limit to first 50

        if citations:
            data = [['Platform', 'Domain', 'Classification', 'URL']]

            for citation in citations:
                # Truncate long URLs for readability
                url = citation.get('url', '')
                if len(url) > 60:
                    url = url[:57] + '...'

                data.append([
                    citation.get('platform', '').title(),
                    citation.get('domain', ''),
                    citation.get('classification', 'editorial'),
                    url
                ])

            table = Table(data, colWidths=[1*inch, 1.5*inch, 1*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B2635')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            story.append(table)

            if len(audit_data.get('all_citations', [])) > 50:
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"<i>Showing first 50 of {len(audit_data.get('all_citations', []))} total citations. Complete data available in CSV export.</i>", self.styles['Normal']))

        return story

    def _get_performance_level(self, score):
        """Convert numeric score to performance level description"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Strong"
        elif score >= 50:
            return "Moderate"
        elif score >= 35:
            return "Weak"
        else:
            return "Critical"

    def _get_component_description(self, component):
        """Get description for score components"""
        descriptions = {
            'presence': 'Query mention frequency',
            'prominence': 'Citation context quality',
            'quality': 'Source authority level',
            'competitive': 'vs competitor mentions',
            'freshness': 'Recent content ratio'
        }
        return descriptions.get(component, 'Performance metric')


def generate_pdf_report(brand_name, audit_data, output_dir):
    """
    Convenience function to generate a PDF report

    Args:
        brand_name: Brand name for the report
        audit_data: Complete audit results dictionary
        output_dir: Directory to save the PDF report

    Returns:
        Path to generated PDF file
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{brand_name.replace(' ', '_')}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)

    # Generate the report
    generator = PDFReportGenerator()
    return generator.generate_report(brand_name, audit_data, output_path)


# Example usage and testing
if __name__ == "__main__":
    # Sample data for testing
    sample_data = {
        'brand_name': 'HoneyBaked Ham',
        'total_citations': 148,
        'overall_score': 57.5,
        'scores': {
            'overall': 57.5,
            'presence': 50.0,
            'prominence': 49.8,
            'quality': 69.2,
            'competitive_delta': 75.0,
            'freshness': 50.0
        },
        'platforms': {
            'perplexity': {'citations': 66, 'prompts_run': 6},
            'chatgpt': {'citations': 45, 'prompts_run': 6},
            'claude': {'citations': 37, 'prompts_run': 6}
        },
        'citation_quality': {
            'editorial_tier1': 8,
            'food_tier1': 2,
            'food_tier2': 2,
            'industry_trade': 12,
            'editorial': 114,
            'pr': 10
        },
        'competitors': [
            {'name': 'Smithfield Foods', 'segment': 'Mass Market', 'threat_level': 'high'},
            {'name': 'Butterball', 'segment': 'Mass Premium', 'threat_level': 'medium'}
        ],
        'all_citations': []  # Would contain actual citation data
    }

    # Generate test report
    output_path = generate_pdf_report('HoneyBaked Ham', sample_data, './output')
    print(f"Test PDF report generated: {output_path}")
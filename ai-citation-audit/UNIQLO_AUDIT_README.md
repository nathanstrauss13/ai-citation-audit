# UNIQLO Comprehensive PR Visibility Audit

## Overview

The UNIQLO audit script provides a comprehensive analysis of UNIQLO's AI citation presence compared to fast fashion competitors, with a specific focus on sustainability positioning and strategic PR recommendations.

## Features

- **Comprehensive Competitive Analysis**: Compares UNIQLO against H&M, Zara, Gap, Shein, Patagonia, and Everlane
- **Sustainability Focus**: Specialized prompts and analysis for environmental positioning
- **Strategic Recommendations**: Data-driven PR recommendations based on actual audit results
- **Multi-Platform Coverage**: Leverages multiple AI platforms (Perplexity, ChatGPT, Claude, Gemini)
- **Detailed Reporting**: JSON and CSV exports for further analysis

## Quick Start

### Prerequisites

1. **Environment Setup**: Ensure you have the required API keys in your environment:
   ```bash
   export PERPLEXITY_API_KEY="your_key_here"
   export OPENAI_API_KEY="your_key_here"        # Optional but recommended
   export ANTHROPIC_API_KEY="your_key_here"     # Optional but recommended
   export GEMINI_API_KEY="your_key_here"        # Optional but recommended
   ```

2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Audit

#### Method 1: Direct Execution
```bash
python3 uniqlo_audit.py
```

#### Method 2: Import and Run
```python
from uniqlo_audit import run_uniqlo_comprehensive_audit

# Execute the audit
results = run_uniqlo_comprehensive_audit()
```

## Audit Configuration

The audit is pre-configured with:

### Competitors Analyzed
- **H&M**: Direct sustainability competitor
- **Zara**: Fast fashion leader
- **Gap**: American basics competitor
- **Shein**: Ultra-fast fashion threat
- **Patagonia**: Sustainability benchmark
- **Everlane**: Transparency competitor

### Analysis Strategies
- Competitive positioning
- Sustainability focus
- Category dominance
- Media presence
- Innovation coverage
- Purchase journey analysis
- Brand sentiment
- Customer experience

### Custom Prompts (40+ specialized queries)

#### Sustainability Focused
- "Which fast fashion brands are most sustainable 2025?"
- "UNIQLO vs H&M sustainability comparison"
- "UNIQLO recycling program and circular fashion"
- "Fast fashion brands with best labor practices"

#### Competitive Positioning
- "UNIQLO vs Zara vs H&M quality comparison 2025"
- "Is UNIQLO better quality than Shein?"
- "Best affordable basics brands globally"

#### UNIQLO Differentiation
- "UNIQLO LifeWear philosophy explained"
- "UNIQLO Heattech vs competitors technology"
- "Japanese minimalist fashion brands"

#### Market Perception
- "Why do millennials shop at UNIQLO?"
- "Is UNIQLO considered fast fashion or quality basics?"
- "Best value clothing brands for professionals"

## Output Analysis

### Visibility Scores
- **Overall Score**: Composite visibility rating (0-100)
- **Presence**: How often UNIQLO appears in AI responses
- **Prominence**: Position and emphasis in responses
- **Quality**: Authority of citing sources
- **Competitive Delta**: Performance vs competitors

### Strategic Insights

#### PR Recommendations
The audit generates data-driven recommendations such as:
1. **Increase Fashion Media Authority** - Target tier-1 fashion publications
2. **Differentiate from Ultra-Fast Fashion** - Distance from Shein association
3. **Strengthen Competitive Position** - Address competitor dominance
4. **Improve Source Authority** - Target tier-1 business media
5. **Amplify Sustainability Credentials** - Increase eco-media presence

#### Sustainability Analysis
Specialized insights including:
- Sustainability media presence analysis
- Competitor co-citation patterns
- Environmental positioning opportunities
- Technology vs sustainability narrative balance

### Export Files

The audit generates two key files in the `outputs/` directory:

1. **JSON Report** (`uniqlo_pr_audit_YYYYMMDD_HHMM.json`)
   - Complete audit results
   - Detailed recommendations
   - Citation metadata
   - Competitive analysis

2. **Citations CSV** (`uniqlo_citations_YYYYMMDD_HHMM.csv`)
   - Raw citation data
   - Domain classification
   - Platform attribution
   - Prompt mapping

## Advanced Usage

### Customizing the Audit

You can modify the audit configuration by editing the `AuditConfig` in `uniqlo_audit.py`:

```python
config = AuditConfig(
    brand="UNIQLO",
    competitors=["H&M", "Zara", "Gap"],  # Modify competitor list
    max_prompts=30,                      # Adjust prompt count
    region="US",                         # Change geographic focus
    parallel_execution=False,            # Disable parallel processing
    custom_prompts=[                     # Add custom prompts
        "Your custom prompt here"
    ]
)
```

### Integration with Existing Workflows

The audit integrates seamlessly with the existing citation audit framework:

```python
from api import CitationAuditAPI, AuditConfig, Industry, PromptStrategy
from uniqlo_audit import generate_pr_recommendations, analyze_sustainability_positioning

# Use existing API with UNIQLO-specific analysis
api = CitationAuditAPI()
results = api.run_audit(your_config)

# Apply UNIQLO-specific analysis functions
recommendations = generate_pr_recommendations(results)
sustainability_insights = analyze_sustainability_positioning(results)
```

## Interpreting Results

### Score Interpretation
- **90-100**: Excellent visibility and authority
- **70-89**: Good presence with optimization opportunities
- **50-69**: Moderate visibility, significant improvement needed
- **Below 50**: Poor visibility, urgent action required

### Competitive Delta Analysis
- **Above 80**: Strong competitive position
- **60-80**: Competitive but with opportunities
- **40-60**: Lagging behind competitors
- **Below 40**: Significant competitive disadvantage

### Sustainability Positioning
- **High eco-media presence**: Strong sustainability narrative
- **Patagonia co-citations**: Aspirational sustainability benchmark
- **Shein co-citations**: Risk of fast fashion association
- **H&M co-citations**: Direct sustainability competition

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   ERROR: PERPLEXITY_API_KEY not set in environment
   ```
   **Solution**: Set the required API keys in your environment

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'api'
   ```
   **Solution**: Ensure you're running from the correct directory with `api.py`

3. **Platform Failures**
   ```
   ❌ Gemini platform failed: [error message]
   ```
   **Solution**: The audit will continue with available platforms

### Performance Optimization

- **Parallel Execution**: Enabled by default for faster processing
- **Rate Limiting**: Built-in delays prevent API throttling
- **Platform Selection**: Audit adapts to available API keys

## Next Steps for PR Teams

After running the audit:

1. **Review JSON Report**: Analyze detailed citation breakdown and competitive positioning
2. **Examine CSV Data**: Identify domain-specific opportunities and gaps
3. **Implement HIGH Priority Recommendations**: Focus on urgent strategic actions
4. **Schedule Regular Re-audits**: Monthly or quarterly monitoring for progress tracking

## Support

For questions about the audit methodology, refer to:
- `README_API.md` - API framework documentation
- `TECHNICAL_SPEC_V2.md` - Technical specifications
- Case studies in `case_studies/` directory

## Example Output

```
UNIQLO AI CITATION VISIBILITY AUDIT
Competitive Intelligence & PR Strategy Analysis
============================================================

📊 VISIBILITY SCORES:
  Overall Score: 67.3/100
  Presence: 72.1
  Prominence: 58.9
  Quality: 71.2
  Competitive Delta: 64.8

📈 CITATION METRICS:
  Total Citations: 156
  Platforms Used: perplexity, chatgpt, claude, gemini
  Execution Time: 127.3 seconds

🏆 COMPETITIVE INTELLIGENCE:
  H&M: 23 co-citations
  Zara: 19 co-citations
  Gap: 12 co-citations
  Shein: 8 co-citations
  Patagonia: 3 co-citations
  Everlane: 2 co-citations

PR STRATEGIC RECOMMENDATIONS
============================================================

1. INCREASE FASHION MEDIA AUTHORITY
   Priority: HIGH
   Only 12 citations from fashion tier-1 media (7.7% of total)
   • Target publications missing from citations: vogue.com, wwd.com, hypebeast.com
   • Develop fashion-forward narrative beyond basics positioning
   • Create exclusive content for fashion media
   • Build relationships with key fashion editors
```

This comprehensive audit provides actionable insights for UNIQLO's PR strategy, focusing on competitive positioning and sustainability leadership in the fast fashion industry.

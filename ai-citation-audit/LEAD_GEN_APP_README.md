# Lead Generation AI Visibility Audit - POC

## Overview

Lightweight proof-of-concept for customer-facing AI visibility audits. Runs limited 5-query audits to generate leads for full analysis services.

## Features

- **Simple Form**: Brand, email, competitors, sample query
- **Fast Execution**: 5 queries × 4 platforms = ~2-3 minutes
- **Sample Dashboard**: Key metrics with clear upgrade CTA
- **Lead Capture**: Email required for results delivery
- **CSV Download**: Sample data export

## Quick Start

### 1. Start the Flask App

```bash
# Ensure .env has API keys
source .env  # or load_env.py

# Run the web app
python3 web_app.py
```

Server starts at: `http://localhost:5010`

### 2. Access Lead Gen Form

Navigate to: `http://localhost:5010/lead-gen`

### 3. Fill Out Form

**Required:**
- Your Brand: e.g., "ACME Corp"
- Your Email: e.g., "prospect@acme.com"
- Sample Query: e.g., "What are the best widgets for holiday gift giving?"

**Optional:**
- Competitors: e.g., "Dunder Mifflin, Wayne Enterprises"

### 4. View Results

After ~2-3 minutes, see:
- Brand mention rate
- Competitive comparison
- Sample query results
- Platform performance
- **Big CTA for full analysis**
- CSV download link

## File Structure

```
simple_lead_auditor.py          # Limited 5-query audit engine
templates/lead_gen_results.html # Results dashboard template
web_app.py                      # Flask routes (/lead-gen)
lead_audits/                    # Output directory for audits
```

## API Keys Required

Same as internal tool:
- `OPENAI_API_KEY` - ChatGPT
- `ANTHROPIC_API_KEY` - Claude
- `PERPLEXITY_API_KEY` - Perplexity
- `GOOGLE_API_KEY` - Gemini

## Output Files

Generated in `lead_audits/` directory:
- `{Brand}_sample_{timestamp}.csv` - Raw query results
- `{Brand}_summary_{timestamp}.json` - Summary metrics

## Deployment

### Local Testing

```bash
python3 web_app.py
# Visit http://localhost:5010/lead-gen
```

### Production Deployment (Example: Heroku/Render/Railway)

1. Add to `requirements.txt` (already included)
2. Set environment variables (API keys)
3. Deploy Flask app
4. Point innatec3.com subdomain to app URL

Example for subdomain:
- `https://audit.innatec3.com` → `/lead-gen` route

## Customization

### Update CTA Email/Calendar

Edit in `templates/lead_gen_results.html`:

```html
<a href="mailto:YOUR.EMAIL@innatec3.com?subject=Full AI Visibility Audit Request">
```

And:

```html
<strong>calendly.com/YOUR-LINK</strong>
```

### Adjust Query Count

Edit in `simple_lead_auditor.py`:

```python
def generate_queries(self) -> List[str]:
    # Currently returns 5 queries
    # Increase to 8-10 for more robust sample
```

### Modify Branding Colors

Edit CSS in `templates/lead_gen_results.html`:

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change to your brand colors */
}
```

## Usage Flow

```
User visits /lead-gen
    ↓
Fills out form (brand, email, query, competitors)
    ↓
Submits form (POST to /lead-gen)
    ↓
simple_lead_auditor.py runs
    ├─ Generate 5 queries
    ├─ Query ChatGPT, Claude, Perplexity, Gemini
    ├─ Analyze responses for brand mentions
    └─ Calculate metrics
    ↓
Render lead_gen_results.html
    ├─ Show key metrics
    ├─ Competitive comparison
    ├─ Sample query breakdown
    └─ BIG CTA for full analysis
    ↓
User downloads CSV or contacts for full audit
```

## Testing

### Test with Sample Data

```bash
# Run the auditor directly
python3 simple_lead_auditor.py

# This will run a test audit for "ACME Corp"
# Check lead_audits/ for output files
```

### Test Web Form

1. Visit `http://localhost:5010/lead-gen`
2. Enter test data:
   - Brand: "Test Brand"
   - Email: "test@test.com"
   - Query: "best products for testing"
   - Competitors: "Competitor A, Competitor B"
3. Submit and wait ~2-3 minutes
4. Verify dashboard displays correctly
5. Test CSV download link

## Limitations (POC)

❌ No real-time progress updates (v2 feature)
❌ No email automation (manual follow-up)
❌ Basic form validation only
❌ No payment/CRM integration
❌ Minimal branding/CSS polish

## Next Steps (v2)

1. **Real-time progress**: WebSocket/SSE for live updates
2. **Email automation**: Send results + follow-up sequence
3. **Enhanced UX**: Typeform-style multi-step flow
4. **CRM integration**: Auto-create leads in HubSpot/Salesforce
5. **A/B testing**: Test different CTAs and query counts
6. **Analytics**: Track conversion rates

## Support

Questions? Contact: [your email]

## License

Internal use only - Innate C3

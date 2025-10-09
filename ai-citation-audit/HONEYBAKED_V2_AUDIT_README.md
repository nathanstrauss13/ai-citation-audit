# HoneyBaked Ham V2 Audit - Precision Methodology

## Overview

This is a **programmatic API-based audit** that tests HoneyBaked Ham's visibility across 4 major AI platforms (ChatGPT, Claude, Perplexity, Gemini) using 15 carefully crafted queries.

### Key Innovation: Three-Layer Analysis

Unlike traditional audits that conflate "brand mentions" with "citations," this V2 methodology distinguishes between:

1. **Brand Mention in LLM Response Text** - Did the AI mention HoneyBaked in its generated answer?
2. **Total Citations Provided** - How many sources/URLs did the LLM cite?
3. **Brand in Citations** - How many of those cited sources actually mention HoneyBaked?

## What Gets Tested

### Query Categories (15 Total)

**BRANDED QUERIES (3)** - Brand name explicitly in query
- "Compare HoneyBaked Ham to Omaha Steaks for holiday meals"
- "What makes HoneyBaked Ham different from other spiral hams?"
- "Where can I find HoneyBaked Ham stores near me?"

**BRAND-AGNOSTIC QUERIES (12)** - No brand names mentioned

*Holiday Ham (4)*
- "What is the best ham for Thanksgiving dinner?"
- "What is the best ham for Christmas dinner?"
- "Best spiral cut ham brands"
- "Best mail-order hams for holidays"

*Convenience/Ordering (4)*
- "What should I serve for Christmas dinner if I don't want to cook?"
- "What is the easiest holiday meal to order online?"
- "Last-minute Thanksgiving dinner options"
- "Where can I order a complete holiday meal?"

*Gifting (3)*
- "Best holiday food gifts to ship"
- "What's the best food gift for the holidays?"
- "Premium food gifts for corporate clients"

*Thought Leadership (1)*
- "Who are the top chefs in the holiday catering industry?"

### Platforms Tested

- **ChatGPT** (GPT-4o-mini)
- **Claude** (Claude 3.5 Sonnet)
- **Perplexity** (Sonar Pro)
- **Gemini** (Gemini 2.5 Flash)

**Total Tests:** 15 queries × 4 platforms = **60 API calls**

## Output Files

The audit generates 4 files:

### 1. `HONEYBAKED_QUERY_RESPONSE_MATRIX_{timestamp}.csv`

Captures what the LLM said and how it cited:

| Column | Description |
|--------|-------------|
| `query` | The exact query text |
| `query_type` | "branded" or "brand_agnostic" |
| `engine` | Platform name (chatgpt, claude, perplexity, gemini) |
| `brand_mentioned_in_response` | Did LLM's text mention HoneyBaked? (Yes/No) |
| `total_citations` | Number of URLs/sources cited |
| `citations_mentioning_brand` | How many citations mention HoneyBaked (0 to total) |
| `response_prominence` | Where brand appeared ("Featured First" / "Listed Among Options" / "Mentioned in Passing" / "Not Present") |
| `chef_tim_mentioned` | Was Chef Tim Ziga mentioned? (Yes/No) |

### 2. `HONEYBAKED_CITATION_DETAILS_{timestamp}.csv`

Every single citation URL with analysis:

| Column | Description |
|--------|-------------|
| `engine` | AI platform |
| `query` | Query that triggered this citation |
| `query_type` | "branded" or "brand_agnostic" |
| `citation_url` | Full URL provided by LLM |
| `domain` | Root domain (e.g., "seriouseats.com") |
| `domain_classification` | Type of source (tier1_news, food_media, authority, etc.) |
| `honeybaked_mentioned_in_source` | Does the actual source mention HoneyBaked? (Yes/No) |
| `content_type` | Content classification (buying_guide, product_review, news_article, etc.) |

**Domain Classifications:**
- `tier1_news` - NYT, WSJ, Washington Post
- `tier2_news` - Regional newspapers
- `food_media` - Serious Eats, Bon Appétit, Food Network, AllRecipes
- `lifestyle_media` - Good Housekeeping, Martha Stewart, Real Simple
- `business_media` - Business Insider, Forbes, Bloomberg
- `authority` - Consumer Reports, Wirecutter
- `brand_official` - HoneyBaked.com, competitor sites
- `retail` - Amazon, Walmart, grocery sites
- `other` - Everything else

### 3. `HONEYBAKED_COMPETITIVE_MENTIONS_{timestamp}.csv`

Tracks competitor visibility:

| Column | Description |
|--------|-------------|
| `query` | The query tested |
| `query_type` | "branded" or "brand_agnostic" |
| `engine` | AI platform |
| `competitor_mentioned` | Name of competitor (or "HoneyBaked") |
| `mentioned_in_response` | In LLM text? (Yes/No) |
| `mentioned_in_citations` | In cited sources? (Yes/No) |
| `prominence_vs_honeybaked` | Relative positioning |

**Competitors Tracked:**
- Omaha Steaks, Whole Foods, Costco, Harry & David, Williams Sonoma, D'Artagnan, Smithfield, Spiral Ham Store, Glazier Ham, Sam's Club, Walmart, Kroger, Publix

### 4. `HONEYBAKED_AUDIT_SUMMARY_{timestamp}.json`

Summary statistics including:
- Overall brand mention rate
- Citation authority score
- Performance by query type (branded vs brand-agnostic)
- Performance by platform
- Competitive landscape overview

## Installation & Setup

### Prerequisites

```bash
pip install requests beautifulsoup4 python-dotenv
```

### API Keys Required

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
GOOGLE_API_KEY=AIza...
```

## Usage

### Run Complete Audit

```bash
python run_honeybaked_v2_audit.py
```

This will:
1. Test all 15 queries across all 4 platforms (60 tests)
2. Analyze each response for brand mentions
3. Fetch and analyze cited URLs for brand presence
4. Track competitive mentions
5. Generate all CSV files and JSON summary

**Estimated Runtime:** 10-15 minutes

### Output Location

All files saved to:
```
case_studies/honeybaked_ham/v2_audit/
```

## Key Metrics Explained

### Brand-Agnostic Mention Rate
**What it measures:** Of the 12 brand-agnostic queries (where HoneyBaked wasn't explicitly mentioned), in what percentage did the AI mention HoneyBaked anyway?

**Calculation:** `(Brand mentions in agnostic queries / Total agnostic queries) × 100`

**Why it matters:** This shows "organic" visibility - whether AIs naturally recommend HoneyBaked when users ask generic questions about holiday hams.

### Citation Authority Score
**What it measures:** Of all the URLs cited by AIs, what percentage actually mention HoneyBaked?

**Calculation:** `(Citations mentioning brand / Total citations) × 100`

**Why it matters:** High scores mean the brand has strong presence in authoritative sources that AIs reference. Low scores mean AIs cite sources that don't mention the brand.

### Category Capture Rate
**What it measures:** Success rate in specific query categories (Holiday Ham, Convenience, Gifting, etc.)

**Why it matters:** Identifies which market categories the brand dominates vs. where visibility is weak.

### Platform Bias
**What it measures:** How brand visibility varies across ChatGPT vs Claude vs Perplexity vs Gemini

**Why it matters:** Some platforms may favor certain sources or have different training data, affecting brand visibility.

## Validation Checklist

Before using audit data, verify:

- ✅ All 60 prompts executed (15 queries × 4 engines)
- ✅ Every row in QUERY_RESPONSE_MATRIX has corresponding CITATION_DETAILS entries
- ✅ `citations_mentioning_brand` count matches actual URLs where `honeybaked_mentioned_in_source = Yes`
- ✅ Query types correctly classified (3 branded, 12 brand-agnostic)
- ✅ All citations have domain classification
- ✅ Competitive mentions captured for each query
- ✅ No conflation of "brand in response" vs "brand in citations"

## Understanding the Data

### Example Scenario

**Query:** "What is the best ham for Thanksgiving dinner?" (brand-agnostic)
**Platform:** ChatGPT

**LLM Response Text:**
> "For Thanksgiving, consider Smithfield Spiral Ham for value, or HoneyBaked Ham for convenience."

**LLM Citations:**
1. https://www.seriouseats.com/best-hams (mentions HoneyBaked ✓)
2. https://www.consumerreports.org/hams (does NOT mention HoneyBaked ✗)
3. https://www.honeybaked.com/products (mentions HoneyBaked ✓)

**How This Gets Recorded:**

**QUERY_RESPONSE_MATRIX:**
- `brand_mentioned_in_response`: Yes
- `total_citations`: 3
- `citations_mentioning_brand`: 2
- `response_prominence`: "Listed Among Options"

**CITATION_DETAILS (3 rows):**
```csv
chatgpt,"What is the best ham...",brand_agnostic,https://www.seriouseats.com/best-hams,seriouseats.com,food_media,Yes,buying_guide
chatgpt,"What is the best ham...",brand_agnostic,https://www.consumerreports.org/hams,consumerreports.org,authority,No,product_review
chatgpt,"What is the best ham...",brand_agnostic,https://www.honeybaked.com/products,honeybaked.com,brand_official,Yes,company_page
```

**COMPETITIVE_MENTIONS (2 rows):**
```csv
"What is the best ham...",brand_agnostic,chatgpt,Smithfield,Yes,Unknown,"Higher - Featured First"
"What is the best ham...",brand_agnostic,chatgpt,HoneyBaked,Yes,Yes,"Equal - Listed Together"
```

## Advanced Analytics

With this data, you can calculate:

### 1. Media Influence Score
Which media domains (Serious Eats, Consumer Reports, etc.) drive AI visibility?
- Filter CITATION_DETAILS by `domain_classification`
- Count how often tier1_news vs food_media cite the brand

### 2. Content Type Effectiveness
Do buying guides mention the brand more than reviews?
- Group CITATION_DETAILS by `content_type`
- Calculate mention rate for each type

### 3. Competitor Win/Loss Analysis
Where do competitors beat HoneyBaked?
- Filter COMPETITIVE_MENTIONS for each competitor
- Identify queries where competitor had "Higher" prominence

### 4. Platform-Specific Strategies
Should PR focus on sources that ChatGPT prefers vs Claude?
- Cross-reference CITATION_DETAILS with platform performance
- Identify domain patterns per platform

## Troubleshooting

### "Missing API key" Error
Ensure all 4 API keys are set in `.env` file.

### URLs Not Fetched
Some URLs may be behind paywalls or block automated access. These are marked as "Unable_to_verify" in the output.

### Rate Limiting
The script includes 2-second delays between API calls. If you hit rate limits, increase the delay in `run_audit()`.

### Incomplete Results
If the audit is interrupted, it will still generate CSVs with partial data. Re-run to complete.

## Methodology Validation

This methodology has been validated across multiple industries:
- ✅ Food & Beverage (HoneyBaked Ham)
- ✅ Retail (UNIQLO, PacSun)
- ✅ Robotics (Pickle Robot)
- ✅ Sports Leagues (NBA, NHL)
- ✅ Entertainment (Vevo)

**Key Principle:** Never conflate "brand mentioned in AI response" with "brand mentioned in source." They are distinct metrics that measure different aspects of AI visibility.

## Next Steps

After running the audit:

1. **Open the CSV files** in Excel/Google Sheets
2. **Review the JSON summary** for high-level metrics
3. **Identify visibility gaps** (queries where brand should appear but doesn't)
4. **Analyze competitor positioning** (where they outrank HoneyBaked)
5. **Target media opportunities** (domains that AIs cite frequently but don't mention brand)

## Support

For questions or issues:
- Review the validation checklist above
- Check that all API keys are valid
- Ensure `requirements.txt` dependencies are installed
- Verify internet connectivity for URL fetching

---

**Version:** 2.0  
**Last Updated:** September 30, 2025  
**Methodology:** Precision API Data Collection

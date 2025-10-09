# HoneyBaked Ham Comprehensive GEO Citation Analysis

Complete implementation of the AEO methodology framework for HoneyBaked Ham's holiday PR campaign analysis.

## 📋 Overview

This tool conducts a comprehensive AI citation audit with:
- **35 unique queries** across 5 categories
- **4 AI platforms**: ChatGPT, Claude, Perplexity, Gemini
- **140 total tests** (35 queries × 4 platforms)
- **4 CSV outputs** for complete analysis

## 🎯 Analysis Objectives

1. **Query Coverage**: Measure HoneyBaked presence across holiday shopping queries
2. **PR Media Targets**: Track achievement of 11 priority media outlets
3. **Competitive Context**: Analyze positioning vs. key competitors
4. **Authority Building**: Track Chef Tim Ziga thought leadership mentions
5. **Citation Quality**: Assess editorial tier and media quality

## 📊 Query Structure

### 1. Branded Queries (7 queries - 20%)
Test HoneyBaked's owned content quality and baseline presence:
- "What is HoneyBaked Ham known for?"
- "Tell me about HoneyBaked Ham"
- "HoneyBaked Ham history and reputation"
- "Where can I buy HoneyBaked Ham?"
- "HoneyBaked Ham reviews and ratings"
- "Who is Chef Tim Ziga?"
- "HoneyBaked Ham holiday menu 2025"

### 2. Primary Holiday Queries (10 queries - 29%)
Core holiday shopping intent:
- Best ham for Thanksgiving/Christmas dinner
- Quick holiday ham ordering
- Easy meal solutions
- Pre-cooked delivery options
- Complete dinner delivery services

### 3. Gift & Convenience Queries (8 queries - 23%)
Gift-giving and convenience positioning:
- Holiday food gifts
- Corporate gifts
- Mail order options
- Gourmet food gifts
- Catering services

### 4. Competitive Comparison Queries (5 queries - 14%)
Direct competitive context:
- "Best premium ham brands"
- "Compare holiday ham delivery services"
- "Omaha Steaks vs HoneyBaked Ham vs Harry & David"
- Market share and popularity queries

### 5. Quality & Expertise Queries (5 queries - 14%)
Thought leadership positioning:
- How to choose quality ham
- Chef preparation tips
- Professional serving guidance
- Quality indicators

## 📁 Output Files

### 1. HONEYBAKED_ANALYSIS_MATRIX_{timestamp}.csv
Query-level performance tracking with competitive context.

**Columns** (19 total):
- Query metadata (query, type, category, commercial intent)
- Platform data (engine, timestamp, quality)
- Brand presence (HoneyBaked mentioned, prominence, featured brand)
- Competitor tracking (competitors mentioned)
- Citation analysis (total, owned, earned, by brand)
- Authority tracking (Chef Tim Ziga mentions)

**Usage**: Primary dashboard for query performance analysis.

### 2. CITATION_DETAILS_{timestamp}.csv
Every individual citation captured for source-level analysis.

**Columns** (15 total):
- Query context (engine, query, category, type)
- Citation data (URL, domain, position)
- Classification (domain type, content type, media tier)
- Brand tracking (HoneyBaked, competitor mentions)

**Usage**: Source quality analysis, media partnership identification.

### 3. COMPETITIVE_CONTEXT_{timestamp}.csv
Every brand mention tracked for competitive intelligence.

**Columns** (11 total):
- Brand identification
- Query context
- Mention analysis (present, prominence ranking)
- Context extraction (tone, products, mention context)
- Citation count per brand

**Usage**: Competitive positioning analysis, share of voice.

### 4. PR_MEDIA_TARGETS_{timestamp}.csv
Achievement tracking for 11 priority media outlets.

**Columns** (11 total):
- Media outlet identification
- Target status (ACHIEVED, TARGET)
- Performance metrics (citation count, queries, engines)
- Content tracking (URLs, HoneyBaked mentions)
- Strategic value assessment

**Usage**: PR campaign effectiveness measurement.

## 🏗️ Domain Classification System

The tool implements a comprehensive domain classification system:

### Brand & Competitor
- `brand_official`: honeybaked.com
- `competitor_official`: Omaha Steaks, Harry & David, Costco, Whole Foods, Smithfield

### Editorial Media
- `editorial_tier1`: Food & Wine, Bon Appétit, Serious Eats, Epicurious
- `editorial_tier2`: Allrecipes, Delish, Taste of Home, The Kitchn
- `editorial_tier3`: Bustle, Refinery29, BuzzFeed

### Lifestyle Media
- `lifestyle_tier1`: Business Insider, Forbes, CNN
- `lifestyle_tier2`: Southern Living, Real Simple, GQ

### News & Trade
- `news_media`: NYT, WSJ, Reuters, AP
- `food_trade`: Restaurant Business, QSR, Nation's Restaurant News
- `retail_trade`: Retail Dive, Chain Store Age
- `franchise_trade`: Franchise Times, Entrepreneur

### Commerce & Social
- `retail_partner`: Amazon, Walmart, Target, Kroger
- `review_platform`: Yelp, TripAdvisor, Trustpilot
- `social_reddit`, `social_youtube`, `social_tiktok`, `social_instagram`
- `pr_wire`: PR Newswire, Business Wire

## 🎨 Content Type Classification

The tool classifies content into:
- `buying_guide`: Best X articles, roundups
- `product_review`: Individual reviews
- `holiday_guide`: Holiday-specific content
- `gift_guide`: Gift recommendations
- `recipe_content`: Recipes, cooking instructions
- `how_to_guide`: Tips, instructional content
- `news_article`: News, announcements
- `listicle`: Numbered lists, rankings
- `comparison_article`: Side-by-side comparisons

## 🎯 PR Target Media (from brief)

The tool specifically tracks these 11 priority outlets:
1. Business Insider (businessinsider.com)
2. Serious Eats (seriouseats.com)
3. Allrecipes (allrecipes.com)
4. The Spruce Eats (thespruceeats.com)
5. Good Housekeeping (goodhousekeeping.com)
6. CNN (cnn.com)
7. Consumer Reports (consumerreports.org)
8. Eater (eater.com)
9. Food & Wine (foodandwine.com)
10. Southern Living (southernliving.com)
11. Bon Appétit (bonappetit.com)

## 🚀 Usage

### Prerequisites
```bash
# Install dependencies
pip install requests google-generativeai

# Configure API keys in .env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### Running the Audit
```bash
# Execute comprehensive audit
python run_honeybaked_comprehensive.py

# Or directly
python honeybaked_comprehensive_geo_auditor.py
```

### Expected Runtime
- **Full audit**: 30-45 minutes
- **Per query**: ~45-60 seconds (4 platforms)
- **Total tests**: 140 (35 queries × 4 platforms)

Note: Gemini limited to first 10 queries due to rate limits.

## 📈 Output Location

All files saved to:
```
case_studies/honeybaked_ham/comprehensive_geo/
├── HONEYBAKED_ANALYSIS_MATRIX_YYYYMMDD_HHMM.csv
├── CITATION_DETAILS_YYYYMMDD_HHMM.csv
├── COMPETITIVE_CONTEXT_YYYYMMDD_HHMM.csv
└── PR_MEDIA_TARGETS_YYYYMMDD_HHMM.csv
```

## 📊 Key Metrics Tracked

### Query Coverage
- % of queries where HoneyBaked appears
- Performance by query category
- Platform-by-platform breakdown

### PR Media Achievement
- Number of target media outlets cited
- Citation frequency per outlet
- Query coverage per outlet

### Competitive Position
- Share of mentions vs. competitors
- Prominence ranking (1st, 2nd, 3rd mention)
- Featured brand analysis

### Authority Building
- Chef Tim Ziga mention frequency
- Context of authority mentions
- Platform distribution

### Citation Quality
- Total citations collected
- Owned vs. earned media ratio
- Editorial tier distribution
- Media quality scores

## 🔍 Analysis Workflow

1. **Run the audit** (30-45 minutes)
2. **Review console output** for immediate metrics
3. **Upload CSV files to Claude** for dashboard creation
4. **Analyze results** using methodology framework
5. **Generate strategic recommendations**

## 🎯 Strategic Priorities

Based on the PR brief, the analysis focuses on:

1. **Primary Holiday Queries** - Highest priority for PR campaign
2. **PR Target Media** - Track 11 specific outlets
3. **Chef Tim Ziga** - Thought leadership tracking
4. **Competitive Context** - Document competitor dominance
5. **Gift Category** - Critical for holiday campaign

## ⚠️ Limitations

1. **Gemini Rate Limits**: Only first 10 queries tested
2. **Citation Completeness**: AI platforms vary in citation provision
3. **Real-time Content**: Results reflect current AI training data
4. **Manual Validation**: Some fields (page titles, dates) require manual scraping
5. **Sentiment Analysis**: Tone assessment is placeholder (requires NLP)

## 🔧 Technical Details

### API Adapters
- **Perplexity**: Native citation support via `return_citations=True`
- **ChatGPT**: URL extraction from response text
- **Claude**: URL extraction from response text
- **Gemini**: URL extraction from response text

### Rate Limiting
- 1 second delay between ChatGPT/Claude/Perplexity calls
- 4 second delay for Gemini calls
- Sequential processing to avoid API throttling

### Error Handling
- Platform failures logged with error codes
- Partial results saved if audit interrupted
- Missing API keys handled gracefully

## 📚 Methodology References

This implementation follows:
- AEO Citation Analysis - Complete Methodology & Framework.pdf
- HoneyBaked Ham PR Brief specifications
- Previous audit learnings from existing tools

## 🤝 Support

For issues or questions:
1. Check API key configuration in .env
2. Verify internet connectivity
3. Review console output for specific errors
4. Check case_studies/honeybaked_ham/comprehensive_geo/ for partial results

## 📝 Next Steps After Audit

1. **Upload CSV files to Claude** for dashboard creation
2. **Review PR target achievement** - Which outlets were cited?
3. **Analyze competitive gaps** - Where do competitors dominate?
4. **Identify content opportunities** - Which queries need better coverage?
5. **Develop strategic recommendations** - Based on data insights

---

**Generated with**: HoneyBaked Ham Comprehensive GEO Citation Auditor v1.0  
**Framework**: AEO Methodology for AI Citation Analysis  
**Focus**: Holiday Shopping Season (Thanksgiving, Christmas, Gift-Giving)

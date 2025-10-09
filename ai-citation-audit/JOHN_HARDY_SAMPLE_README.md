# John Hardy "Free Sample" AEO Citation Analysis

## Proof-of-Concept: 10 Queries × 4 Engines = 40 Prompts

**Demonstrate AEO Analysis Value with Minimal Investment**

---

## Overview

This streamlined analysis tests **10 strategically selected queries** across 4 AI platforms to demonstrate:
- Citation tracking methodology
- Competitive positioning insights  
- Content strategy gaps
- Media influence analysis
- ROI potential before full 100-prompt analysis

**Time Investment:** ~90 minutes data collection + analysis  
**Output:** Proof-of-concept dashboard showing methodology value

---

## Quick Start

### Prerequisites

1. **API Keys Required** (set in `.env` file):
   ```bash
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   PERPLEXITY_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

2. **Dependencies** (already installed if using this project):
   ```bash
   pip install requests beautifulsoup4 python-dotenv
   ```

### Running the Audit

```bash
# Simple execution
python run_john_hardy_sample.py

# Or direct execution
python john_hardy_sample_audit.py
```

---

## The 10 Strategic Queries

### Category 1: Brand Awareness (2 queries)
1. **"What is John Hardy jewelry known for?"**
   - Tests: Basic brand visibility
   - Expected: High visibility on direct brand query

2. **"Is John Hardy jewelry worth the investment?"**
   - Tests: Value positioning, quality perception
   - Expected: May compare to Tiffany, Cartier

### Category 2: Sustainability Focus (3 queries)
3. **"Most sustainable luxury jewelry brands"**
   - Tests: Sustainability positioning (strategic priority)
   - Competitors: Brilliant Earth, Vrai, Mejuri expected

4. **"Ethical jewelry brands that use recycled materials"**
   - Tests: Specific sustainability claims (recycled metals)
   - Expected: Shows if JH's recycled metal messaging is visible

5. **"Which jewelry companies are truly sustainable?"**
   - Tests: Authenticity/credibility in sustainability
   - Competitors: B-Corp certified brands may dominate

### Category 3: Lab-Grown Diamonds (2 queries)
6. **"Best lab-grown diamond jewelry brands"**
   - Tests: Lab-grown diamond association
   - Critical: Is JH even mentioned in this category?

7. **"Luxury brands that offer lab-grown diamonds"**
   - Tests: Does AI know JH offers lab-grown?
   - Expected: Likely low visibility if new product line

### Category 4: Competitive Positioning (2 queries)
8. **"John Hardy vs Tiffany & Co sustainability"**
   - Tests: Direct competitive comparison
   - Shows: Which brand "wins" sustainability positioning

9. **"David Yurman vs John Hardy craftsmanship"**
   - Tests: Craftsmanship/artisan positioning
   - Shows: Authority on artisan/craft narrative

### Category 5: Thought Leadership (1 query)
10. **"Jewelry industry sustainability leaders"**
    - Tests: Thought leadership/authority
    - Shows: Is JH viewed as industry leader or follower?

---

## Output Files

The audit generates 4 files in `case_studies/john_hardy_sample/`:

### 1. JOHN_HARDY_SAMPLE_MATRIX_[timestamp].csv

**Purpose:** High-level query performance overview

**Columns:**
- `query` - The search query tested
- `engine` - AI platform (chatgpt, claude, perplexity, gemini)
- `john_hardy_present` - Was John Hardy mentioned? (Yes/No)
- `competitors_mentioned` - Which competitors appeared
- `position_prominence` - How prominently positioned (High/Medium/Low/Not Present)
- `winner_brand` - Which brand presented most favorably
- `total_citations` - Number of sources cited

**Use For:**
- Quick visibility scorecard
- Platform comparison
- Category performance analysis

### 2. RAW_CITATIONS_SAMPLE_[timestamp].csv

**Purpose:** Detailed citation-level analysis

**Columns:**
- `Engine` - AI platform
- `Query` - Search query
- `Domain` - Source website domain
- `Classification` - Source type (luxury_fashion_tier1, business_sustainability, etc.)
- `URL` - Full citation URL
- `Brand_Association` - Which brand cited (John Hardy, competitor, or Unknown)
- `Confidence_Level` - HIGH/MEDIUM/LOW confidence in brand association
- `URL_Contains_Brand` - Does URL explicitly contain brand name?
- `Content_Type` - Editorial, Product, Owned, Sustainability, News, etc.

**Classification Types:**
- `luxury_fashion_tier1` - Vogue, Harper's Bazaar, Elle
- `business_sustainability` - Forbes, Fast Company
- `jewelry_trade` - JCK, National Jeweler
- `sustainability_media` - The Good Trade
- `owned` - John Hardy official site
- `competitor_owned` - Competitor official sites
- `retail` - Nordstrom, Neiman Marcus
- `general_editorial` - Other editorial content

**Use For:**
- Content strategy insights
- PR target identification
- Competitor content analysis
- Authority source mapping

### 3. MEDIA_TRACKING_SAMPLE_[timestamp].csv

**Purpose:** Media outlet influence analysis

**Columns:**
- `Media_Outlet` - Domain name
- `Citation_Count` - Total times cited
- `John_Hardy_Citations` - Citations mentioning JH
- `Competitor_Citations` - Citations mentioning competitors
- `Top_Queries` - Which queries triggered citations
- `Engines` - Which platforms cited this outlet

**Tracked Outlets:**
1. vogue.com
2. forbes.com
3. harpersbazaar.com
4. thegoodtrade.com (sustainability focus)
5. jckonline.com (jewelry trade)
6. nordstrom.com (retail partner)
7. brilliantearth.com (competitor)
8. tiffany.com (competitor)
9. nytimes.com
10. businessinsider.com

**Use For:**
- PR strategy prioritization
- Media relationship gaps
- Competitor coverage comparison
- Tier 1 outlet performance

### 4. AUDIT_SUMMARY_[timestamp].json

**Purpose:** Executive summary statistics

**Contains:**
- Overall visibility rates
- Category performance breakdown
- Platform comparison
- Top competitor mentions
- Media coverage summary

---

## Strategic Questions This Sample Answers

### ✓ Visibility Questions
- Is John Hardy visible in AI responses at all?
- For what % of queries does JH appear?
- How does visibility compare to key competitors?

### ✓ Positioning Questions
- Is JH positioned as sustainable leader or follower?
- Is JH associated with lab-grown diamonds?
- Does JH have craftsmanship/artisan authority?
- Who "wins" in competitive comparisons?

### ✓ Content Strategy Questions
- What content types drive competitor visibility?
- Are competitor blogs cited more than JH?
- Is JH's owned content being cited at all?
- Where are the content gaps?

### ✓ PR Strategy Questions
- Which media outlets cover JH?
- Which outlets cover competitors but not JH?
- What's the quality of coverage (tier 1 vs. tier 2)?
- Where should PR focus efforts?

---

## Expected Insights

The proof-of-concept will reveal one of these scenarios:

### Scenario A: Low Visibility
- **Finding:** JH appears in only 30% of queries
- **Insight:** Competitors dominate sustainability queries
- **ROI Case:** Full analysis identifies all gaps → targeted PR/content strategy → improved AI visibility

### Scenario B: Presence Without Prominence
- **Finding:** JH appears in 70% of queries but rarely "wins"
- **Insight:** Always mentioned alongside 5+ competitors, never first
- **ROI Case:** Full analysis reveals positioning weaknesses → refined messaging → improved competitive standing

### Scenario C: Content Strategy Gap
- **Finding:** Competitor blogs cited 40 times, JH blog cited 0 times
- **Insight:** Content not reaching AI training data
- **ROI Case:** Full analysis shows exact content types that work → content investment → future AI training includes JH

### Scenario D: Retail Dependency
- **Finding:** 80% of JH citations are Nordstrom/Neiman Marcus pages
- **Insight:** Only 20% editorial coverage
- **ROI Case:** Full analysis identifies editorial gaps → PR strategy → less retail-dependent visibility

---

## Next Steps After POC

### 1. Review Generated CSVs
- Analyze visibility patterns
- Identify competitor strengths
- Map content gaps

### 2. Generate Dashboard (Optional)
Upload the CSVs to Claude with this prompt:

```
I've completed a proof-of-concept AEO citation analysis for John Hardy jewelry brand.
I tested 10 strategic queries across 4 AI platforms (40 prompts total).

Attached are 3 CSV files:
1. JOHN_HARDY_SAMPLE_MATRIX.csv (query performance)
2. RAW_CITATIONS_SAMPLE.csv (all citations with confidence levels)
3. MEDIA_TRACKING_SAMPLE.csv (media outlet analysis)

Please create a proof-of-concept AEO dashboard showing:
1. Overall visibility score (% of queries where JH appears)
2. Competitive ranking (JH vs. top 3 competitors)
3. Query performance breakdown (10 queries with win/loss)
4. Top 5 strategic insights with specific data points
5. ROI case for full 100-prompt analysis

Brand colors:
- Primary: #1A1A1A (black)
- Secondary: #C0A080 (bronze/gold)
- Accent: #2D5016 (green - sustainability)

Focus on:
- Sustainability positioning gaps
- Lab-grown diamond awareness
- Content strategy opportunities
- PR target media list
```

### 3. Decide on Full Analysis
Based on findings, decide whether to invest in:
- **Full 100-prompt analysis** (comprehensive coverage)
- **Category-specific deep dive** (e.g., just sustainability)
- **Quarterly monitoring** (track changes over time)

---

## Business Value Demonstrated

### From 90-Minute Sample:
✓ Proof that methodology works  
✓ Identification of 2-3 major gaps  
✓ Competitive intelligence on what works  
✓ Clear ROI case for full analysis  

### From Full 100-Prompt Analysis:
✓ Comprehensive competitive landscape  
✓ 25 query types tested across all positioning pillars  
✓ Detailed media target list  
✓ Content strategy roadmap  
✓ PR pitch priorities  
✓ Before/after tracking capability  

---

## Technical Details

### Methodology
- **Sequential execution** with 2-second rate limiting
- **Full response text analysis** for brand mentions
- **Citation-level tracking** with confidence scoring
- **Multi-brand comparison** across 15+ competitors

### Confidence Levels
- **HIGH:** Brand name explicitly in citation URL
- **MEDIUM:** Brand mentioned in response but not in URL, or inferred from context
- **LOW:** Uncertain association or competitor site

### Platform Coverage
- **ChatGPT:** GPT-4o-mini model
- **Claude:** Claude 3.5 Sonnet
- **Perplexity:** Sonar Pro
- **Gemini:** Gemini 2.5 Flash

---

## Troubleshooting

### Missing API Keys
```bash
Error: Missing required API keys: OPENAI_API_KEY

Solution: Set all required keys in .env file
```

### Rate Limiting
```bash
Error: 429 Too Many Requests

Solution: Script includes 2-second delays, but you may need to wait
```

### No Citations Returned
```bash
Warning: No citations found for query

Possible causes:
- Platform didn't provide sources
- Query too generic
- Timeout issue

Solution: Review individual platform responses in logs
```

---

## FAQ

**Q: How long does the audit take?**  
A: Approximately 90 minutes for 40 prompts (10 queries × 4 platforms) including rate limiting.

**Q: Can I test different queries?**  
A: Yes, modify the `_define_queries()` method in `john_hardy_sample_audit.py`.

**Q: What if one platform fails?**  
A: The audit continues with other platforms. Failed queries are logged.

**Q: How is "winner" determined?**  
A: Based on prominence in response, positive language, and position in lists.

**Q: Can I run this for other brands?**  
A: Yes, modify `brand_name`, `brand_variants`, and `competitors` in the `__init__` method.

---

## Support

For questions or issues:
1. Check the log output for detailed error messages
2. Verify all API keys are set correctly
3. Ensure all dependencies are installed
4. Review the generated CSV files for partial results

---

## Related Documentation

- Full AEO methodology: `TECHNICAL_SPEC_V2.md`
- Platform adapters: `platforms/` directory
- HoneyBaked Ham case study: `case_studies/honeybaked_ham/`
- Main README: `README.md`

---

**Last Updated:** October 2025  
**Version:** 1.0.0 (Proof-of-Concept)

# Claude.ai Prompt for John Hardy AEO Dashboard Creation

Copy and paste this prompt into Claude.ai along with uploading the 5 John Hardy data files.

---

## PROMPT FOR CLAUDE.AI:

I need you to analyze the John Hardy jewelry AEO citation data and create an interactive HTML dashboard similar to the NBA example I'll show you, but customized for luxury jewelry brand analysis.

### FILES TO UPLOAD:
1. `JOHN_HARDY_BRAND_ANALYSIS_MATRIX_20251001_1752.csv`
2. `JOHN_HARDY_CITATION_DETAILS_20251001_1752.csv`
3. `JOHN_HARDY_COMPETITIVE_CONTEXT_20251001_1752.csv`
4. `JOHN_HARDY_MEDIA_INFLUENCE_20251001_1752.csv`
5. `PLATFORM_RELIABILITY_REPORT_20251001_1752.json`

### TASK:
Create a comprehensive, interactive HTML dashboard for John Hardy's AEO citation analysis that:

1. **Analyzes the complete dataset** (777 citations across 255 domains from 98 successful tests)
2. **Provides PR strategy insights** for luxury jewelry vertical
3. **Identifies media opportunities** in Tier-1 fashion/lifestyle outlets
4. **Tracks earned vs. owned media** (2.02:1 ratio)
5. **Benchmarks against 12 competitors** (Brilliant Earth, Vrai, Tiffany, etc.)

### BRAND CONTEXT:
**John Hardy** is a luxury artisan jewelry brand focused on:
- **Sustainability** - recycled materials, ethical sourcing
- **Craftsmanship** - Balinese artisan techniques
- **Lab-Grown Diamonds** - new product line (testing market awareness)
- **Cultural Heritage** - Indonesian design traditions

**Key Competitors:**
- Brilliant Earth (sustainability leader)
- Vrai (lab-grown diamond focus)
- Tiffany & Co (luxury heritage)
- David Yurman (artisan craftsmanship)
- Mejuri, Aurate, Catbird (accessible luxury)
- Cartier, Chopard, Lagos, Pandora, Bario Neal

### DASHBOARD STRUCTURE:

#### 1. HEADER
- **Title:** "John Hardy Jewelry - AEO Citation Analysis & PR Strategy Dashboard"
- **Subtitle:** "777 Citations Analyzed Across 255 Media Outlets | October 1, 2025"
- **Brand Colors:**
  - Primary: `#1A1A1A` (black - sophistication)
  - Secondary: `#C0A080` (bronze/gold - luxury)
  - Accent: `#2D5016` (green - sustainability)

#### 2. EXECUTIVE SUMMARY (Key Insight Box)
Extract from the data and create a strategic insight highlighting:
- John Hardy's overall citation presence (how many of 98 tests mentioned JH?)
- Top competitor (likely Brilliant Earth or Vrai based on POC)
- Critical gap identified (e.g., sustainability queries, lab-grown diamond category)
- Primary PR opportunity (e.g., "35 media outlets cite competitors but not John Hardy")

#### 3. KEY METRICS GRID (8 cards)
Calculate and display:
- **Total Citations Captured** (777)
- **John Hardy Citations** (count from citation_details where john_hardy_mentioned='Yes')
- **Unique Media Outlets** (255 confirmed)
- **JH Visibility Rate** (% of 98 tests where john_hardy_mentioned='Yes')
- **Earned/Owned Ratio** (2.02:1 from JSON)
- **Tier-1 Luxury Outlet Citations** (count luxury_fashion_tier1)
- **Competitor Citation Lead** (top competitor citations vs. JH)
- **PR Targets Identified** (outlets with competitor citations but no JH)

#### 4. COMPETITIVE CITATION RANKINGS
Create a ranked table showing:
- John Hardy vs. top 5 competitors (Brilliant Earth, Vrai, Tiffany, David Yurman, Mejuri)
- Total citations per brand
- % of total citations
- Citation gap (vs. leader)
- Primary focus mentions (where brand was featured first)
- Visualization: Horizontal bar chart showing market share

**Source:** Aggregate COMPETITIVE_CONTEXT_MATRIX by brand

#### 5. TOP MEDIA OUTLETS (Tabbed View)
Create 4 tabs analyzing MEDIA_INFLUENCE file:

**Tab 1: All Outlets (Top 30)**
- Rank by total citation_count
- Show: Domain, Classification, Total Citations, JH Citations, Competitor Citations, JH Share %, Platforms
- Highlight outlets with >5 citations and <30% JH share (PR targets)

**Tab 2: Luxury Fashion Media**
- Filter: domain_classification = 'luxury_fashion_tier1' (Vogue, Harper's Bazaar, Elle)
- Show JH vs. competitor presence
- **Strategic Insight:** Are competitors dominating tier-1 luxury media?

**Tab 3: Sustainability Media**
- Filter: domain_classification = 'sustainability_media'
- Critical for JH's positioning
- Show citation counts and JH share

**Tab 4: Retail Partners**
- Filter: domain_classification = 'retail_partner'
- Nordstrom, Neiman Marcus, Bloomingdale's, Saks
- Show if JH is visible through retail channels

#### 6. CATEGORY PERFORMANCE ANALYSIS
Analyze BRAND_ANALYSIS_MATRIX by category:

Create a table showing:
- **Brand Awareness** (4 queries): JH mention rate, avg citations
- **Sustainability** (6 queries): JH mention rate, competitor dominance
- **Lab-Grown** (4 queries): JH visibility vs. Vrai/Brilliant Earth
- **Competitive** (4 queries): Head-to-head win rate
- **Thought Leadership** (3 queries): Industry authority presence
- **Product Specific** (4 queries): Artisan/craftsmanship positioning

For each category:
- Calculate: % of queries where john_hardy_mentioned='Yes'
- Identify: Featured brand in category
- Highlight: Critical gaps (POC showed 0% sustainability visibility)

#### 7. PR TARGET LIST (3-Tier System)

**Tier 1: URGENT (Red highlighting)**
- Outlets with 5+ total citations and <30% JH share
- High-frequency domains citing competitors but not JH
- Calculate "opportunity score" = (total_citations × (100 - jh_share%) / 100)
- Provide recommended action for each

**Tier 2: MEDIUM PRIORITY (Yellow)**
- Outlets with 30-60% JH share
- Growth opportunities to increase JH presence
- Calculate target share (e.g., aim for 75%)

**Tier 3: MAINTAIN (Green)**
- Outlets with >60% JH share
- "JH Advocates" - maintain relationships
- Show as success stories

#### 8. EARNED VS. OWNED MEDIA ANALYSIS
Visualize the 2.02:1 ratio:
- **Owned Media:** johnhardy.com citations (40 from JSON)
- **Earned Media:** Third-party mentions (81 from JSON)
- **Chart:** Pie chart or stacked bar
- **Insight:** Is 2:1 ratio healthy? Compare to industry benchmarks

Break down earned media by:
- Tier-1 luxury (Vogue, etc.)
- Tier-2 specialty (lifestyle, sustainability)
- Industry trade (jewelry publications)
- Retail partners
- Other

#### 9. PLATFORM CITATION PATTERNS
Analyze citation behavior by platform (from JSON):
- **ChatGPT:** 248 citations (31.9%)
- **Perplexity:** 311 citations (40.0%)
- **Gemini:** 174 citations (22.4%)
- **Claude:** 44 citations (5.7%)

For each platform:
- Success rate (100% for all from JSON)
- Average citations per query
- Top domain cited
- JH citation rate

**Strategic Insight:** Perplexity is the primary citation driver - optimize content for Perplexity

#### 10. DOMAIN CLASSIFICATION BREAKDOWN
From CITATION_DETAILS, group by domain_classification:
- luxury_fashion_tier1
- business_media
- jewelry_trade
- sustainability_media
- lifestyle_media
- brand_official
- competitor_official
- retail_partner
- news_media
- wiki_reference
- other

For each:
- Total citations
- % of total
- JH citations
- JH share within category

**Insight:** Where is JH strong vs. weak?

#### 11. CONTENT TYPE INTELLIGENCE
From CITATION_DETAILS, analyze by content_type:
- buying_guide
- product_review
- sustainability_content
- editorial
- owned_content
- news_article

**Questions to answer:**
- What content types get cited most?
- Which formats favor JH vs. competitors?
- Where should JH invest in content creation?

#### 12. STRATEGIC RECOMMENDATIONS SECTION

Create 3 alert boxes:

**IMMEDIATE ACTIONS (Red - Urgent)**
- Based on data, identify 4-5 urgent PR opportunities
- Example: "Target [outlet] with [X] total citations but 0% JH share"
- Specific, actionable recommendations

**MEDIUM-TERM STRATEGY (Blue - Info)**
- 3-6 month strategic initiatives
- Example: "Content partnership with Tier-1 luxury media"
- Category-specific strategies (sustainability, lab-grown)

**COMPETITIVE THREATS (Yellow - Warning)**
- Where competitors dominate
- Example: "Brilliant Earth owns 80% of sustainability query citations"
- Defensive positioning needs

#### 13. METHODOLOGY & DATA QUALITY
- 98/100 tests successful (98% completion rate)
- 777 citations captured
- 255 unique domains analyzed
- 25 queries × 4 platforms
- Gemini multi-key approach: 100% success rate
- Earned/owned ratio: 2.02:1

### STYLING REQUIREMENTS:

Use the NBA dashboard as visual inspiration but adapt:

**Colors:**
- Header gradient: `linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%)`
- Accent color for highlights: `#C0A080` (bronze/gold)
- Success/green: `#2D5016` (JH sustainability green)
- Warning: `#f59e0b`
- Danger: `#C9082A`

**Typography:**
- Clean, modern sans-serif (same as NBA example)
- Luxury feel - ample whitespace, elegant layout

**Interactive Elements:**
- Tabs for different data views
- Sortable tables (click column headers)
- Hover effects on cards
- Progress bars for visibility metrics
- Badge system for rankings

### DATA ANALYSIS INSTRUCTIONS:

1. **Calculate JH Overall Visibility:**
   - Count rows in BRAND_ANALYSIS_MATRIX where john_hardy_mentioned='Yes'
   - Divide by 98 (total successful tests)
   - This is JH's visibility rate

2. **Identify Top Competitors:**
   - Aggregate COMPETITIVE_CONTEXT_MATRIX by brand
   - Sum brand_specific_citations for each
   - Rank by total citations

3. **Find PR Target Outlets:**
   - From MEDIA_INFLUENCE, filter where:
     - citation_count >= 5 AND
     - (john_hardy_citations / citation_count) < 0.30
   - These are high-frequency outlets with low JH presence

4. **Analyze Category Performance:**
   - Group BRAND_ANALYSIS_MATRIX by category
   - For each category, calculate % where john_hardy_mentioned='Yes'
   - Identify categories with <40% visibility (critical gaps)

5. **Earned Media Breakdown:**
   - From CITATION_DETAILS where john_hardy_mentioned='Yes'
   - Count by domain_classification
   - Exclude domain_classification='brand_official' for earned media

### OUTPUT REQUIREMENTS:

1. **Single HTML file** (self-contained, no external dependencies)
2. **Responsive design** (works on desktop and mobile)
3. **Interactive JavaScript** for tabs, sorting, filtering
4. **Data embedded** in JavaScript arrays (not separate files)
5. **Professional presentation** quality (client-ready)

### CRITICAL FOCUS AREAS:

Based on proof-of-concept findings, emphasize:
- **Sustainability gap** (POC showed 0% visibility)
- **Lab-grown diamond awareness** (POC showed 0% visibility)
- **Tier-1 luxury media presence** (only 3 outlets identified)
- **Competitive positioning** (Brilliant Earth/Vrai dominance)
- **Earned media opportunities** (81 earned vs 40 owned - can we improve?)

### EXAMPLE STRATEGIC INSIGHT TO INCLUDE:

If data shows Vogue cited competitors 15 times but John Hardy 0 times:
> "**URGENT PR TARGET:** Vogue.com has 15 total citations across luxury jewelry queries but 0 John Hardy mentions. Given JH's sustainability positioning and artisan craftsmanship, this represents a critical earned media gap. Recommended action: Pitch Vogue fashion editors on JH's Bali workshop sustainability story + lab-grown diamond launch."

### FINAL CHECKLIST:

- [ ] All 5 data files analyzed
- [ ] 777 citations accounted for
- [ ] 255 domains mapped
- [ ] Top 30 media outlets ranked
- [ ] Competitor citations vs. JH calculated
- [ ] PR targets identified (3 tiers)
- [ ] Category performance breakdown (6 categories)
- [ ] Earned vs. owned visualization
- [ ] Platform citation patterns analyzed
- [ ] Strategic recommendations provided
- [ ] John Hardy brand colors implemented
- [ ] Interactive elements functional
- [ ] Professional, client-ready presentation

Create the dashboard now. Make it comprehensive, data-driven, and actionable for John Hardy's PR and marketing teams.

---

## ADDITIONAL CONTEXT FOR CLAUDE:

The dashboard should help John Hardy's team answer:
1. Where do we have visibility vs. competitors?
2. Which media outlets should we target for PR?
3. Are we winning the sustainability narrative?
4. Is our lab-grown diamond line visible to AI?
5. What content types should we create?
6. Which platforms should we optimize for?
7. What's our earned vs. owned media balance?
8. Where are the critical gaps vs. Brilliant Earth/Vrai?

The output should be a strategic tool for quarterly planning and PR prioritization.

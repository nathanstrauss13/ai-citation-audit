# NBA Streaming Options Citation Analysis
## Amazon Prime Competitive Intelligence - Full Data Collection Protocol

**Strategic Objective:** Measure how AI platforms recommend NBA streaming options to inform Amazon PR strategy for increasing Amazon Prime Video's share of voice through earned media and owned content optimization.

---

## 📋 Overview

This audit systematically tests 10 streaming-focused queries across 4 AI platforms to understand:
- How AI platforms volunteer streaming services WITHOUT prompting
- How platforms present services when EXPLICITLY asked
- Which media outlets drive recommendations
- Where Amazon needs PR/content strategy support

### Key Metrics
- **40 total AI prompts** (10 queries × 4 platforms)
- **6 service-agnostic queries** (tests unprompted recommendations)
- **4 service-specific queries** (tests prompted explanations)
- **3 CSV outputs + JSON summary**

---

## 🎯 Query Protocol

### Query Set A: Service-Agnostic Core Queries (6 queries)
*Tests which services AI platforms volunteer without prompting*

1. "How can I stream NBA games online?"
2. "What's the best way to watch NBA games without cable?"
3. "NBA streaming options comparison"
4. "Where to watch NBA games 2025-2026 season"
5. "Best streaming service for NBA fans"
6. "How to watch NBA games on streaming platforms"

### Query Set B: Service-Specific Queries (4 queries)
*Tests how platforms present services when explicitly asked*

7. "How do I get NBA League Pass?"
8. "Can I watch NBA games on Amazon Prime?"
9. "Is NBA League Pass worth it compared to YouTube TV?"
10. "Hulu vs NBA League Pass for watching basketball"

---

## 🚀 Execution

### Prerequisites
```bash
# Ensure all API keys are in .env file
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### Run Complete Audit
```bash
python run_nba_streaming_audit.py
```

**Estimated Time:** 2-3 hours for complete 40-prompt collection

### Rate Limiting
- 2-4 second delay between platform queries
- Automatic rate limit handling
- Error recovery with empty result placeholders

---

## 📊 Output Files

All files generated in `case_studies/nba_streaming/` with timestamp:

### 1. NBA_STREAMING_QUERY_MATRIX_[timestamp].csv
**Primary competitive intelligence file**

**Columns:**
- `query_id` - A1-A6 (service-agnostic), B1-B4 (service-specific)
- `query_text` - Exact query tested
- `query_type` - "service_agnostic" or "service_specific"
- `engine` - Platform name (ChatGPT, Claude, Perplexity, Gemini)
- `nba_leaguepass_mentioned` - Yes/No
- `nba_leaguepass_position` - First/Prominent/Secondary/Buried/Not Present
- `amazon_prime_mentioned` - Yes/No
- `amazon_prime_position` - First/Prominent/Secondary/Buried/Not Present
- `youtube_tv_mentioned` - Yes/No
- `youtube_tv_position` - First/Prominent/Secondary/Buried/Not Present
- `hulu_mentioned` - Yes/No
- `hulu_position` - First/Prominent/Secondary/Buried/Not Present
- `other_services_mentioned` - Comma-separated (Sling TV, FuboTV, etc.)
- `primary_recommendation` - Which service is featured most favorably
- `total_citations` - Total count of sources
- `scraped_citations` - Count of visible URLs
- `inferred_citations` - Count of mentioned but not linked sources

**Position Scoring Rules:**
- **First:** Service mentioned in first sentence OR listed first
- **Prominent:** Service in top 3 mentions OR given most detail
- **Secondary:** Moderate detail mid-response
- **Buried:** Brief mention or listed last
- **Not Present:** Not mentioned

### 2. NBA_STREAMING_RAW_CITATIONS_[timestamp].csv
**Citation source intelligence file**

**Columns:**
- `citation_id` - Sequential (C001, C002, etc.)
- `query_id` - Links to query matrix
- `engine` - Platform name
- `citation_type` - scraped_url / inferred_source / inline_mention
- `domain` - Root domain (nba.com, espn.com, amazon.com, etc.)
- `classification` - Domain category (see below)
- `full_url` - Complete URL or "INFERRED"
- `service_supported` - Which streaming option this source recommends
- `citation_context` - Brief note on what source says

**Citation Type Guidance:**
- **scraped_url:** Platform provides clickable/visible URL
- **inferred_source:** Platform mentions source by name without link (e.g., "According to ESPN...")
- **inline_mention:** Platform states information without attribution

**Domain Classifications:**
- `league_official` - nba.com, nba.com/leaguepass
- `amazon_official` - amazon.com, primevideo.com, aboutamazon.com
- `streaming_official` - youtube.com, hulu.com, sling.com, fubo.tv
- `sports_media_tier1` - ESPN, The Athletic, SI, Bleacher Report (Premium/Subscription)
- `sports_media_tier2` - Fox Sports, CBS Sports, Yahoo Sports, NBC Sports (Major Networks)
- `tech_media` - CNET, TechRadar, The Verge, Wired
- `cord_cutting_media` - Cord Cutters News, Flixed, Streaming Better
- `mainstream_news` - NYT, Washington Post, USA Today
- `finance_business` - Forbes, WSJ, Bloomberg, CNBC
- `reference` - Wikipedia, Reddit, Quora
- `other` - Everything else

### 3. NBA_STREAMING_MEDIA_TRACKING_[timestamp].csv
**PR targeting intelligence file**

**Columns:**
- `media_outlet` - Domain name
- `total_citations` - Total times cited across all queries
- `scraped_count` - Visible URL citations
- `inferred_count` - Inferred source citations
- `services_favored` - Comma-separated services this outlet supports
- `amazon_mention_count` - Times outlet mentioned Amazon Prime
- `leaguepass_mention_count` - Times outlet mentioned NBA League Pass
- `queries_appeared_in` - Which queries cited this outlet
- `engines_citing` - Which platforms cited this outlet
- `sample_urls` - Up to 3 example URLs

**Purpose:** Identify which media outlets drive streaming recommendations and which services they favor. Critical for Amazon PR targeting.

### 4. NBA_STREAMING_AUDIT_SUMMARY_[timestamp].json
**Executive summary with key metrics**

Contains:
- Audit metadata (timestamp, query counts, platforms)
- Share of voice analysis (mention rates by service)
- Citation intelligence (total citations, type breakdown)
- Media outlet intelligence (unique outlets, top 10)
- Strategic insights (visibility gaps, opportunities)

---

## 📈 Strategic Analysis Framework

### 1. Share of Voice Analysis
**Service-Agnostic Queries (A1-A6):** When users don't specify a service:
- What % mention Amazon Prime unprompted?
- What % mention NBA League Pass first?
- What % mention YouTube TV / Hulu?
- **Gap Analysis:** Where Amazon needs earned media to increase unprompted mentions

**Service-Specific Queries (B1-B4):** When directly asked about services:
- How thoroughly do platforms explain Amazon Prime option?
- What citations support Amazon Prime explanations?
- Are platforms presenting accurate information about Amazon's NBA offering?

### 2. Citation Source Intelligence
**Which outlets drive Amazon mentions?**
- Is Amazon's own content (amazon.com, aboutamazon.com) being cited?
- Which sports media outlets mention Amazon?
  - **Tier 1 Premium:** ESPN, The Athletic, SI - high-value targets for thought leadership
  - **Tier 2 Networks:** Fox Sports, CBS Sports, Yahoo Sports, NBC Sports - broad reach
- Which mainstream news outlets mention Amazon? (NYT, WashPost - legitimacy angle)
- Which tech/streaming media outlets mention Amazon?
- Are there citation gaps where competitors have coverage but Amazon doesn't?

**Which outlets favor competitors?**
- Which sources primarily recommend NBA League Pass?
- Which sources favor YouTube TV or Hulu?
- What narratives do these sources use?

### 3. Platform Variance
- Which AI platforms are most favorable to Amazon?
- Which platforms under-represent Amazon?
- Are there platform-specific strategies needed?

### 4. Content Gap Analysis
**Where Amazon needs earned media:**
- Query types where Amazon has low/no mentions
- Media outlets that don't cite Amazon
- Competitor advantages (exclusive content, established reputation)

**Where Amazon needs owned content optimization:**
- Amazon.com SEO for NBA streaming queries
- Prime Video landing pages for NBA content
- Press release distribution and pickup

---

## 🎯 Success Criteria

This data collection succeeds when Amazon PR team can answer:

1. **Where do we win?** Which queries/platforms favor Amazon Prime?
2. **Where do we lose?** Which queries/platforms under-represent Amazon?
3. **Who helps us win?** Which media outlets cite Amazon favorably?
4. **Where are the gaps?** Which outlets cover competitors but not Amazon?
   - **Tier 1 gaps:** ESPN, The Athletic, SI not mentioning Amazon?
   - **Tier 2 gaps:** Fox/CBS/Yahoo/NBC Sports coverage gaps?
   - **Mainstream gaps:** NYT, WashPost missing Amazon angle?
5. **What's our narrative?** How are we positioned vs "official" League Pass vs "value" options?
6. **Where do we invest?** Earned media targets vs owned content optimization?

---

## 📊 Post-Collection: Claude Dashboard Request

After completing data collection, upload the 3 CSV files to Claude with this prompt:

```
Create an NBA Streaming Citation Analysis dashboard for Amazon PR team using uploaded CSVs.

Strategic Focus:
- Competitive positioning: Amazon Prime Video vs NBA League Pass vs YouTube TV vs Hulu
- Share of voice in service-agnostic queries (unprompted mentions)
- Citation source analysis: which media outlets drive recommendations?
  - Sports Media Tier 1: ESPN, The Athletic, SI, Bleacher Report
  - Sports Media Tier 2: Fox Sports, CBS Sports, Yahoo Sports, NBC Sports
  - Mainstream News: NYT, Washington Post
  - Tech/Streaming Media: CNET, TechRadar, The Verge, Cord Cutters News
- Platform-specific strategies: Claude, Perplexity, ChatGPT, Gemini performance
- Content gaps: where Amazon needs earned media vs owned content optimization

Analysis Requirements:
1. Separate metrics for service-agnostic (A1-A6) vs service-specific queries (B1-B4)
2. Amazon Prime positioning analysis (First/Prominent/Not Present rates)
3. Media outlet targeting priorities based on citation patterns BY TIER
4. Competitor advantages to counter
5. Platform-by-platform recommendation strategies

Key Metrics to Highlight:
- 40 LLM prompts tested
- % service-agnostic queries mentioning Amazon Prime unprompted
- % queries where Amazon Prime is mentioned first vs competitors
- Top media outlets citing Amazon Prime (or NOT citing it - gaps to close)
- Media tier analysis: Tier 1 vs Tier 2 vs Mainstream coverage patterns
- Citation type breakdown (scraped URLs vs inferred sources by platform)

Deliverable Format:
- Executive summary with Amazon's current competitive position
- Detailed query-level performance with actual citations
- Media targeting recommendations for PR team BY TIER
- Content strategy recommendations (earned vs owned)
- Platform-specific optimization strategies

Brand Colors: Amazon orange (#FF9900), NBA blue (#17408B), NBA red (#C8102E)
```

---

## 🔍 Technical Implementation

### Service Detection Logic
```python
# Services tracked
- NBA League Pass (patterns: "nba league pass", "league pass")
- Amazon Prime Video (patterns: "amazon prime video", "amazon prime", "prime video")
- YouTube TV (pattern: "youtube tv")
- Hulu Live TV (patterns: "hulu live tv", "hulu + live tv", "hulu live")
```

### Position Classification
```python
# First: Service in first sentence OR first 200 chars
# Prominent: Top 3 mentions OR highlighted section
# Secondary: Moderate detail mid-response
# Buried: Brief mention or listed last
# Not Present: Not mentioned
```

### Citation Extraction
```python
# Perplexity: Direct citation array from API
# All platforms: URL regex extraction from response text
# Claude/Gemini: Inferred source detection ("According to X...")
```

---

## ⚠️ Known Limitations

1. **Claude/Gemini Citation Limitation:** These platforms often don't provide direct URLs, resulting in higher inferred citation counts
2. **Rate Limits:** Some platforms have stricter rate limits; built-in delays handle this
3. **Response Variability:** AI responses may vary slightly between runs; position scoring captures general patterns
4. **Content Freshness:** AI platforms may have different training cutoffs affecting streaming service awareness

---

## 📝 Example Output Rows

### Query Matrix Example:
```csv
query_id,query_text,query_type,engine,nba_leaguepass_mentioned,nba_leaguepass_position,amazon_prime_mentioned,amazon_prime_position,youtube_tv_mentioned,youtube_tv_position,hulu_mentioned,hulu_position,other_services_mentioned,primary_recommendation,total_citations,scraped_citations,inferred_citations

A1,"How can I stream NBA games online?",service_agnostic,Claude,Yes,First,Yes,Prominent,Yes,Prominent,Yes,Secondary,"Sling TV,FuboTV",NBA League Pass,15,0,12

B2,"Can I watch NBA games on Amazon Prime?",service_specific,Perplexity,Yes,Prominent,Yes,First,No,Not Present,No,Not Present,,Amazon Prime Video,8,8,0
```

### Raw Citations Example:
```csv
citation_id,query_id,engine,citation_type,domain,classification,full_url,service_supported,citation_context

C001,A1,Perplexity,scraped_url,nba.com,league_official,https://www.nba.com/watch,NBA League Pass,"Official NBA League Pass information"

C002,A1,Claude,inferred_source,espn.com,sports_media_tier1,INFERRED,Multiple,"According to ESPN, viewers can access games via multiple platforms"

C005,B2,Perplexity,scraped_url,amazon.com,amazon_official,https://www.amazon.com/nba,Amazon Prime Video,"Amazon Prime Video includes Thursday Night Basketball"
```

### Media Tracking Example:
```csv
media_outlet,total_citations,scraped_count,inferred_count,services_favored,amazon_mention_count,leaguepass_mention_count,queries_appeared_in,engines_citing,sample_urls

espn.com,18,12,6,Multiple,4,8,"A1,A2,A3,A5,B1,B3","Claude,Perplexity,ChatGPT","https://espn.com/nba/story1 | https://espn.com/nba/story2"

amazon.com,6,4,2,Amazon Prime Video,6,0,"A1,A3,B2","Perplexity,Claude","https://amazon.com/nba | https://primevideo.com"

theathletic.com,12,8,4,Multiple,3,5,"A1,A2,A4,A6","Claude,Perplexity","https://theathletic.com/nba-streaming"
```

---

## 🛠️ Troubleshooting

### API Key Issues
```bash
# Verify keys are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Keys loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Rate Limit Errors
- Built-in 2-4 second delays between queries
- If still hitting limits, increase delays in code
- Script will add empty result rows and continue

### Platform-Specific Issues
- **Gemini:** May require API key rotation; using single key for now
- **Perplexity:** Most reliable for citation extraction
- **Claude:** High inferred citation count (doesn't provide URLs)
- **ChatGPT:** Using GPT-4o for better reasoning

---

## 📚 Related Documentation

- See task description for full protocol details
- Dashboard prompt template included above
- Media outlet tier classifications defined in code

---

## 🎓 Methodology Notes

**Why 40 prompts?**
- 10 queries × 4 platforms = comprehensive coverage
- Service-agnostic queries reveal unprompted mention rates
- Service-specific queries test accuracy when prompted
- Multiple platforms reveal consistency/variance

**Why these specific queries?**
- A1-A6 designed to be neutral (no service bias)
- B1-B4 designed to directly probe each major service
- Mix of casual ("how can I") and analytical ("comparison") language
- Real user intent patterns from search data

**Why these media tiers?**
- Tier 1 = Premium/subscription outlets with influence
- Tier 2 = Broad reach network sites
- Tech media = Streaming/cord-cutting angle
- Mainstream = Business/legitimacy angle
- Different PR strategies for each tier

---

**Version:** 1.0  
**Last Updated:** October 7, 2025  
**Maintainer:** AI Citation Audit Team

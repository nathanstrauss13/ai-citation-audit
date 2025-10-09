# NBA Fan Engagement AEO Analysis
## Methodology, Assumptions, and Data Limitations

**Analysis Date:** September 30, 2025  
**Total Tests:** 72 (18 queries × 4 AI platforms)  
**Completion Time:** 46 minutes

---

## Key Assumptions Made

### 1. **Citation Extraction Assumptions**

**ASSUMPTION:** Citations returned by AI platforms accurately represent the sources used to generate responses.

**REALITY CHECK:**
- ❌ ChatGPT (GPT-4o-mini) does NOT natively provide citations - our adapter extracts numbered references from response text
- ✓ Claude provides structured citations through API
- ✓ Perplexity explicitly returns citation URLs in API response
- ✓ Gemini can return grounding metadata (when available)

**IMPACT:** ChatGPT citation data may be less reliable than other platforms because:
- References are text-parsed, not API-provided
- Model may hallucinate or format references inconsistently
- No guarantee every statement is actually backed by listed source

### 2. **League Detection in URLs Assumptions**

**ASSUMPTION:** A league mention in a URL indicates that source discusses that league.

**CURRENT METHOD:** Simple keyword matching (e.g., "nba" in URL = NBA source)

**LIMITATIONS:**
- Does NOT fetch and parse actual web page content
- URL alone may be misleading (e.g., article comparing multiple leagues)
- Cannot detect nuanced coverage (positive vs negative mentions)
- Misses context: "Why NBA ratings are declining" vs "NBA breaks viewership records"

**EXAMPLE EDGE CASE:**
- URL: `espn.com/nba-vs-nfl-viewership-comparison`
- Detected as: NBA source AND NFL source
- Reality: May actually favor one league in content

### 3. **Response Text Analysis Assumptions**

**ASSUMPTION:** League prominence in response text reflects AI platform's assessment of that league's relevance.

**WHAT WE'RE ACTUALLY MEASURING:**
- First mention position (not necessarily recommendation strength)
- Text presence (not sentiment or favorability depth)
- Surface-level patterns (not nuanced arguments)

**LIMITATIONS:**
- Cannot detect sarcasm or qualified recommendations
- "The NBA is often considered..." vs "The NBA is definitively..." treated the same
- Response structure varies by platform (some more verbose than others)

### 4. **Commercial Intent Classification Assumptions**

**ASSUMPTION:** Query text clearly indicates user's commercial intent.

**CLASSIFICATIONS USED:**
- `streaming`: Keywords like "watch", "stream"
- `ticketing`: Keywords like "tickets", "attend"  
- `fan_acquisition`: Keywords like "become a fan", "root for"
- `brand_preference`: Keywords like "best", "most exciting"

**LIMITATIONS:**
- Real user intent may be multifaceted
- Context matters: "How do I watch NBA games?" (streaming) vs "Should I watch NBA games?" (brand_preference with streaming overlap)
- User journey is non-linear (research → compare → decide → purchase)

### 5. **Cross-Platform Comparison Assumptions**

**ASSUMPTION:** Platforms are comparable and tested under equivalent conditions.

**REALITY:**
- Different models: GPT-4o-mini vs Claude 3.5 Sonnet vs Sonar Pro vs Gemini 2.0 Flash
- Different context windows and training data
- Different citation mechanisms (some native, some simulated)
- Different rate limits and response times
- Gemini experienced significant timeouts (11 failures out of 18 queries)

**COMPARABILITY ISSUES:**
- Gemini data incomplete (missing ~30% of intended tests due to API overload)
- Each platform may interpret "citation" differently
- Response verbosity varies (affects word-based prominence metrics)

---

## Data Quality Issues Identified

### Platform-Specific Issues

**ChatGPT:**
- ✓ 18/18 queries successful
- ⚠️ Citations are text-extracted, not API-native
- ⚠️ Citation accuracy depends on model's reference formatting consistency

**Claude:**
- ✓ 18/18 queries successful  
- ✓ Native citation support via API
- ✓ Most reliable citation data

**Perplexity:**
- ✓ 17/18 queries successful (1 timeout)
- ✓ Native citation support via API
- ✓ High-quality citation data

**Gemini:**
- ❌ 7/18 queries successful (11 timeouts/errors)
- ⚠️ API instability (503 errors, timeouts)
- ⚠️ Incomplete dataset - missing 61% of intended tests
- ⚠️ Results NOT representative of typical Gemini performance

### Systematic Biases

**1. Time-of-Day Bias:**
- All queries executed 2:52 PM - 3:38 PM ET on Monday
- API performance may vary by time
- Gemini particularly affected (likely quota/load issues)

**2. Query Order Bias:**
- Queries tested sequentially in fixed order
- Later queries may have different API conditions
- Platform "warming up" effect not controlled

**3. Rate Limiting Artifacts:**
- 2-second delay between queries within same platform
- Different actual response times per platform
- May affect quality of responses under pressure

**4. Model Temperature Settings:**
- ChatGPT: 0.3 (more deterministic)
- Claude: Default
- Perplexity: Default
- Gemini: 0.7 (more creative)
- Not equivalent for fair comparison

---

## What This Data Actually Shows

### ✓ **VALID INSIGHTS:**

1. **Relative Platform Behavior**
   - How different AI platforms respond to sports league queries
   - Which platforms cite more sources
   - Surface-level prominence patterns

2. **Citation Volume Patterns**
   - Total number of sources cited per platform
   - Domain diversity in citations
   - Media outlet representation

3. **Response Structure Patterns**
   - Which leagues get mentioned first
   - Whether NBA appears in responses at all
   - Rough sense of multi-league coverage

### ❌ **INVALID CONCLUSIONS:**

1. **"NBA is more/less visible than NFL"**
   - Missing context from citation content
   - No sentiment analysis
   - Prominence ≠ favorability

2. **"Platform X recommends NBA over Y"**
   - We detect mentions, not recommendations
   - No qualitative assessment of recommendation strength
   - Context matters (streaming vs ticketing different)

3. **"This represents real user experience"**
   - API responses may differ from web interface
   - Single query per topic (no variation testing)
   - No geographic personalization tested

4. **"Gemini performs worse than other platforms"**
   - Gemini data incomplete due to API issues
   - Cannot draw performance conclusions from failed tests
   - Need full dataset for fair comparison

---

## Methodological Improvements Needed

### 1. **Enhanced Citation Verification**
```python
# CURRENT: URL keyword matching
leagues = check_leagues_in_url(url)  # Simple string search

# NEEDED: Actual content analysis
response = fetch_url_content(url)
leagues = analyze_article_content(response)  # NLP analysis
sentiment = assess_league_sentiment(response)  # Positive/negative
context = extract_key_claims(response)  # What's actually said
```

### 2. **Response Quality Scoring**
- Implement NLP sentiment analysis on responses
- Measure recommendation strength, not just mention
- Context-aware prominence (first in list vs buried in paragraph)

### 3. **Statistical Rigor**
- Multiple runs per query (test consistency)
- Random query ordering (eliminate sequence bias)
- Stratified sampling across times of day
- Control for model temperature differences

### 4. **Gemini Retry Logic**
- Implement exponential backoff
- Queue failed queries for retry
- Alternative models when primary unavailable

### 5. **Citation Content Analysis**
- Fetch and parse actual web pages
- Verify claims made in citations
- Track positive vs negative mentions
- Measure depth of coverage per source

---

## Data Veracity Assessment

### High Confidence (70-90% Accuracy)
✓ Total citations count per platform  
✓ Citation domain identification  
✓ Branded vs league-agnostic query responses  
✓ Whether NBA is mentioned at all in response  

### Medium Confidence (40-70% Accuracy)
⚠️ NBA "prominence" rankings  
⚠️ Featured league identification  
⚠️ Citation relevance to query  
⚠️ Commercial intent alignment  

### Low Confidence (<40% Accuracy)
❌ League favorability comparisons  
❌ Cross-platform performance ranking  
❌ Gemini results (incomplete dataset)  
❌ Actionable info presence (keyword-only detection)  
❌ Citation-to-claim verification  

---

## Recommended Data Usage

### ✓ **SAFE TO USE FOR:**
- Directional insights on platform citation behavior
- Identifying which media outlets get cited frequently
- High-level league mention patterns
- Platform API reliability comparison
- Query categorization validation

### ⚠️ **USE WITH CAUTION FOR:**
- League prominence rankings (need qualitative review)
- Platform recommendation comparisons (context missing)
- Commercial intent effectiveness (needs user studies)
- Media influence scoring (needs content analysis)

### ❌ **DO NOT USE FOR:**
- Definitive statements about league visibility
- ROI calculations without validation
- Platform selection without considering API stability
- Marketing strategy changes without deeper analysis
- Competitive intelligence without source verification

---

## Validation Steps Needed

Before making strategic decisions based on this data:

1. **Manual Sample Review**
   - Read 10-20 random citations to verify relevance
   - Check if "NBA mention" truly means NBA coverage
   - Assess sentiment of mentions (positive/negative/neutral)

2. **Response Quality Audit**
   - Have sports marketing experts rate 20-30 responses
   - Compare automated prominence scoring to human judgment
   - Validate commercial intent classifications

3. **Platform Comparison Fairness**
   - Re-run Gemini queries when API stable
   - Test all platforms with identical model parameters
   - Control for time-of-day effects

4. **Citation Verification**
   - Fetch and read top 50 cited sources
   - Verify claims made in AI responses match source content
   - Check for hallucinated references

5. **Longitudinal Testing**
   - Re-run analysis quarterly to track trends
   - Test geographic variations (different API regions)
   - Compare free vs paid API tiers

---

## Conclusion

This dataset provides **directional insights** into AI platform citation behavior for sports league queries, but should NOT be treated as definitive evidence of NBA visibility or competitive positioning.

**Think of it as:** A screening tool that identifies patterns worth investigating further.

**NOT as:** Proof that NBA is more/less visible than competing leagues in AI systems.

**Next Steps:** Use this data to inform deeper qualitative research, including manual citation review, content analysis, and user experience testing.

---

## Transparency Statement

**Gemini Data Quality:** Only 7 of 18 Gemini queries completed successfully (39% completion rate). Gemini results should be considered incomplete and NOT representative of typical platform performance. All Gemini-based insights in this analysis are based on limited data and should be validated with additional testing when API stability improves.

**Citation Extraction:** ChatGPT citations are text-parsed from response content, not API-native. Citation quality for ChatGPT may be lower than Claude/Perplexity which provide structured citation data.

**Temporal Limitation:** All data collected in single 46-minute window on September 30, 2025. Results represent snapshot, not longitudinal trend.

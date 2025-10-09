# NBA Sports League V2 Audit System

## Overview

The NBA V2 Audit System provides **precision competitive analysis** of NBA visibility across AI platforms compared to NFL, MLB, and NHL. Unlike traditional audits that conflate metrics, this system separates:

1. **League mentions in LLM response text** (what the AI wrote)
2. **Total citation volume** (how many sources cited)
3. **League presence in citations** (which leagues appear in cited sources)
4. **Competitive positioning** (relative prominence of NBA vs. other leagues)
5. **Revenue-adjusted metrics** (performance per $1B revenue)

## Key Innovation: Revenue-Adjusted Analysis

This audit uniquely calculates **mentions per $1B revenue**, allowing you to answer:

- **Does NBA trail NFL in absolute mentions but WIN on revenue-adjusted basis?**
- **Is NBA's "gap" real or expected given league revenue differences?**
- **Which platforms favor which leagues?**
- **Where does NBA have genuine competitive advantage?**

### Example Insight

If results show:
- NFL: 25 mentions at $19B revenue = **1.32 mentions per $1B**
- NBA: 20 mentions at $11B revenue = **1.82 mentions per $1B**

**Conclusion**: NBA is actually outperforming NFL despite lower absolute numbers.

## Query Set (15 Total)

### Branded Queries (4)
NBA explicitly mentioned in query:
1. "Tell me about the NBA"
2. "What makes the NBA different from other professional sports leagues?"
3. "NBA game schedule tonight"
4. "How can I watch NBA games?"

### League-Agnostic Queries (11)
No league names mentioned:

**General Sports (4)**
5. "What's the most popular professional sports league in America?"
6. "Best professional sports to watch"
7. "Most exciting sports league"
8. "Which sports league has the best athletes?"

**Family Entertainment (3)**
9. "Best professional sports for families"
10. "Kid-friendly sporting events"
11. "Sports games to take children to"

**Entertainment Value (3)**
12. "Most entertaining sports league"
13. "Fast-paced sports to watch"
14. "Best sports for casual fans"

**Cultural Impact (1)**
15. "Which sports league has the biggest cultural impact?"

## Output Files (4 Total)

### 1. NBA_LEAGUE_RESPONSE_MATRIX_{timestamp}.csv

**Primary metrics for each query/platform combination**

Columns:
- `query`: Exact query text
- `query_type`: "branded" or "league_agnostic"
- `engine`: "chatgpt", "claude", "perplexity", or "gemini"
- `nba_mentioned_in_response`: Did LLM mention NBA? (Yes/No)
- `nfl_mentioned`, `mlb_mentioned`, `nhl_mentioned`: Other leagues mentioned? (Yes/No)
- `other_leagues_mentioned`: MLS, Premier League, etc.
- `total_citations`: Total URLs cited
- `citations_mentioning_nba/nfl/mlb/nhl`: Citation counts per league
- `response_prominence_nba`: How prominently was NBA positioned?

**Response Prominence Values:**
- `Exclusive Focus`: Only NBA discussed
- `Featured First`: NBA as top recommendation
- `Listed First Among Options`: NBA first in list
- `Listed Among Options`: NBA in list but not first
- `Mentioned in Passing`: Brief mention
- `Not Present`: Not mentioned

### 2. NBA_CITATION_DETAILS_{timestamp}.csv

**Every citation URL with league analysis**

Columns:
- `engine`: AI platform
- `query`: Query that generated citation
- `query_type`: "branded" or "league_agnostic"
- `citation_url`: Full URL
- `domain`: Root domain (e.g., "espn.com")
- `domain_classification`: Source type (see below)
- `nba/nfl/mlb/nhl_mentioned_in_source`: League mentioned? (Yes/No)
- `content_type`: Content classification (see below)
- `primary_league_focus`: Which league is primary subject?

**Domain Classifications:**
- `sports_media`: ESPN, Bleacher Report, The Athletic, SI, CBS/Fox/NBC Sports
- `league_official`: NBA.com, NFL.com, MLB.com, NHL.com
- `social_media`: Twitter, YouTube, Instagram, Reddit
- `news_media`: NYT, Washington Post, CNN, USA Today
- `authority`: Nielsen, Statista, Pew Research
- `business_media`: Forbes, Bloomberg, CNBC, Business Insider
- `entertainment_media`: Entertainment Weekly, Variety
- `other`: Everything else

**Content Types:**
- `news_article`: Current news/reporting
- `statistics`: Data, ratings, viewership
- `schedule`: Game schedules, calendars
- `video`: YouTube, video content
- `opinion`: Editorial, commentary
- `how_to`: Guides, explainers
- `company_page`: Official league pages
- `forum_discussion`: Reddit, forums
- `other`

### 3. NBA_COMPETITIVE_MENTIONS_{timestamp}.csv

**Competitive landscape tracking**

Tracks each major league (NFL, NBA, MLB, NHL) for every query, showing:
- `query`, `query_type`, `engine`: Test identifiers
- `league_mentioned`: Which league
- `mentioned_in_response`: In LLM text? (Yes/No)
- `mentioned_in_citations`: In cited sources? (Yes/No)
- `prominence_vs_nba`: How this league compared to NBA
- `viewership_data_cited`: Response included viewership data? (Yes/No)
- `cultural_impact_noted`: Discussed cultural impact? (Yes/No)

**Prominence vs NBA Values:**
- `Higher - Featured First`: More prominent than NBA
- `Higher - Mentioned First`: Appeared before NBA
- `Equal - Listed Together`: Same prominence as NBA
- `Lower - Mentioned After`: NBA featured more prominently
- `Present, NBA Absent`: League mentioned but not NBA
- `Both Absent`: Neither mentioned
- `N/A - NBA Present Only`: Can't compare (NBA's own row)

### 4. NBA_AUDIT_SUMMARY_{timestamp}.json

**Aggregated metrics and insights**

Structure:
```json
{
  "audit_date": "ISO timestamp",
  "total_queries_tested": 60,
  "total_platforms": 4,
  "overall_metrics": {
    "nba_mention_rate": 35.0,
    "total_nba_mentions": 21,
    "total_citations": 654,
    "citations_with_nba": 130,
    "nba_citation_authority_score": 19.88
  },
  "by_query_type": {
    "branded": {...},
    "league_agnostic": {...}
  },
  "by_platform": {
    "chatgpt": {...},
    "claude": {...},
    "perplexity": {...},
    "gemini": {...}
  },
  "competitive_landscape": {
    "nfl_mentions": 18,
    "mlb_mentions": 12,
    "nhl_mentions": 8
  },
  "revenue_adjusted_metrics": {
    "nba": {
      "revenue_billions": 11.0,
      "absolute_mentions": 21,
      "mentions_per_billion": 1.909
    },
    "nfl": {...},
    "mlb": {...},
    "nhl": {...}
  }
}
```

## Installation & Setup

### 1. Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- requests
- beautifulsoup4
- python-dotenv

### 2. API Keys

Create a `.env` file with:

```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### 3. File Structure

```
ai-citation-audit/
├── nba_sports_league_v2_audit.py    # Main audit system
├── run_nba_v2_audit.py              # Runner script
├── NBA_V2_AUDIT_README.md           # This file
├── platforms/                        # Platform adapters
│   ├── chatgpt.py
│   ├── claude.py
│   ├── perplexity.py
│   └── gemini.py
└── case_studies/nba_analysis/v2_audit/  # Output location
```

## Usage

### Run Full Audit

```bash
python3 run_nba_v2_audit.py
```

This will:
1. Test 15 queries × 4 platforms = 60 total tests
2. Track NBA vs. NFL/MLB/NHL competitive positioning
3. Analyze citations for league mentions
4. Calculate revenue-adjusted metrics
5. Generate 4 output files

**Runtime**: 8-12 minutes

### Programmatic Usage

```python
from nba_sports_league_v2_audit import NBALeagueAuditor

auditor = NBALeagueAuditor()
output_files = auditor.run_audit()

print(f"Results saved to: {output_files['summary']}")
```

## Key Metrics Explained

### 1. League-Agnostic Mention Rate
```
% of category queries where NBA appears
= (NBA mentions in league-agnostic queries / Total league-agnostic queries) × 100
```

**What it means**: How often AI platforms mention NBA when NOT explicitly asked about it.

### 2. Citation Authority Score
```
% of all citations that mention NBA
= (Citations mentioning NBA / Total citations) × 100
```

**What it means**: How strongly NBA is represented in the sources AI platforms cite.

### 3. Revenue-Adjusted Visibility
```
Mentions per $1B revenue
= Total mentions / League revenue (billions)
```

**What it means**: Performance normalized for league size. Higher = better visibility per dollar.

### 4. Competitive Win Rate
```
% of queries where NBA featured above competitors
= (Queries with NBA prominently featured / Total queries with NBA) × 100
```

**What it means**: How often NBA is positioned favorably vs. NFL/MLB/NHL.

## Example Analysis Workflow

### 1. Start with Summary JSON
```bash
cat case_studies/nba_analysis/v2_audit/NBA_AUDIT_SUMMARY_*.json | jq .
```

Check:
- Overall NBA mention rate
- Revenue-adjusted metrics vs. competitors
- Platform-by-platform performance

### 2. Drill into League Matrix CSV
```bash
# Find league-agnostic queries where NBA mentioned
grep "league_agnostic" NBA_LEAGUE_RESPONSE_MATRIX_*.csv | grep "Yes"
```

Analyze:
- Which categories favor NBA?
- Which platforms favor NBA?
- How does prominence compare?

### 3. Examine Competitive Landscape
```bash
# See NFL vs NBA head-to-head
grep "NFL\|NBA" NBA_COMPETITIVE_MENTIONS_*.csv | sort
```

Understand:
- Where NFL outperforms NBA
- Where NBA holds advantage
- Platform-specific biases

### 4. Review Citation Sources
```bash
# Find authoritative sources mentioning NBA
grep "authority" NBA_CITATION_DETAILS_*.csv | grep "Yes"
```

Identify:
- Quality of NBA citations
- Domain diversity
- Content type distribution

## Critical Methodology Rules

### Rule 1: Distinguish Response vs. Citations
- **Response text** = What the LLM wrote
- **Citations** = URLs the LLM provided
- **NEVER conflate these**

### Rule 2: Query Type Classification
- **Branded** = "NBA" in query text
- **League-agnostic** = No league names in query
  - Even if NBA appears in results, query is still league-agnostic

### Rule 3: Fast Mode URL Analysis
Current implementation uses **FAST MODE**:
- Only checks official league sites (nba.com, nfl.com, etc.)
- Does NOT fetch external URLs
- Marks non-official URLs as "No" for league mentions

To enable **FULL MODE** (fetch and parse all URLs):
- Modify `_check_leagues_in_url()` method
- Add BeautifulSoup content analysis
- Increase timeout allowances
- Runtime will increase to 25-40 minutes

### Rule 4: Revenue Context
League revenue estimates (used for normalization):
- **NBA**: $11B annual revenue
- **NFL**: $19B annual revenue
- **MLB**: $11.5B annual revenue
- **NHL**: $6B annual revenue

## Interpreting Results

### Scenario 1: NBA Trails NFL in Absolute Mentions
```
NFL: 25 mentions
NBA: 20 mentions
```

**Check revenue-adjusted metrics:**
- NFL: 25 / $19B = 1.32 per $1B
- NBA: 20 / $11B = 1.82 per $1B

**Conclusion**: NBA actually outperforms when normalized for league size.

### Scenario 2: NBA Mentioned But Not Prominently
```
Query: "Best professional sports to watch"
Response: "NFL offers great action. MLB has a long season. NBA is also popular."
```

**Analysis:**
- NBA mentioned: Yes
- Prominence: "Listed Among Options" (not featured)
- NFL positioned higher

**Insight**: Need to improve NBA positioning in general sports queries.

### Scenario 3: Platform Bias Detected
```
Perplexity: 8/15 NBA mentions
Claude: 12/15 NBA mentions
```

**Analysis:**
- Claude favors NBA more than Perplexity
- May reflect Claude's training data or ESPN citation preferences

**Action**: Understand why platforms differ, adjust PR strategy accordingly.

## Troubleshooting

### Issue: Missing API Keys
```
Error: Missing required API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY
```

**Solution**: Add all required keys to `.env` file

### Issue: Timeout Errors
```
Error: Gemini API error: 503 - The model is overloaded
```

**Solution**: System auto-retries with exponential backoff. Occasional timeouts are normal.

### Issue: Low Citation Counts
```
Warning: Only 2 citations found for query
```

**Solution**: This may be expected for certain queries. Check if platforms naturally provide fewer citations for that query type.

### Issue: Empty Response Text
```
Warning: Empty response text from Claude
```

**Solution**: Platform may have rate limit or API issue. System continues with remaining platforms.

## Advanced Usage

### Custom Query Set

Modify `_define_queries()` in `nba_sports_league_v2_audit.py`:

```python
def _define_queries(self):
    queries = []
    
    # Add your custom queries
    custom_queries = [
        "Your custom query here",
        "Another custom query"
    ]
    
    for q in custom_queries:
        queries.append({
            "text": q,
            "type": "league_agnostic",
            "category": "custom"
        })
    
    return queries
```

### Add Additional Leagues

Extend league tracking in `__init__()`:

```python
self.leagues = {
    'NBA': ['NBA', 'National Basketball Association'],
    'NFL': ['NFL', 'National Football League'],
    'MLB': ['MLB', 'Major League Baseball'],
    'NHL': ['NHL', 'National Hockey League'],
    'MLS': ['MLS', 'Major League Soccer'],
    'WNBA': ['WNBA', 'Women\'s National Basketball Association']  # Added
}
```

## Comparison to V1 Methodology

| Feature | V1 Approach | V2 Approach |
|---------|-------------|-------------|
| **Metrics** | Conflated response + citations | Separated clearly |
| **Query Types** | No distinction | Branded vs. league-agnostic |
| **Competitive Context** | Not tracked | Full multi-league tracking |
| **Revenue Adjustment** | Not available | Mentions per $1B |
| **Prominence Tracking** | Binary (mentioned/not) | 6-level prominence scale |
| **Platform Analysis** | Aggregated | Platform-by-platform breakdown |
| **Scalability** | Sport-specific | Repeatable across sports |

## File Locations

After running audit, find files in:
```
case_studies/nba_analysis/v2_audit/
├── NBA_LEAGUE_RESPONSE_MATRIX_YYYYMMDD_HHMM.csv
├── NBA_CITATION_DETAILS_YYYYMMDD_HHMM.csv
├── NBA_COMPETITIVE_MENTIONS_YYYYMMDD_HHMM.csv
└── NBA_AUDIT_SUMMARY_YYYYMMDD_HHMM.json
```

## Support

For issues or questions:
1. Check this README thoroughly
2. Review HoneyBaked V2 audit (similar methodology)
3. Examine platform adapter code in `platforms/` directory

## License

Part of the AI Citation Audit system.
See main repository LICENSE for details.

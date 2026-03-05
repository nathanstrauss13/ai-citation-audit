# AI Citation Audit

Multi-platform AI citation intelligence tool. Queries 5-10 LLM platforms in parallel and produces clean CSV data (full responses + citation URLs) for dashboard generation.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys in .env
cp .env.example .env  # then add your keys

# Run a 5-platform collection
python collect.py "Lululemon" -q "Best yoga pants,Lululemon vs Athleta"

# Run with 7 platforms
python collect.py "Lululemon" -q queries.csv -p 7

# Run all 10 platforms
python collect.py "Lululemon" -q queries.csv -p all

# Generate dashboard after collection
python collect.py "Lululemon" -q queries.csv --dashboard

# Generate Citation Explorer (interactive tree)
python collect.py "Lululemon" -q queries.csv --tree

# Generate explorer from existing CSV
python generate_citation_tree.py output/LULULEMON_CITATIONS_20260305.csv "Lululemon"
```

## Platforms

| Platform | Model | API Key | Set |
|----------|-------|---------|-----|
| ChatGPT | gpt-4o (Responses API + web_search GA) | `OPENAI_API_KEY` | Standard 5 |
| Claude | claude-sonnet-4 (web search tool) | `ANTHROPIC_API_KEY` | Standard 5 |
| Perplexity | sonar-pro (native search) | `PERPLEXITY_API_KEY` | Standard 5 |
| Gemini | gemini-2.5-flash (google search grounding) | `GOOGLE_API_KEY` | Standard 5 |
| Grok | grok-3-latest | `XAI_API_KEY` | Standard 5 |
| DeepSeek | deepseek-chat (V3) | `DEEPSEEK_API_KEY` | Extended 7 |
| Meta Llama | Llama-3.3-70B via Together.ai | `TOGETHER_API_KEY` | Extended 7 |
| Copilot | gpt-4o (Responses API + web_search GA) | `OPENAI_API_KEY` | Full 10 |
| Google AI Studio | gemini-2.5-flash (search grounding) | `GOOGLE_API_KEY` | Full 10 |
| You.com | Research API (native citations) | `YOU_API_KEY` | Full 10 |

## CLI Usage

```bash
python collect.py BRAND -q QUERIES [options]

Arguments:
  BRAND                    Brand name to audit

Options:
  -q, --queries            Queries CSV/JSON file, or inline comma-separated
  -p, --platforms {5,7,10,all}  Platform set (default: 5)
  -o, --output-dir         Output directory (default: output/)
  -c, --competitors        Comma-separated competitor names
  --dashboard              Generate HTML dashboard after collection
  --tree                   Generate Citation Explorer (interactive tree)
  --sequential             Sequential instead of parallel collection
  --max-workers N          Max parallel threads (default: 30)
```

## Query Input Formats

**CSV** (columns: query_id, query, category, query_type):
```csv
query_id,query,category,query_type
Q001,Best yoga pants for hot yoga,Product Discovery,unbranded
Q002,Lululemon vs Athleta,Brand Comparison,branded
```

**JSON**:
```json
[
  {"id": "Q001", "query": "Best yoga pants", "category": "Product", "query_type": "unbranded"},
  {"id": "Q002", "query": "Lululemon vs Athleta", "category": "Comparison", "query_type": "branded"}
]
```

**Inline** (auto-assigned IDs):
```bash
python collect.py "Brand" -q "query one,query two,query three"
```

## CSV Output Schema

All analytical inference (brand mentions, winners, competitors) is deferred to dashboard generation where Claude does it more accurately from the full output.

| Column | Description |
|--------|-------------|
| `query_id` | Unique query identifier |
| `query` | Exact query text sent to LLM |
| `query_type` | branded / unbranded |
| `category` | Query category |
| `persona` | Optional persona label (for Citation Explorer hierarchy) |
| `intent` | Optional intent label (for Citation Explorer hierarchy) |
| `engine` | Platform name |
| `search_enabled` | Yes/No - whether RAG/web search was detected |
| `full_output` | Complete LLM response text |
| `citation_urls` | Extracted URLs (newline-separated) |
| `citation_domains` | Extracted domains (newline-separated) |
| `timestamp` | ISO timestamp |

## Project Structure

```
ai-citation-audit/
├── collect.py                    # Unified CLI collector (start here)
├── generate_citation_tree.py     # Citation Explorer generator from CSV
├── platforms/                    # LLM platform adapters
│   ├── __init__.py              # Platform registry & loader (5/7/10/all)
│   ├── chatgpt.py               # OpenAI (Responses API + web_search GA + url_citation)
│   ├── claude.py                # Anthropic (web search tool)
│   ├── perplexity.py            # Perplexity (native search)
│   ├── gemini.py                # Google Gemini (google search grounding)
│   ├── grok.py                  # xAI Grok
│   ├── deepseek.py              # DeepSeek (native + Together.ai fallback)
│   ├── together_ai.py           # Meta Llama via Together.ai
│   ├── copilot.py               # Microsoft Copilot (Responses API + web_search GA)
│   ├── google_ai_studio.py      # Google AI Studio (search grounding)
│   └── youcom.py                # You.com (Research API + structured citations)
├── engines/                      # Dashboard rendering & analysis
│   ├── dashboard_v3.py          # Current dashboard renderer
│   ├── citation_tree_engine.py  # Citation Explorer (interactive tree)
│   ├── citation_classifier.py   # Adaptive citation classification
│   └── response_analyzer.py     # Claude-based response analysis
├── generate_dashboard_from_csv.py  # Dashboard generation from CSV
├── run_collection_job.py         # Streamlit job runner (wraps collect.py)
├── app.py                        # Streamlit web UI
├── pr_analysis_backend.py        # PR opportunity scoring
├── output/                       # Collection output (CSV + dashboards)
├── archive/                      # Historical scripts and data
│   ├── scripts/                 # Old client-specific collectors
│   └── data/                    # Historical CSVs and dashboards
└── requirements.txt
```

## Architecture

1. **`collect.py`** orchestrates everything: loads platform adapters, runs preflight health checks, executes queries in parallel with per-platform semaphores and retry logic, saves clean CSV output.

2. **`platforms/`** adapters each implement `get_citations(prompt) -> {"response": str, "citations": [...]}`. They handle API calls, response parsing, and citation extraction independently.

3. **Dashboard generation** (optional) uses `engines/dashboard_v3.py` and `engines/citation_classifier.py` to produce interactive HTML dashboards from the CSV data.

## Environment Variables

Required in `.env`:
```
# Standard 5
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
GOOGLE_API_KEY=AI...
XAI_API_KEY=xai-...

# Extended 7 (add these for -p 7)
DEEPSEEK_API_KEY=sk-...
TOGETHER_API_KEY=...

# Full 10 (add these for -p 10 / -p all)
# OPENAI_API_KEY already covers Copilot
# GOOGLE_API_KEY already covers Google AI Studio
YOU_API_KEY=ydc-...
```

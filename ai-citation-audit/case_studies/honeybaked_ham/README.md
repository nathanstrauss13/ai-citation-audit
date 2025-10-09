# HoneyBaked Ham Programmatic API Data Collection

## Overview

This project implements a precision methodology for AI citation analysis, specifically designed to capture brand mentions, citations, and competitive positioning for HoneyBaked Ham across multiple AI platforms.

## Methodology

The audit captures three key data points for 15 queries across 4 AI platforms (ChatGPT, Claude, Perplexity, Gemini):

1. **Brand Mention**: Detection of "HoneyBaked" or "HoneyBaked Ham" in LLM-generated text
2. **Citations**: Total number of URLs/sources cited by the LLM
3. **Brand in Citations**: Number of citations that actually mention HoneyBaked

### Query Categories

#### Branded Queries (3)
- Compare HoneyBaked Ham to Omaha Steaks for holiday meals
- What makes HoneyBaked Ham different from other spiral hams?
- Where can I find HoneyBaked Ham stores near me?

#### Brand-Agnostic Queries (12)

**Holiday Ham**
- What is the best ham for Thanksgiving dinner?
- What is the best ham for Christmas dinner?
- Best spiral cut ham brands
- Best mail-order hams for holidays

**Convenience/Ordering**
- What should I serve for Christmas dinner if I don't want to cook?
- What is the easiest holiday meal to order online?
- Last-minute Thanksgiving dinner options
- Where can I order a complete holiday meal?

**Gifting**
- Best holiday food gifts to ship
- What's the best food gift for the holidays?
- Premium food gifts for corporate clients

**Thought Leadership**
- Who are the top chefs in the holiday catering industry?

## Output Files

The script generates three CSV files:

1. **QUERY_RESPONSE_MATRIX.csv**
   - Captures what the LLM said and cited
   - Columns: query, query_type, engine, brand_mentioned_in_response, total_citations, citations_mentioning_brand, response_prominence, chef_tim_mentioned

2. **CITATION_DETAILS.csv**
   - Details of every citation URL
   - Columns: engine, query, query_type, citation_url, domain, domain_classification, honeybaked_mentioned_in_source, content_type

3. **COMPETITIVE_MENTIONS.csv**
   - Tracks competitor mentions
   - Columns: query, query_type, engine, competitor_mentioned, mentioned_in_response, mentioned_in_citations, prominence_vs_honeybaked

## Setup and Usage

### Prerequisites
- Python 3.8+
- pip
- (Optional) Virtual environment recommended

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/honeybaked-ham-audit.git
   cd honeybaked-ham-audit
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   - Copy `.env.example` to `.env`
   - Fill in your API keys for:
     * Perplexity
     * OpenAI (ChatGPT)
     * Anthropic (Claude)
     * Google Gemini

5. **Run the Audit**
   ```bash
   python run_honeybaked_ham_audit.py
   ```

### Alternative: One-Step Execution
```bash
python run_honeybaked_ham_audit.py
```
This script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Validate API keys
- Run the citation audit

## Dependencies

### Required
- requests
- python-dotenv

### Platform-Specific
- google-generativeai (Gemini)
- openai (ChatGPT)
- anthropic (Claude)

## Configuration Options

### Environment Variables
- `PERPLEXITY_API_KEY`: API key for Perplexity
- `OPENAI_API_KEY`: API key for ChatGPT
- `ANTHROPIC_API_KEY`: API key for Claude
- `GEMINI_API_KEY`: API key for Google Gemini
- `DEBUG`: Enable debug logging (True/False)
- `LOG_LEVEL`: Set logging verbosity (INFO, DEBUG, WARNING, ERROR)

### .env File
Use the `.env.example` as a template to configure your API access and logging preferences.

## Limitations and Considerations

### Technical Constraints
- API rate limits
- Potential variability in AI responses
- Citation verification challenges

### Mitigation Strategies
- **Error Handling**: 
  - Comprehensive retry mechanism with exponential backoff
  - Detailed error tracking and logging
  - Graceful handling of API failures
- **Logging**:
  - Structured logging with multiple output formats
  - Configurable log levels
  - Detailed event tracking
- **Citation Verification**:
  - URL accessibility checks
  - Content type validation
  - Fallback mechanisms for unreachable sources

### Advanced Features
- Automatic API key rotation
- Dynamic rate limit management
- Intelligent citation source evaluation

## Future Improvements

- Implement actual API calls for each platform
- Enhance error handling and logging
- Develop more sophisticated citation verification
- Create machine learning-based source credibility scoring

## Logging and Monitoring

### Log Configuration
- Supports multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Generates both human-readable and machine-parseable logs
- Configurable log file rotation

### Monitoring Capabilities
- Track API call success rates
- Monitor citation verification performance
- Capture detailed error diagnostics

## License

[Insert appropriate license]

## Contact

[Insert contact information]

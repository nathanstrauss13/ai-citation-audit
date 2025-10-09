# HoneyBaked Ham Citation Audit 🍖🤖

## Overview

The HoneyBaked Ham Citation Audit is a cutting-edge, precision-driven methodology for analyzing brand mentions and citations across multiple AI platforms. This project provides a comprehensive framework for understanding Generative Engine Optimization (GEO) strategies.

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python Version](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Project Goals

- Capture brand mentions across AI platforms
- Analyze citation patterns
- Provide insights into competitive positioning
- Support research in generative AI communication

## 🚀 Key Features

- **Multi-Platform Analysis**
  - ChatGPT
  - Claude
  - Perplexity
  - Gemini

- **Comprehensive Query Set**
  - 15 strategic queries
  - Branded and brand-agnostic approaches

- **Advanced Reporting**
  - Detailed CSV output
  - Brand mention tracking
  - Competitive analysis

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/honeybaked-ham-citation-audit.git
   cd honeybaked-ham-citation-audit
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   - Copy `.env.example` to `.env`
   - Add your API keys for:
     * Perplexity
     * OpenAI (ChatGPT)
     * Anthropic (Claude)
     * Google Gemini

## 🖥️ Usage

### Run the Audit
```bash
python run_honeybaked_ham_audit.py
```

### Configuration Options
Customize your audit using environment variables in `.env`:
- `DEBUG`: Enable detailed logging
- `LOG_LEVEL`: Set logging verbosity
- `MAX_RETRIES`: Configure API call retry attempts

## 📊 Output Files

The audit generates three primary CSV files:

1. **QUERY_RESPONSE_MATRIX.csv**
   - Brand mentions
   - Citation counts
   - Response prominence

2. **CITATION_DETAILS.csv**
   - Detailed citation analysis
   - Domain classification
   - Content type

3. **COMPETITIVE_MENTIONS.csv**
   - Competitor tracking
   - Relative brand positioning

## 🧪 Testing

Run comprehensive test suite:
```bash
pytest test_honeybaked_ham_audit.py
```

## 🤝 Contributing

Interested in contributing? Great!

- Read our [CONTRIBUTING.md](CONTRIBUTING.md)
- Check the [TODO.md](TODO.md) for current priorities
- Join our community discussions

## 📈 Roadmap

- [ ] Complete AI platform integrations
- [ ] Enhance error handling
- [ ] Develop advanced citation verification
- [ ] Implement machine learning insights

## 📜 License

MIT License with additional research-focused terms.
See [LICENSE](LICENSE) for details.

## 🏆 Acknowledgments

- HoneyBaked Ham (for inspiring the research)
- AI Platform Providers
- Open Source Community

## 📞 Contact

[Your Contact Information]
- Email: 
- Twitter: 
- LinkedIn: 

---

**Disclaimer**: This is an independent research project not affiliated with HoneyBaked Ham or any AI platform.

# AI Citation Audit Tool

A powerful web application that analyzes brand visibility across AI platforms (ChatGPT, Claude, Perplexity, Gemini) and identifies PR opportunities for corporate communications professionals.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for AI platforms (see Configuration section)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/nathanstrauss13/ai-citation-audit.git
cd ai-citation-audit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with your API keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key
GEMINI_API_KEY=your_gemini_key
```

4. Run the application:
```bash
python web_app.py
```

5. Open your browser to `http://localhost:5000`

## 🎯 Features

### Core Functionality
- **Multi-Platform Analysis**: Queries ChatGPT, Claude, Perplexity, and Gemini simultaneously
- **Citation Extraction**: Identifies all sources cited by AI platforms
- **Competitive Intelligence**: Tracks competitor mentions and rankings
- **PR Opportunity Scoring**: Quantifies media outreach opportunities (0-100 score)
- **Outlet Classification**: Categorizes media outlets by tier and influence

### Advanced Features
- **Smart Query Generation**: AI-powered query variations for comprehensive coverage
- **Competitor Detection**: Automatically identifies industry competitors
- **Export Capabilities**: CSV reports for analysis and sharing
- **Real-time Processing**: Instant results with progress tracking

## 💼 Use Cases

### For PR Professionals
- Identify which media outlets AI systems cite for your industry
- Discover gaps where competitors are mentioned but your brand isn't
- Prioritize outreach to high-impact publications
- Track brand visibility trends over time

### For Marketing Teams
- Understand how AI systems perceive your brand
- Benchmark against competitors
- Identify content opportunities
- Measure PR campaign effectiveness

### For Agencies
- Provide data-driven recommendations to clients
- Demonstrate PR value with quantifiable metrics
- Identify new business opportunities
- Create competitive intelligence reports

## 📊 API Endpoints

### `/typeform-audit` (GET)
Returns the web interface

### `/typeform-audit` (POST)
Main API endpoint for audit operations

#### Actions:

**1. Detect Competitors**
```json
{
  "action": "detect_competitors",
  "brand": "Tesla"
}
```

**2. Generate Queries**
```json
{
  "action": "generate_queries",
  "brand": "Tesla",
  "query": "best electric vehicles",
  "competitors": ["Rivian", "Lucid Motors"]
}
```

**3. Run Audit**
```json
{
  "action": "run_audit",
  "brand": "Tesla",
  "competitors": ["Rivian", "Lucid Motors"],
  "prompts": ["What are the best electric vehicles?"]
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Required API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
GEMINI_API_KEY=AI...

# Optional Configuration
PORT=5000
DEBUG=False
```

### Platform Requirements
- At least one API key must be configured
- System will automatically use available platforms
- Fallback mechanisms ensure reliability

## 📈 PR Opportunity Scoring Algorithm

The system uses a sophisticated scoring algorithm:

```
Score = Citation_Frequency × Tier_Weight × Platform_Breadth × Recommendation_Bonus × Brand_Gap
```

- **Citation Frequency**: How often the outlet is cited
- **Tier Weight**: Editorial (10) > Trade (7) > Social (3) > Info (2)
- **Platform Breadth**: Bonus for citations across multiple AI platforms
- **Recommendation Bonus**: 2x multiplier for recommended resources
- **Brand Gap**: Higher score if competitors mentioned but not your brand

## 🚢 Deployment

### Deploy to Render

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service
4. Select this repository
5. Use the included `render.yaml` configuration
6. Add environment variables in Render dashboard
7. Deploy!

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set ANTHROPIC_API_KEY=your_key
git push heroku main
```

## 📁 Project Structure

```
ai-citation-audit/
├── web_app.py                 # Flask application
├── pr_analysis_backend.py     # PR scoring engine
├── simple_raw_auditor.py      # Core audit logic
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment config
├── README.md                 # This file
└── .env                      # Environment variables (create this)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask, OpenAI, Anthropic, and Google APIs
- Inspired by the need for better PR intelligence in the AI era
- Special thanks to corporate communications professionals who provided feedback

## 📞 Support

For questions or support, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for PR professionals navigating the AI revolution**

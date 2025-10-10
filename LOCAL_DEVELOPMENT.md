# Local Development Setup

## Prerequisites

1. **Python 3.11+** installed
2. **Redis** installed and running locally
3. **API Keys** configured in `.env` file

## Quick Start

### 1. Install Redis (if not already installed)

**macOS (using Homebrew):**
```bash
brew install redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
```

**Windows:**
Download from https://redis.io/download or use WSL

### 2. Start Redis Server

```bash
# Start Redis in the background
redis-server --daemonize yes

# Or start in foreground (for debugging)
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Python Dependencies

```bash
cd /path/to/ai-citation-audit-standalone
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create/update `.env` file:
```bash
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Local Redis (default)
REDIS_URL=redis://localhost:6379

# Flask
FLASK_SECRET_KEY=dev-secret-key-change-in-production
```

### 5. Start the Application

**Terminal 1 - Web Server:**
```bash
python web_app.py
```

The app will start at http://localhost:5010

**Terminal 2 - Background Worker:**
```bash
rq worker --url redis://localhost:6379 default
```

### 6. Access the Application

Open your browser to:
- **Main App**: http://localhost:5010/typeform-audit
- **Health Check**: http://localhost:5010/healthz

## Development Workflow

### Running Without Background Jobs (Fallback Mode)

If you don't want to run Redis/worker during development:

1. Stop Redis: `redis-cli shutdown`
2. Start only the web server: `python web_app.py`
3. The app will automatically fall back to synchronous execution with a 120s timeout

### Monitoring Background Jobs

**Check job queue:**
```bash
rq info --url redis://localhost:6379
```

**Monitor worker in real-time:**
```bash
rq worker --url redis://localhost:6379 default --verbose
```

**Clear all jobs (if needed):**
```bash
redis-cli FLUSHALL
```

### Testing the Full Flow

1. Visit http://localhost:5010/typeform-audit
2. Enter a brand name (e.g., "Tesla")
3. Let it generate a query suggestion
4. Review competitors (auto-detected)
5. Review generated queries
6. Click "Run Audit"
7. Watch the progress bar (should complete in 2-3 minutes)
8. View results dashboard

## Troubleshooting

### Redis Connection Issues

**Error**: `Failed to connect to Redis`

**Solution**:
```bash
# Check if Redis is running
redis-cli ping

# If not running, start it
redis-server --daemonize yes

# Check the port
redis-cli -p 6379 ping
```

### Worker Not Processing Jobs

**Check worker logs:**
```bash
rq worker --url redis://localhost:6379 default --verbose
```

**Verify job is queued:**
```bash
rq info --url redis://localhost:6379
```

### Port Already in Use

**Error**: `Address already in use: 5010`

**Solution**:
```bash
# Find process using port 5010
lsof -i :5010

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=5011 python web_app.py
```

### API Rate Limits

If you hit API rate limits during testing:
- Reduce the number of test queries
- Add delays between requests
- Use fewer competitors

## Project Structure

```
ai-citation-audit-standalone/
├── web_app.py              # Flask web server
├── worker.py               # Background job processor
├── simple_raw_auditor.py   # Audit logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── lead_audits/           # CSV output directory
└── LOCAL_DEVELOPMENT.md   # This file
```

## Development Tips

### Hot Reload

The Flask app runs with `debug=True` by default, so changes to `web_app.py` will auto-reload.

For worker changes, you need to restart the worker manually:
```bash
# Stop worker (Ctrl+C)
# Restart worker
rq worker --url redis://localhost:6379 default
```

### Debugging Background Jobs

Add logging to `worker.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Without Full Audit

To test the UI without running full audits:
1. Comment out the actual API calls in `simple_raw_auditor.py`
2. Return mock data
3. Test the frontend rendering

## Stopping Everything

```bash
# Stop web server: Ctrl+C in Terminal 1
# Stop worker: Ctrl+C in Terminal 2
# Stop Redis:
redis-cli shutdown
```

## Next Steps for Production

When ready to deploy again:
1. Commit your changes: `git add . && git commit -m "Your message"`
2. Push to GitHub: `git push origin main`
3. Render will auto-deploy
4. Unsuspend the Render services

## Cost Savings

**Local Development**: $0/month
**Render (Suspended)**: $0/month
**Render (Active)**: $14/month (Redis + Worker)

Keep services suspended during development to save costs!

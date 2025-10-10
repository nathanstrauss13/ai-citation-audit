# Render Environment Variables Setup Guide

## Issue: Claude Not Populating in Audit Results

If Claude is missing from your audit results, it's likely because the `ANTHROPIC_API_KEY` environment variable is not set on Render.

## Required Environment Variables

The app requires these API keys to query all 4 platforms:

| Variable Name | Platform | Required | Alternative Names Supported |
|--------------|----------|----------|----------------------------|
| `OPENAI_API_KEY` | ChatGPT | Yes | `OPEN_AI_API_KEY` |
| `ANTHROPIC_API_KEY` | Claude | Yes | `CLAUDE_API_KEY` |
| `PERPLEXITY_API_KEY` | Perplexity | Yes | `PPLX_API_KEY` |
| `GOOGLE_API_KEY` | Gemini | Yes | `GEMINI_API_KEY` |

## How to Set Environment Variables on Render

### Step 1: Go to Your Render Dashboard

1. Log in to [Render](https://dashboard.render.com/)
2. Click on your `ai-citation-audit` web service

### Step 2: Navigate to Environment Variables

1. Click on **"Environment"** in the left sidebar
2. You'll see a list of current environment variables

### Step 3: Add Missing API Keys

For each missing API key, click **"Add Environment Variable"** and enter:

#### Claude (Anthropic)
- **Key:** `ANTHROPIC_API_KEY`
- **Value:** Your Anthropic API key (starts with `sk-ant-api03-...`)

#### ChatGPT (OpenAI)
- **Key:** `OPENAI_API_KEY`
- **Value:** Your OpenAI API key (starts with `sk-proj-...`)

#### Perplexity
- **Key:** `PERPLEXITY_API_KEY`
- **Value:** Your Perplexity API key (starts with `pplx-...`)

#### Gemini (Google)
- **Key:** `GOOGLE_API_KEY`
- **Value:** Your Google API key (starts with `AIza...`)

### Step 4: Save and Redeploy

1. Click **"Save Changes"**
2. Render will automatically redeploy your service with the new environment variables
3. Wait 2-3 minutes for the deployment to complete

## Verifying the Fix

After redeployment, run a test audit:

1. Go to https://ai-citation-audit.onrender.com/typeform-audit
2. Enter a brand name (e.g., "Budweiser")
3. Enter a query (e.g., "What are the best light beers?")
4. Click "Generate Queries"
5. Click "Run Audit"

**Expected Result:** You should see responses from all 4 platforms:
- ✅ ChatGPT
- ✅ Claude
- ✅ Perplexity
- ✅ Gemini

## Checking Logs for Errors

If Claude is still missing after setting the environment variable:

1. Go to your Render dashboard
2. Click on **"Logs"** in the left sidebar
3. Look for error messages like:
   - `Claude API key not found (ANTHROPIC_API_KEY or CLAUDE_API_KEY)`
   - `Claude API error: 401` (invalid API key)
   - `Claude API error: 403` (insufficient permissions)
   - `Claude query failed: [error message]`

## Common Issues

### Issue 1: API Key Not Set
**Symptom:** Logs show "Claude API key not found"
**Solution:** Add `ANTHROPIC_API_KEY` to Render environment variables

### Issue 2: Invalid API Key
**Symptom:** Logs show "Claude API error: 401"
**Solution:** Verify your Anthropic API key is correct and active

### Issue 3: Rate Limiting
**Symptom:** Logs show "Claude API error: 429"
**Solution:** Wait a few minutes and try again, or upgrade your Anthropic API plan

### Issue 4: Model Access
**Symptom:** Logs show "Claude API error: 403" or "model not found"
**Solution:** Verify your API key has access to `claude-3-5-sonnet-20241022`

## Getting API Keys

If you don't have API keys yet:

### Anthropic (Claude)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys** section
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-api03-...`)

### OpenAI (ChatGPT)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-proj-...`)

### Perplexity
1. Go to https://www.perplexity.ai/settings/api
2. Sign up or log in
3. Generate an API key
4. Copy the key (starts with `pplx-...`)

### Google (Gemini)
1. Go to https://makersuite.google.com/app/apikey
2. Sign up or log in
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

## Testing Locally

To test with all API keys locally before deploying:

1. Copy `.env.example` to `.env`
2. Add your API keys to `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   ANTHROPIC_API_KEY=sk-ant-api03-...
   PERPLEXITY_API_KEY=pplx-...
   GOOGLE_API_KEY=AIza...
   ```
3. Run the app locally:
   ```bash
   python web_app.py
   ```
4. Test at http://localhost:5000/typeform-audit

## Support

If you're still having issues after following this guide:

1. Check the Render logs for specific error messages
2. Verify all 4 API keys are set correctly
3. Ensure your API keys have sufficient credits/quota
4. Try running a test audit with a simple query

The app now includes detailed logging for Claude API calls, so any errors will be visible in the Render logs.

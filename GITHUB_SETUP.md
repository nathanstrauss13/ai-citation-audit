# GitHub Repository Setup Instructions

## Creating Your Repository on GitHub

Since the GitHub CLI is not available, please follow these manual steps to create your repository:

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in the following details:
   - **Repository name**: `ai-citation-audit`
   - **Description**: "AI-powered tool for analyzing brand visibility across AI platforms and identifying PR opportunities"
   - **Visibility**: Public
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. Click "Create repository"

### Step 2: Connect Your Local Repository

After creating the repository on GitHub, you'll see a page with setup instructions. Run these commands in your terminal:

```bash
cd /Users/nathanstrauss/Desktop/ai-citation-audit-standalone

# Add the remote repository
git remote add origin https://github.com/nathanstrauss13/ai-citation-audit.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files:
   - `web_app.py` - Main Flask application
   - `pr_analysis_backend.py` - PR scoring engine
   - `simple_raw_auditor.py` - Core audit logic
   - `requirements.txt` - Dependencies
   - `render.yaml` - Deployment configuration
   - `README.md` - Documentation
   - And other supporting files

### Step 4: Deploy to Render (Optional)

Once your repository is on GitHub:

1. Go to https://render.com
2. Sign in with your GitHub account
3. Click "New +" → "Web Service"
4. Connect your `ai-citation-audit` repository
5. Render will automatically detect the `render.yaml` configuration
6. Add your API keys as environment variables:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `GEMINI_API_KEY`
7. Click "Create Web Service"

### Alternative: Quick Setup Commands

If you want to set up the remote repository quickly, here's a one-liner after creating the repo on GitHub:

```bash
git remote add origin https://github.com/nathanstrauss13/ai-citation-audit.git && git push -u origin main
```

## Repository URL

Your repository will be available at:
**https://github.com/nathanstrauss13/ai-citation-audit**

## Next Steps

1. ✅ Create repository on GitHub.com
2. ✅ Push your local code to GitHub
3. ✅ Verify all files are uploaded
4. 🚀 Deploy to Render (optional)
5. 📧 Share with stakeholders

## Troubleshooting

### If you get a "repository not found" error:
- Make sure you've created the repository on GitHub first
- Check that the repository name matches exactly

### If you get authentication errors:
- You may need to set up a Personal Access Token
- Go to GitHub Settings → Developer settings → Personal access tokens
- Generate a new token with `repo` scope
- Use the token as your password when pushing

### If you want to use SSH instead of HTTPS:
```bash
git remote set-url origin git@github.com:nathanstrauss13/ai-citation-audit.git
```

---

**Ready to go!** Your standalone repository is prepared and waiting to be pushed to GitHub.

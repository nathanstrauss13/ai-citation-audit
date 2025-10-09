# URGENT: Render Deployment Fix Required

## ⚠️ Current Issue
Render is still trying to run `gunicorn app:app` instead of `gunicorn web_app:app` despite the render.yaml being updated.

## 🔧 Solution Steps

### Option 1: Update Start Command in Render Dashboard (Recommended)

1. **Go to your Render Dashboard**
   - Navigate to: https://dashboard.render.com
   - Find your `ai-citation-audit` service

2. **Override the Start Command**
   - Click on your service
   - Go to "Settings" tab
   - Find "Start Command" section
   - Change from: `gunicorn app:app`
   - Change to: `gunicorn web_app:app`
   - Click "Save Changes"

3. **Manual Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - This will force Render to use the new configuration

### Option 2: Delete and Recreate the Service

If the above doesn't work:

1. **Delete the current service**
   - In Render dashboard, go to Settings
   - Scroll to bottom
   - Click "Delete Service"

2. **Create a new service**
   - Click "New +" → "Web Service"
   - Connect to `ai-citation-audit` repository
   - Render should now use the updated render.yaml
   - Add your API keys as environment variables
   - Deploy

### Option 3: Create a Procfile (Alternative Approach)

If Render continues to ignore render.yaml:

1. **Create a Procfile in your repository:**
   ```
   web: gunicorn web_app:app
   ```

2. **Push to GitHub:**
   ```bash
   cd /Users/nathanstrauss/Desktop/ai-citation-audit-standalone
   echo "web: gunicorn web_app:app" > Procfile
   git add Procfile
   git commit -m "Add Procfile for Render deployment"
   git push origin main
   ```

3. **Redeploy on Render**

## 📝 Why This Happens

Render may cache service configurations when first created. If you initially deployed with `app:app`, it might persist even after updating render.yaml. The dashboard override or service recreation ensures the new configuration is used.

## ✅ Verification

After applying the fix, you should see in the Render logs:
```
==> Running 'gunicorn web_app:app'
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:10000
```

Instead of the error:
```
ModuleNotFoundError: No module named 'app'
```

## 🚀 Quick Command Reference

To test after deployment:
```bash
# Check if the service is running
curl https://ai-citation-audit.onrender.com/typeform-audit

# Test the API
curl -X POST https://ai-citation-audit.onrender.com/typeform-audit \
  -H "Content-Type: application/json" \
  -d '{"action":"detect_competitors","brand":"Tesla"}'
```

---

**Priority Action:** Go to Render Dashboard → Settings → Start Command → Change to `gunicorn web_app:app`

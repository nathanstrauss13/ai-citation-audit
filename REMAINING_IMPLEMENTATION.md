# Remaining Implementation Steps

## Status: 70% Complete

### ✅ What's Done:
1. Created `worker.py` with background job functions
2. Updated `requirements.txt` with Redis + RQ
3. Fixed env loading in `web_app.py` (python-dotenv)
4. Added Redis connection and RQ queue initialization
5. Added `/job/<job_id>` endpoint for checking job status

### 🚧 What's Left:

## 1. Modify `/typeform-audit` endpoint (CRITICAL)

The `run_audit` action currently runs synchronously. It needs to:
- Queue the job instead of running it directly
- Return 202 Accepted with job ID
- Let the frontend poll `/job/<job_id>` for status

**Current code location:** Line ~1100 in web_app.py, in the `elif action == 'run_audit':` block

**Change needed:**
```python
elif action == 'run_audit':
    # Check if Redis/RQ is available
    if not redis_conn or not job_queue:
        # Fallback to synchronous execution
        try:
            brand = request.json.get('brand', '')
            competitors = request.json.get('competitors', [])
            prompts = request.json.get('prompts', [])
            
            from simple_raw_auditor import SimpleRawAuditor
            auditor = SimpleRawAuditor(brand, competitors, prompts)
            results = auditor.run_audit()
            
            # Save CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            safe_brand = "".join(c for c in brand if c.isalnum() or c in (' ', '-', '_')).strip()
            csv_filename = f"{safe_brand}_audit_{timestamp}.csv"
            csv_path = f"lead_audits/{csv_filename}"
            auditor.to_csv(csv_path)
            
            # Analyze results for dashboard
            analysis = analyze_audit_results(brand, competitors, results)
            analysis['csv_filename'] = csv_filename
            
            return analysis
        except Exception as e:
            logger.exception("run_audit failed")
            return {'error': str(e)}, 500
    
    # Queue the job for background processing
    try:
        brand = request.json.get('brand', '')
        competitors = request.json.get('competitors', [])
        prompts = request.json.get('prompts', [])
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Queue the job
        from worker import run_audit_job
        job = job_queue.enqueue(
            run_audit_job,
            brand,
            competitors,
            prompts,
            job_id,
            job_timeout='10m',  # 10 minute timeout
            result_ttl=3600  # Keep results for 1 hour
        )
        
        logger.info(f"Queued audit job {job.id} for brand {brand}")
        
        # Return 202 Accepted with job ID
        return jsonify({
            'status': 'queued',
            'job_id': job.id,
            'message': 'Audit queued for processing'
        }), 202
        
    except Exception as e:
        logger.exception("Failed to queue audit job")
        return {'error': str(e)}, 500
```

## 2. Update Frontend JavaScript

The `runAudit()` function needs to:
- Handle 202 response with job_id
- Poll `/job/<job_id>` every 2-3 seconds
- Update progress bar based on job status
- Show results when complete

**Location:** In the TPL_TYPEFORM_AUDIT template, around line 1500+

**Change the runAudit function to:**
```javascript
async function runAudit() {
    showScreen(5);
    startProcessingAnimation();
    
    try {
        const response = await fetch('/typeform-audit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: 'run_audit',
                brand: appState.brand,
                competitors: appState.competitors.filter(c => c.trim()),
                prompts: appState.queries.filter(q => q.trim())
            })
        });
        
        const data = await response.json();
        
        // Check if job was queued (202 response)
        if (response.status === 202 && data.job_id) {
            // Poll for job status
            pollJobStatus(data.job_id);
        } else if (response.ok) {
            // Synchronous response (fallback when Redis unavailable)
            appState.results = data;
            renderResults(data);
            showScreen(6);
        } else {
            throw new Error(data.error || `Request failed (${response.status})`);
        }
    } catch (error) {
        alert('Error running audit: ' + error.message);
        showScreen(4);
    }
}

async function pollJobStatus(jobId) {
    const pollInterval = 2000; // Poll every 2 seconds
    
    const poll = async () => {
        try {
            const response = await fetch(`/job/${jobId}`);
            const data = await response.json();
            
            if (data.status === 'completed') {
                // Job finished successfully
                appState.results = data.result;
                renderResults(data.result);
                showScreen(6);
            } else if (data.status === 'failed') {
                // Job failed
                throw new Error(data.error || 'Job failed');
            } else if (data.status === 'processing') {
                // Update progress if available
                if (data.progress) {
                    document.getElementById('timeProgressBar').style.width = data.progress + '%';
                    document.getElementById('progressPercent').textContent = Math.round(data.progress) + '%';
                }
                // Continue polling
                setTimeout(poll, pollInterval);
            } else {
                // Still queued, continue polling
                setTimeout(poll, pollInterval);
            }
        } catch (error) {
            alert('Error checking job status: ' + error.message);
            showScreen(4);
        }
    };
    
    // Start polling
    poll();
}
```

## 3. Update render.yaml

Add Redis service and worker:

```yaml
services:
  - type: web
    name: ai-citation-audit
    runtime: python
    buildCommand: pip install -r requirements.txt
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
      - key: REDIS_URL
        fromService:
          type: redis
          name: ai-citation-audit-redis
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PERPLEXITY_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: PPLX_API_KEY
        sync: false
  
  - type: redis
    name: ai-citation-audit-redis
    plan: starter
    ipAllowList: []
  
  - type: worker
    name: ai-citation-audit-worker
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: rq worker --url $REDIS_URL default
    envVars:
      - key: REDIS_URL
        fromService:
          type: redis
          name: ai-citation-audit-redis
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PERPLEXITY_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: PPLX_API_KEY
        sync: false
```

## 4. Update/Create Procfile (if needed for local dev)

```
web: gunicorn web_app:app --bind 0.0.0.0:$PORT --timeout 120
worker: rq worker --url $REDIS_URL default
```

## 5. Test Locally

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start worker
export REDIS_URL=redis://localhost:6379
rq worker default

# Terminal 3: Start web app
export REDIS_URL=redis://localhost:6379
python web_app.py
```

## 6. Deploy to Render

After making all changes:
1. Commit and push to GitHub
2. Render will automatically deploy
3. Verify Redis service is running
4. Verify worker service is running
5. Test an audit - should complete without timeout

## Quick Fix Alternative

If you want to deploy faster without background jobs, just increase the Gunicorn timeout in the web service start command in render.yaml:

```yaml
startCommand: gunicorn web_app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
```

This gives 5 minutes instead of 30 seconds, which should be enough for most audits.

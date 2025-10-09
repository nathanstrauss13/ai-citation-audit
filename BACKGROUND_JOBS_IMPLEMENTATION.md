# Background Jobs Implementation with Redis + RQ

## Overview
Implementing robust background job processing to handle long-running audit tasks that were timing out with Gunicorn's 30s worker timeout.

## Implementation Status

### ✅ Completed
1. Created `worker.py` with job functions:
   - `run_audit_job()` - Main audit processing
   - `detect_competitors_job()` - Competitor detection
   - `generate_queries_job()` - Query generation

2. Updated `requirements.txt`:
   - Added `redis==5.0.1`
   - Added `rq==1.15.1`

3. Updated `web_app.py`:
   - Fixed env loading (using python-dotenv instead of custom load_env)
   - Added Redis connection and RQ queue initialization
   - Imports: uuid, jsonify, Redis, Queue, Job

### 🚧 In Progress
4. Modify `/typeform-audit` endpoint to:
   - Queue long-running audits as background jobs
   - Return 202 Accepted with job ID immediately
   - Keep quick operations (detect_competitors, generate_queries) synchronous

5. Add `/job/<job_id>` endpoint:
   - Check job status (queued, started, finished, failed)
   - Return results when complete
   - Return progress updates while running

### ⏳ Remaining Tasks
6. Update `render.yaml`:
   - Add Redis service
   - Add worker service to process background jobs
   - Configure environment variables

7. Update/Create `Procfile`:
   - Web process: gunicorn with increased timeout
   - Worker process: rq worker

8. Update frontend JavaScript:
   - Poll `/job/<job_id>` for status
   - Display progress updates
   - Show results when complete

9. Testing:
   - Local testing with Redis
   - Deploy to Render
   - Verify no worker timeouts
   - Verify job processing works

10. Documentation:
    - Update README with new architecture
    - Document Redis setup
    - Document worker deployment

## Architecture

```
User Request → Flask App → Queue Job → Return 202 + Job ID
                              ↓
                         RQ Worker (background)
                              ↓
                         Process Audit
                              ↓
                         Store Results in Job
                              ↓
User Polls /job/<id> ← Job Status/Results
```

## Key Design Decisions

1. **Quick operations stay synchronous**: detect_competitors and generate_queries are fast (<5s) so no need to queue them
2. **Only audit runs in background**: The main audit (run_audit) takes 2-3 minutes, so it needs background processing
3. **Job status polling**: Frontend polls every 2-3 seconds for updates
4. **Progress tracking**: Worker updates job meta with progress information
5. **Result storage**: Results stored in Redis via RQ job, retrieved when complete

## Next Steps

Continue with modifying the `/typeform-audit` endpoint to queue the audit job and return immediately with a job ID.

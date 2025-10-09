#!/usr/bin/env python3
"""
Background worker for processing audit jobs using RQ (Redis Queue)
"""

import os
import logging
from datetime import datetime
from simple_raw_auditor import SimpleRawAuditor, infer_competitors, generate_queries

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_audit_job(brand, competitors, prompts, job_id):
    """
    Background job function to run the audit
    
    Args:
        brand: Brand name
        competitors: List of competitor names
        prompts: List of query prompts
        job_id: Unique job identifier
    
    Returns:
        dict: Job result with status and data
    """
    try:
        logger.info(f"[Job {job_id}] Starting audit for {brand}")
        logger.info(f"[Job {job_id}] Testing {len(prompts)} queries across 4 platforms")
        
        # Run the audit
        auditor = SimpleRawAuditor(brand, competitors, prompts)
        results = auditor.run_audit()
        
        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        safe_brand = "".join(c for c in brand if c.isalnum() or c in (' ', '-', '_')).strip()
        csv_filename = f"{safe_brand}_audit_{timestamp}.csv"
        
        # Ensure directory exists
        os.makedirs('lead_audits', exist_ok=True)
        csv_path = f"lead_audits/{csv_filename}"
        auditor.to_csv(csv_path)
        
        logger.info(f"[Job {job_id}] Audit complete. Saved to {csv_path}")
        
        # Return results
        return {
            'status': 'completed',
            'brand': brand,
            'competitors': competitors,
            'prompts': prompts,
            'results': results,
            'csv_filename': csv_filename,
            'timestamp': timestamp,
            'total_results': len(results)
        }
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Error running audit: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e),
            'brand': brand
        }


def detect_competitors_job(brand, job_id):
    """
    Background job to detect competitors
    
    Args:
        brand: Brand name
        job_id: Unique job identifier
    
    Returns:
        dict: Competitor analysis result
    """
    try:
        logger.info(f"[Job {job_id}] Detecting competitors for {brand}")
        
        openai_key = os.environ.get('OPENAI_API_KEY')
        result = infer_competitors(brand, openai_key)
        
        logger.info(f"[Job {job_id}] Competitor detection complete")
        
        return {
            'status': 'completed',
            'competitors': result.get('competitors', []),
            'industry': result.get('industry', 'Unknown')
        }
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Error detecting competitors: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


def generate_queries_job(brand, query, competitors, job_id):
    """
    Background job to generate queries
    
    Args:
        brand: Brand name
        query: User's general query
        competitors: List of competitors
        job_id: Unique job identifier
    
    Returns:
        dict: Generated queries result
    """
    try:
        logger.info(f"[Job {job_id}] Generating queries for {brand}")
        
        openai_key = os.environ.get('OPENAI_API_KEY')
        prompts = generate_queries(brand, query, competitors, openai_key)
        
        logger.info(f"[Job {job_id}] Query generation complete")
        
        return {
            'status': 'completed',
            'queries': prompts
        }
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Error generating queries: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }

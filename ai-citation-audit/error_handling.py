#!/usr/bin/env python3
"""
Error Handling and Retry Mechanism for HoneyBaked Ham Citation Audit

Provides robust error handling, retry logic, and exception tracking
for API interactions and data processing.
"""

import time
import functools
import requests
from typing import Callable, Any, Optional
from logging_config import get_logger

logger = get_logger()

class AuditError(Exception):
    """Base exception for HoneyBaked Ham Citation Audit errors"""
    pass

class APIError(AuditError):
    """Exception raised for API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(f"API Error: {message}")

class CitationVerificationError(AuditError):
    """Exception raised when citation verification fails"""
    def __init__(self, url: str, reason: str):
        self.url = url
        super().__init__(f"Citation Verification Failed: {url} - {reason}")

class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded"""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        super().__init__(message)

def retry(
    max_attempts: int = 3, 
    delay: float = 1.0, 
    backoff_factor: float = 2.0, 
    allowed_exceptions: tuple = (requests.RequestException, APIError)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_attempts (int): Maximum number of retry attempts
        delay (float): Initial delay between retries
        backoff_factor (float): Multiplier for increasing delay
        allowed_exceptions (tuple): Exceptions that trigger retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_attempt = 0
            current_delay = delay
            
            while current_attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    current_attempt += 1
                    
                    if current_attempt >= max_attempts:
                        logger.error(f"Max retry attempts reached for {func.__name__}")
                        raise
                    
                    logger.warning(
                        f"Attempt {current_attempt} failed: {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            raise AuditError(f"Failed to execute {func.__name__} after {max_attempts} attempts")
        
        return wrapper
    
    return decorator

def validate_api_response(response: requests.Response) -> dict:
    """
    Validate API response and handle potential errors
    
    Args:
        response (requests.Response): API response to validate
    
    Returns:
        dict: Parsed JSON response
    
    Raises:
        APIError: For HTTP errors or invalid responses
    """
    try:
        response.raise_for_status()
        
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = float(response.headers.get('Retry-After', 60))
            raise RateLimitError(
                "API rate limit exceeded", 
                retry_after=retry_after
            )
        
        # Parse JSON response
        data = response.json()
        
        # Additional validation can be added here
        if not data:
            logger.warning("Empty API response received")
        
        return data
    
    except requests.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        raise APIError(
            f"HTTP Error: {e}", 
            status_code=response.status_code
        )
    except requests.JSONDecodeError:
        logger.error("Failed to decode JSON response")
        raise APIError("Invalid JSON response")
    except Exception as e:
        logger.error(f"Unexpected API response error: {e}")
        raise APIError(str(e))

def verify_citation(url: str, timeout: int = 10) -> bool:
    """
    Verify a citation URL is accessible and contains relevant content
    
    Args:
        url (str): URL to verify
        timeout (int): Request timeout in seconds
    
    Returns:
        bool: Whether the citation is valid and accessible
    
    Raises:
        CitationVerificationError: If verification fails
    """
    try:
        response = requests.head(
            url, 
            allow_redirects=True, 
            timeout=timeout
        )
        
        # Check HTTP status
        if response.status_code != 200:
            raise CitationVerificationError(
                url, 
                f"Invalid HTTP status: {response.status_code}"
            )
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        valid_content_types = [
            'text/html', 
            'text/plain', 
            'application/pdf'
        ]
        
        if not any(ct in content_type for ct in valid_content_types):
            raise CitationVerificationError(
                url, 
                f"Invalid content type: {content_type}"
            )
        
        return True
    
    except requests.RequestException as e:
        logger.warning(f"Citation verification failed for {url}: {e}")
        return False
    except CitationVerificationError as e:
        logger.warning(str(e))
        return False

def log_audit_event(
    event_type: str, 
    details: dict, 
    level: str = 'INFO'
):
    """
    Log an audit event with structured information
    
    Args:
        event_type (str): Type of audit event
        details (dict): Event details
        level (str): Logging level
    """
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(
        f"Audit Event: {event_type}", 
        extra={'event_details': details}
    )

# Example usage demonstration
if __name__ == '__main__':
    @retry(max_attempts=3, delay=1.0)
    def example_api_call():
        """Simulated API call with potential failures"""
        import random
        if random.random() < 0.7:
            raise requests.RequestException("Simulated network error")
        return "Success!"
    
    try:
        result = example_api_call()
        print(result)
    except AuditError as e:
        print(f"Audit failed: {e}")

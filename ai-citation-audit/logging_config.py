#!/usr/bin/env python3
"""
Logging Configuration for HoneyBaked Ham Citation Audit

Provides a flexible, configurable logging system to track
the audit process, API interactions, and potential issues.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging(log_level=None, log_dir=None):
    """
    Configure logging for the HoneyBaked Ham Citation Audit
    
    Args:
        log_level (str, optional): Logging level. Defaults to env var or INFO.
        log_dir (str, optional): Directory to store log files. Defaults to audit output dir.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine log level
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create log directory if not exists
    log_dir = log_dir or os.path.join('case_studies', 'honeybaked_ham', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('honeybaked_ham_audit')
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler with Rotation
    log_file = os.path.join(log_dir, 'honeybaked_ham_audit.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # JSON Log Handler for structured logging
    json_log_file = os.path.join(log_dir, 'honeybaked_ham_audit_structured.jsonl')
    json_handler = logging.FileHandler(json_log_file)
    json_handler.setLevel(logging.INFO)
    json_formatter = JsonFormatter()
    json_handler.setFormatter(json_formatter)
    logger.addHandler(json_handler)
    
    return logger

class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Converts log records to JSON format for easier parsing
    """
    def format(self, record):
        """Convert log record to JSON"""
        import json
        from datetime import datetime
        
        log_record = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if exists
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)

def get_logger(name='honeybaked_ham_audit'):
    """
    Convenience method to get a logger instance
    
    Args:
        name (str, optional): Logger name. Defaults to 'honeybaked_ham_audit'.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

# Example usage
if __name__ == '__main__':
    logger = setup_logging(log_level='DEBUG')
    
    # Demonstration of logging levels
    logger.debug('Debug message')
    logger.info('Information message')
    logger.warning('Warning message')
    logger.error('Error message')
    
    try:
        1 / 0  # Intentional error to demonstrate exception logging
    except ZeroDivisionError:
        logger.exception('Caught an exception')

"""
Error Logger Module for Supabase

This module handles logging errors to Supabase execution_errors table.
All workflow errors are captured and stored for monitoring and debugging.
"""

import os
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorLogger:
    """
    Handles logging errors to Supabase execution_errors table.
    
    This class captures workflow errors and stores them in Supabase
    for monitoring, debugging, and error tracking.
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize the Error Logger.
        
        Args:
            supabase_url (str): Supabase project URL. If None, reads from SUPABASE_URL env var.
            supabase_key (str): Supabase API key. If None, reads from SUPABASE_KEY env var.
        """
        # Get credentials from parameters or environment variables
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.table_name = "execution_errors"
        
        # Initialize Supabase client if credentials are available
        self.client: Optional[Client] = None
        self.enabled = False
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                self.enabled = True
                logger.info("✓ Error logger initialized successfully")
            except Exception as e:
                logger.warning(f"⚠ Error logger initialization failed: {e}")
                self.enabled = False
        else:
            logger.warning("⚠ Error logger disabled: Supabase credentials not found")
    
    def generate_error_message_alt(self, 
                                   workflow_name: str,
                                   workflow_id: str,
                                   last_node: str,
                                   error_name: str,
                                   error_message: str,
                                   http_code: Optional[int] = None) -> str:
        """
        Generate a human-readable error message.
        
        Args:
            workflow_name: Name of the workflow
            workflow_id: ID of the workflow
            last_node: Last node that was executed
            error_name: Name/type of the error
            error_message: Detailed error message
            http_code: HTTP status code if applicable
        
        Returns:
            Formatted human-readable error message
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        message = f"""🚨 Workflow Execution Failed

Workflow: {workflow_name} (ID: {workflow_id or 'N/A'})
Last Node: {last_node}"""
        
        if http_code:
            message += f"\nHTTP Code: {http_code}"
        
        message += f"""

Error: {error_name}
Detail: {error_message}

Time: {timestamp}

Next Step: Review the error details and retry the workflow."""
        
        return message
    
    def log_error(self,
                  workflow_name: str = "pdf-generation-workflow",
                  workflow_id: Optional[str] = None,
                  execution_id: Optional[str] = None,
                  execution_url: Optional[str] = None,
                  error_name: str = "UnknownError",
                  error_message: str = "An error occurred",
                  last_node_executed: str = "unknown",
                  severity: str = "error",
                  category: str = "workflow",
                  full_error_data: Optional[Dict[str, Any]] = None,
                  http_code: Optional[int] = None) -> bool:
        """
        Log an error to Supabase execution_errors table.
        
        Args:
            workflow_name: Name of the workflow (default: pdf-generation-workflow)
            workflow_id: ID of the workflow (optional)
            execution_id: ID of the execution (optional)
            execution_url: URL of the execution (optional)
            error_name: Name/type of the error
            error_message: Detailed error message
            last_node_executed: Last node/step that was executed
            severity: Severity level (info, warning, error, critical)
            category: Error category (workflow, validation, database, api, etc.)
            full_error_data: Complete error data as dictionary (optional)
            http_code: HTTP status code if applicable (optional)
        
        Returns:
            bool: True if error was logged successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("⚠ Error logging skipped: Logger not enabled")
            return False
        
        try:
            # Generate unique error ID
            error_id = str(uuid.uuid4())
            
            # Generate execution ID if not provided
            if not execution_id:
                execution_id = str(uuid.uuid4())
            
            # Generate human-readable error message
            error_message_alt = self.generate_error_message_alt(
                workflow_name=workflow_name,
                workflow_id=workflow_id or "N/A",
                last_node=last_node_executed,
                error_name=error_name,
                error_message=error_message,
                http_code=http_code
            )
            
            # Prepare error data
            error_data = {
                "error_id": error_id,
                "workflow_name": workflow_name,
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "execution_url": execution_url,
                "error_name": error_name,
                "error_message": error_message,
                "last_node_executed": last_node_executed,
                "severity": severity,
                "category": category,
                "full_error_data": full_error_data or {},
                "error_message_alt": error_message_alt
            }
            
            # Insert into Supabase
            response = self.client.table(self.table_name).insert(error_data).execute()
            
            logger.info(f"✓ Error logged to Supabase (ID: {error_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to log error to Supabase: {e}")
            return False
    
    def log_workflow_error(self,
                          step_name: str,
                          error: Exception,
                          additional_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Convenience method to log workflow errors.
        
        Args:
            step_name: Name of the workflow step that failed
            error: The exception that was raised
            additional_context: Additional context data (optional)
        
        Returns:
            bool: True if error was logged successfully
        """
        error_name = type(error).__name__
        error_message = str(error)
        
        # Build full error data
        full_error_data = {
            "error_type": error_name,
            "error_str": error_message,
            "step": step_name
        }
        
        if additional_context:
            full_error_data.update(additional_context)
        
        # Determine severity based on error type
        severity = "error"
        if "critical" in error_message.lower() or "fatal" in error_message.lower():
            severity = "critical"
        elif "warning" in error_message.lower():
            severity = "warning"
        
        return self.log_error(
            error_name=error_name,
            error_message=error_message,
            last_node_executed=step_name,
            severity=severity,
            category="workflow",
            full_error_data=full_error_data
        )


# Example usage
def main():
    """
    Example usage of the ErrorLogger class.
    """
    print("=" * 60)
    print("ERROR LOGGER - TEST MODE")
    print("=" * 60)
    
    try:
        # Initialize error logger
        error_logger = ErrorLogger()
        
        if not error_logger.enabled:
            print("\n⚠ Error logger is not enabled")
            print("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
            return
        
        # Example 1: Log a test error
        print("\n📝 Logging test error...")
        success = error_logger.log_error(
            workflow_name="pdf-generation-workflow",
            error_name="TestError",
            error_message="This is a test error for demonstration",
            last_node_executed="test_step",
            severity="info",
            category="test",
            full_error_data={"test": True, "demo": "value"}
        )
        
        if success:
            print("✅ Test error logged successfully!")
        else:
            print("❌ Failed to log test error")
        
        # Example 2: Log a workflow error using convenience method
        print("\n📝 Logging workflow error using convenience method...")
        try:
            # Simulate an error
            raise ValueError("Sample validation error")
        except Exception as e:
            success = error_logger.log_workflow_error(
                step_name="data_validation",
                error=e,
                additional_context={"user_id": "12345", "data": "invalid"}
            )
            
            if success:
                print("✅ Workflow error logged successfully!")
            else:
                print("❌ Failed to log workflow error")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()


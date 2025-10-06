"""
Supabase Storage Uploader Module

This module handles uploading PDF files from the finalPdf folder to Supabase Storage.
It provides functionality to upload files to the 'offers' bucket and return the public URL.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseUploader:
    """
    Handles uploading PDF files to Supabase Storage.
    
    This class manages authentication with Supabase and provides methods to upload
    PDF files to the specified storage bucket.
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None, 
                 bucket_name: str = "offers"):
        """
        Initialize the Supabase Uploader.
        
        Args:
            supabase_url (str): Supabase project URL. If None, reads from SUPABASE_URL env var.
            supabase_key (str): Supabase API key (service_role or anon key). 
                               If None, reads from SUPABASE_KEY env var.
            bucket_name (str): Name of the storage bucket. Defaults to "offers".
        
        Raises:
            ValueError: If Supabase credentials are not provided or found in environment.
        """
        # Get credentials from parameters or environment variables
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.bucket_name = bucket_name
        
        # Validate credentials
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials not found. Please provide supabase_url and supabase_key "
                "or set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        # Initialize Supabase client
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✓ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def upload_pdf(self, file_path: str, destination_path: str = None) -> Dict[str, Any]:
        """
        Upload a PDF file to Supabase Storage.
        
        Args:
            file_path (str): Path to the PDF file to upload.
            destination_path (str): Destination path in the bucket. 
                                   If None, uses the original filename.
        
        Returns:
            Dict containing:
                - success (bool): Whether the upload was successful
                - url (str): Public URL of the uploaded file (if successful)
                - path (str): Storage path of the uploaded file (if successful)
                - error (str): Error message (if failed)
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist.
        """
        file_path = Path(file_path)
        
        # Validate file exists
        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        
        # Validate file is a PDF
        if file_path.suffix.lower() != '.pdf':
            error_msg = f"File is not a PDF: {file_path}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        
        # Determine destination path
        if destination_path is None:
            destination_path = file_path.name
        
        # Ensure destination path doesn't start with /
        destination_path = destination_path.lstrip('/')
        
        logger.info(f"📤 Uploading {file_path.name} to Supabase Storage...")
        logger.info(f"   Bucket: {self.bucket_name}")
        logger.info(f"   Destination: {destination_path}")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=destination_path,
                file=file_content,
                file_options={
                    "content-type": "application/pdf",
                    "upsert": "true"  # Overwrite if file exists
                }
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(destination_path)
            
            logger.info(f"✅ File uploaded successfully!")
            logger.info(f"   Public URL: {public_url}")
            
            return {
                "success": True,
                "url": public_url,
                "path": destination_path,
                "bucket": self.bucket_name,
                "file_name": file_path.name
            }
            
        except Exception as e:
            error_msg = f"Failed to upload file: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def upload_from_finalPdf_folder(self, pdf_filename: str, 
                                     base_folder: str = None) -> Dict[str, Any]:
        """
        Upload a PDF file from the finalPdf folder to Supabase Storage.
        
        Args:
            pdf_filename (str): Name of the PDF file in the finalPdf folder.
            base_folder (str): Base directory path. If None, uses current script directory.
        
        Returns:
            Dict containing upload result with success status, URL, and path.
        """
        if base_folder is None:
            base_folder = Path(__file__).parent
        else:
            base_folder = Path(base_folder)
        
        # Construct path to finalPdf folder
        final_pdf_folder = base_folder / "finalPdf"
        pdf_path = final_pdf_folder / pdf_filename
        
        # Upload the PDF
        return self.upload_pdf(str(pdf_path), destination_path=pdf_filename)
    
    def list_files(self) -> Optional[list]:
        """
        List all files in the bucket.
        
        Returns:
            List of files in the bucket, or None if failed.
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            logger.info(f"✓ Listed {len(files)} files from bucket '{self.bucket_name}'")
            return files
        except Exception as e:
            logger.error(f"❌ Failed to list files: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the bucket.
        
        Args:
            file_path (str): Path of the file in the bucket to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"✓ Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete file: {e}")
            return False


# Example usage and testing
def main():
    """
    Example usage of the SupabaseUploader class.
    """
    print("=" * 60)
    print("SUPABASE PDF UPLOADER - TEST MODE")
    print("=" * 60)
    
    try:
        # Initialize uploader
        uploader = SupabaseUploader()
        
        # Example: Upload a specific PDF from finalPdf folder
        # Replace with your actual PDF filename
        pdf_filename = "MUTTI4_0 Technologies.pdf"
        
        result = uploader.upload_from_finalPdf_folder(pdf_filename)
        
        if result["success"]:
            print("\n✅ Upload Successful!")
            print(f"   File: {result['file_name']}")
            print(f"   Bucket: {result['bucket']}")
            print(f"   Path: {result['path']}")
            print(f"   Public URL: {result['url']}")
        else:
            print(f"\n❌ Upload Failed: {result['error']}")
        
        # List all files in bucket
        print("\n📋 Listing files in bucket...")
        files = uploader.list_files()
        if files:
            for file in files:
                print(f"   - {file.get('name', 'Unknown')}")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 Please set up your Supabase credentials:")
        print("   1. Create a .env file in the project root")
        print("   2. Add the following variables:")
        print("      SUPABASE_URL=https://your-project.supabase.co")
        print("      SUPABASE_KEY=your-api-key")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()


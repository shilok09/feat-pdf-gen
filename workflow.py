"""
PDF Generation Workflow Orchestrator

This module orchestrates the complete PDF generation workflow:
1. Loads data from JSON file
2. Generates HTML files from templates using HTMLGenerator
3. Converts HTML files to PDF using PDFConverter
4. Uploads PDF to Supabase Storage (optional)
5. Cleans up local PDF after successful upload
"""

import asyncio
from pathlib import Path
from typing import Optional, List
import sys

from htmlGenerator import HTMLGenerator
from htmlToPdf import PDFConverter

# Try to import Supabase uploader (optional)
try:
    from supabaseUploader import SupabaseUploader
    SUPABASE_AVAILABLE = True
except (ImportError, ValueError) as e:
    SUPABASE_AVAILABLE = False
    print(f"⚠ Supabase uploader not available: {e}")

# Try to import Error Logger (optional)
try:
    from errorLogger import ErrorLogger
    ERROR_LOGGER_AVAILABLE = True
except (ImportError, ValueError) as e:
    ERROR_LOGGER_AVAILABLE = False
    print(f"⚠ Error logger not available: {e}")


class WorkflowOrchestrator:
    """
    Main workflow orchestrator for PDF generation.
    
    This class coordinates the entire process of generating PDFs from JSON data,
    managing the flow from data input through HTML generation to final PDF output.
    """
    
    def __init__(self, data_file_path: str = None, templates_folder: str = None,
                 html_output_folder: str = None, pdf_output_folder: str = None,
                 cleanup_html: bool = True, upload_to_supabase: bool = True,
                 delete_local_after_upload: bool = True):
        """
        Initialize the WorkflowOrchestrator.
        
        Args:
            data_file_path (str): Path to the JSON data file. Defaults to 'data.json'.
            templates_folder (str): Path to templates folder. If None, will auto-select based on OfferLanguage.
            html_output_folder (str): Path to HTML output folder. Defaults to 'htmlGenerated'.
            pdf_output_folder (str): Path to PDF output folder. Defaults to 'finalPdf'.
            cleanup_html (bool): Whether to delete HTML files after PDF generation. Defaults to True.
            upload_to_supabase (bool): Whether to upload PDF to Supabase Storage. Defaults to True.
            delete_local_after_upload (bool): Whether to delete local PDF after successful upload. Defaults to True.
        """
        self.base_dir = Path(__file__).parent
        self.data_file_path = Path(data_file_path) if data_file_path else self.base_dir / 'data.json'
        self.templates_folder = Path(templates_folder) if templates_folder else None
        self.html_output_folder = Path(html_output_folder) if html_output_folder else self.base_dir / 'htmlGenerated'
        self.pdf_output_folder = Path(pdf_output_folder) if pdf_output_folder else self.base_dir / 'finalPdf'
        self.cleanup_html = cleanup_html
        self.upload_to_supabase = upload_to_supabase
        self.delete_local_after_upload = delete_local_after_upload
        
        # Initialize components
        self.html_generator = None
        self.pdf_converter = None
        self.supabase_uploader = None
        self.error_logger = None
        self.generated_html_files: List[Path] = []
        self.generated_pdf_path: Optional[str] = None
        self.supabase_url: Optional[str] = None
    
    def validate_input(self) -> bool:
        """
        Validate that required input files exist.
        Template folder validation is deferred to HTMLGenerator as it auto-selects based on language.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        print("\n🔍 Validating input files...")
        
        if not self.data_file_path.exists():
            print(f"❌ Error: Data file not found: {self.data_file_path}")
            return False
        print(f"✓ Data file found: {self.data_file_path}")
        
        # If templates_folder is manually specified, validate it
        if self.templates_folder and not self.templates_folder.exists():
            print(f"❌ Error: Templates folder not found: {self.templates_folder}")
            return False
        elif self.templates_folder:
            print(f"✓ Templates folder found: {self.templates_folder}")
            # Check for template files
            required_templates = ['coverpage.html', 'page1.html', 'page2.html', 'page3.html']
            missing_templates = []
            for template in required_templates:
                if not (self.templates_folder / template).exists():
                    missing_templates.append(template)
            
            if missing_templates:
                print(f"⚠ Warning: Some template files are missing: {', '.join(missing_templates)}")
                print("  Workflow will continue but may fail during HTML generation.")
            else:
                print(f"✓ All required template files found")
        else:
            print(f"✓ Templates folder will be auto-selected based on OfferLanguage in JSON data")
        
        print("✅ Validation completed\n")
        return True
    
    def initialize_components(self):
        """Initialize HTML generator, PDF converter, and Supabase uploader components."""
        print("🔧 Initializing workflow components...")
        
        self.html_generator = HTMLGenerator(
            data_file_path=str(self.data_file_path),
            templates_folder=str(self.templates_folder) if self.templates_folder else None,
            output_folder=str(self.html_output_folder)
        )
        
        self.pdf_converter = PDFConverter(
            data_file_path=str(self.data_file_path),
            html_input_folder=str(self.html_output_folder),
            pdf_output_folder=str(self.pdf_output_folder)
        )
        
        # Initialize Supabase uploader if enabled and available
        if self.upload_to_supabase and SUPABASE_AVAILABLE:
            try:
                self.supabase_uploader = SupabaseUploader()
                print("✓ Supabase uploader initialized")
            except ValueError as e:
                print(f"⚠ Supabase uploader not configured: {e}")
                self.upload_to_supabase = False
        elif self.upload_to_supabase and not SUPABASE_AVAILABLE:
            print("⚠ Supabase upload requested but module not available")
            self.upload_to_supabase = False
        
        # Initialize Error Logger if available
        if ERROR_LOGGER_AVAILABLE:
            try:
                self.error_logger = ErrorLogger()
                if self.error_logger.enabled:
                    print("✓ Error logger initialized")
            except Exception as e:
                print(f"⚠ Error logger initialization failed: {e}")
                self.error_logger = None
        
        print("✓ Components initialized\n")
    
    def generate_html(self, template_list: List[str] = None) -> bool:
        """
        Generate HTML files from templates including endingpage.
        
        Args:
            template_list (List[str]): List of template names to render.
                                      If None, uses default list including endingpage.html
        
        Returns:
            bool: True if HTML generation succeeds, False otherwise.
        """
        try:
            print("📝 STEP 1: Generating HTML files from templates")
            print("-" * 60)
            
            # If no template list provided, use default including endingpage.html
            if template_list is None:
                template_list = ['coverpage.html', 'page1.html', 'page2.html', 'page3.html', 'endingpage.html']
            
            self.generated_html_files = self.html_generator.run(template_list)
            
            if not self.generated_html_files:
                error_msg = "No HTML files were generated"
                print(f"❌ {error_msg}")
                
                # Log error to Supabase
                if self.error_logger:
                    self.error_logger.log_error(
                        error_name="HTMLGenerationError",
                        error_message=error_msg,
                        last_node_executed="generate_html",
                        severity="error",
                        category="workflow"
                    )
                return False
            
            print(f"✅ Generated {len(self.generated_html_files)} HTML file(s)\n")
            return True
            
        except Exception as e:
            print(f"❌ Error during HTML generation: {e}")
            
            # Log error to Supabase
            if self.error_logger:
                self.error_logger.log_workflow_error(
                    step_name="generate_html",
                    error=e,
                    additional_context={
                        "template_list": template_list,
                        "data_file": str(self.data_file_path)
                    }
                )
            return False
    
    async def convert_to_pdf(self) -> bool:
        """
        Convert generated HTML files to PDF.
        All HTML files including endingpage.html are now generated from templates.
        
        Returns:
            bool: True if PDF conversion succeeds, False otherwise.
        """
        try:
            print("📄 STEP 2: Converting HTML files to PDF")
            print("-" * 60)
            
            # All HTML files including endingpage.html are now in generated_html_files
            self.generated_pdf_path = await self.pdf_converter.run(
                html_files=self.generated_html_files,
                cleanup=self.cleanup_html
            )
            
            if not self.generated_pdf_path:
                error_msg = "PDF conversion failed - no output file generated"
                print(f"❌ {error_msg}")
                
                # Log error to Supabase
                if self.error_logger:
                    self.error_logger.log_error(
                        error_name="PDFConversionError",
                        error_message=error_msg,
                        last_node_executed="convert_to_pdf",
                        severity="error",
                        category="workflow",
                        full_error_data={
                            "html_files_count": len(self.generated_html_files),
                            "html_files": [str(f) for f in self.generated_html_files]
                        }
                    )
                return False
            
            print(f"✅ PDF generated successfully\n")
            return True
            
        except Exception as e:
            print(f"❌ Error during PDF conversion: {e}")
            
            # Log error to Supabase
            if self.error_logger:
                self.error_logger.log_workflow_error(
                    step_name="convert_to_pdf",
                    error=e,
                    additional_context={
                        "html_files_count": len(self.generated_html_files),
                        "html_files": [str(f) for f in self.generated_html_files]
                    }
                )
            return False
    
    async def upload_to_supabase_storage(self) -> bool:
        """
        Upload the generated PDF to Supabase Storage.
        Optionally delete local PDF after successful upload.
        
        Returns:
            bool: True if upload succeeds or is skipped, False if upload fails.
        """
        if not self.upload_to_supabase:
            print("⏭  Skipping Supabase upload (disabled or not configured)")
            return True
        
        try:
            print("\n📤 STEP 3: Uploading PDF to Supabase Storage")
            print("-" * 60)
            
            if not self.supabase_uploader:
                print("⚠ Supabase uploader not initialized, skipping upload")
                return True
            
            # Get PDF filename
            pdf_path = Path(self.generated_pdf_path)
            pdf_filename = pdf_path.name
            
            # Upload to Supabase
            result = self.supabase_uploader.upload_from_finalPdf_folder(pdf_filename)
            
            if result["success"]:
                print(f"✅ PDF uploaded to Supabase successfully!")
                print(f"   Public URL: {result['url']}")
                self.supabase_url = result['url']
                
                # Delete local PDF if configured
                if self.delete_local_after_upload:
                    try:
                        pdf_path.unlink()
                        print(f"✓ Local PDF deleted: {pdf_filename}")
                    except Exception as e:
                        print(f"⚠ Warning: Could not delete local PDF: {e}")
                
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ Supabase upload failed: {error_msg}")
                
                # Log error to Supabase
                if self.error_logger:
                    self.error_logger.log_error(
                        error_name="SupabaseUploadError",
                        error_message=error_msg,
                        last_node_executed="upload_to_supabase_storage",
                        severity="error",
                        category="storage",
                        full_error_data={
                            "pdf_filename": pdf_filename,
                            "pdf_path": str(pdf_path),
                            "upload_result": result
                        }
                    )
                return False
                
        except Exception as e:
            print(f"❌ Error during Supabase upload: {e}")
            
            # Log error to Supabase
            if self.error_logger:
                self.error_logger.log_workflow_error(
                    step_name="upload_to_supabase_storage",
                    error=e,
                    additional_context={
                        "pdf_path": str(self.generated_pdf_path) if self.generated_pdf_path else None
                    }
                )
            return False
    
    async def run(self, template_list: List[str] = None) -> Optional[str]:
        """
        Execute the complete workflow: Data -> HTML -> PDF.
        
        Args:
            template_list (List[str]): Optional list of template names to use.
        
        Returns:
            str: Path to generated PDF file, or None if workflow failed.
        """
        print("\n" + "=" * 60)
        print("🚀 PDF GENERATION WORKFLOW STARTED")
        print("=" * 60)
        print(f"📁 Working directory: {self.base_dir}")
        print(f"📥 Input data: {self.data_file_path.name}")
        print(f"📤 Output PDF folder: {self.pdf_output_folder}")
        print("=" * 60 + "\n")
        
        # Validate inputs
        if not self.validate_input():
            print("❌ Workflow aborted due to validation errors")
            return None
        
        # Initialize components
        self.initialize_components()
        
        # Step 1: Generate HTML
        if not self.generate_html(template_list):
            print("❌ Workflow aborted: HTML generation failed")
            return None
        
        # Step 2: Convert to PDF
        if not await self.convert_to_pdf():
            print("❌ Workflow aborted: PDF conversion failed")
            return None
        
        # Step 3: Upload to Supabase (optional)
        if not await self.upload_to_supabase_storage():
            print("⚠ Warning: Supabase upload failed, but PDF was generated locally")
            # Don't abort workflow if upload fails
        
        # Success summary
        print("\n" + "=" * 60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        if self.supabase_url:
            print(f"☁️  Supabase URL: {self.supabase_url}")
            if not self.delete_local_after_upload:
                print(f"📄 Local PDF: {self.generated_pdf_path}")
        else:
            print(f"📄 Generated PDF: {self.generated_pdf_path}")
        print(f"🎉 Your PDF offer is ready!")
        print("=" * 60 + "\n")
        
        # Return Supabase URL if available, otherwise local path
        return self.supabase_url if self.supabase_url else self.generated_pdf_path
    
    async def run_with_custom_data(self, data_file_path: str, 
                                   template_list: List[str] = None) -> Optional[str]:
        """
        Run workflow with a custom data file.
        
        Args:
            data_file_path (str): Path to the custom JSON data file.
            template_list (List[str]): Optional list of template names to use.
        
        Returns:
            str: Path to generated PDF file, or None if workflow failed.
        """
        print(f"🔧 DEBUG: run_with_custom_data called with: {data_file_path}")
        self.data_file_path = Path(data_file_path)
        print(f"🔧 DEBUG: data_file_path set to: {self.data_file_path}")
        print(f"🔧 DEBUG: data file exists: {self.data_file_path.exists()}")
        
        # Reinitialize components with the new data file path
        print("🔧 DEBUG: Reinitializing components...")
        self.initialize_components()
        print("🔧 DEBUG: Components reinitialized")
        
        print("🔧 DEBUG: Starting workflow...")
        result = await self.run(template_list)
        print(f"🔧 DEBUG: Workflow completed. Result: {result}")
        return result


def main():
    """Main function for standalone execution."""
    async def run_workflow():
        # Check if custom data file path is provided as command line argument
        if len(sys.argv) > 1:
            data_file = sys.argv[1]
            print(f"Using custom data file: {data_file}")
            orchestrator = WorkflowOrchestrator()
            await orchestrator.run_with_custom_data(data_file)
        else:
            # Use default data.json
            orchestrator = WorkflowOrchestrator()
            await orchestrator.run()
    
    asyncio.run(run_workflow())


if __name__ == "__main__":
    main()

"""
PDF Generation Workflow Orchestrator

This module orchestrates the complete PDF generation workflow:
1. Loads data from JSON file
2. Generates HTML files from templates using HTMLGenerator
3. Converts HTML files to PDF using PDFConverter
"""

import asyncio
from pathlib import Path
from typing import Optional, List
import sys

from htmlGenerator import HTMLGenerator
from htmlToPdf import PDFConverter


class WorkflowOrchestrator:
    """
    Main workflow orchestrator for PDF generation.
    
    This class coordinates the entire process of generating PDFs from JSON data,
    managing the flow from data input through HTML generation to final PDF output.
    """
    
    def __init__(self, data_file_path: str = None, templates_folder: str = None,
                 html_output_folder: str = None, pdf_output_folder: str = None,
                 cleanup_html: bool = True):
        """
        Initialize the WorkflowOrchestrator.
        
        Args:
            data_file_path (str): Path to the JSON data file. Defaults to 'data.json'.
            templates_folder (str): Path to templates folder. Defaults to 'templates'.
            html_output_folder (str): Path to HTML output folder. Defaults to 'htmlGenerated'.
            pdf_output_folder (str): Path to PDF output folder. Defaults to 'finalPdf'.
            cleanup_html (bool): Whether to delete HTML files after PDF generation. Defaults to True.
        """
        self.base_dir = Path(__file__).parent
        self.data_file_path = Path(data_file_path) if data_file_path else self.base_dir / 'data.json'
        self.templates_folder = Path(templates_folder) if templates_folder else self.base_dir / 'templates'
        self.html_output_folder = Path(html_output_folder) if html_output_folder else self.base_dir / 'htmlGenerated'
        self.pdf_output_folder = Path(pdf_output_folder) if pdf_output_folder else self.base_dir / 'finalPdf'
        self.cleanup_html = cleanup_html
        
        # Initialize components
        self.html_generator = None
        self.pdf_converter = None
        self.generated_html_files: List[Path] = []
        self.generated_pdf_path: Optional[str] = None
    
    def validate_input(self) -> bool:
        """
        Validate that required input files and folders exist.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        print("\n🔍 Validating input files and folders...")
        
        if not self.data_file_path.exists():
            print(f"❌ Error: Data file not found: {self.data_file_path}")
            return False
        print(f"✓ Data file found: {self.data_file_path}")
        
        if not self.templates_folder.exists():
            print(f"❌ Error: Templates folder not found: {self.templates_folder}")
            return False
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
        
        print("✅ Validation completed\n")
        return True
    
    def initialize_components(self):
        """Initialize HTML generator and PDF converter components."""
        print("🔧 Initializing workflow components...")
        
        self.html_generator = HTMLGenerator(
            data_file_path=str(self.data_file_path),
            templates_folder=str(self.templates_folder),
            output_folder=str(self.html_output_folder)
        )
        
        self.pdf_converter = PDFConverter(
            data_file_path=str(self.data_file_path),
            html_input_folder=str(self.html_output_folder),
            pdf_output_folder=str(self.pdf_output_folder)
        )
        
        print("✓ Components initialized\n")
    
    def generate_html(self, template_list: List[str] = None) -> bool:
        """
        Generate HTML files from templates.
        
        Args:
            template_list (List[str]): List of template names to render.
        
        Returns:
            bool: True if HTML generation succeeds, False otherwise.
        """
        try:
            print("📝 STEP 1: Generating HTML files from templates")
            print("-" * 60)
            
            self.generated_html_files = self.html_generator.run(template_list)
            
            if not self.generated_html_files:
                print("❌ No HTML files were generated")
                return False
            
            print(f"✅ Generated {len(self.generated_html_files)} HTML file(s)\n")
            return True
            
        except Exception as e:
            print(f"❌ Error during HTML generation: {e}")
            return False
    
    async def convert_to_pdf(self) -> bool:
        """
        Convert generated HTML files to PDF.
        
        Returns:
            bool: True if PDF conversion succeeds, False otherwise.
        """
        try:
            print("📄 STEP 2: Converting HTML files to PDF")
            print("-" * 60)
            
            # Add permanent endingpage.html to the list of files to convert
            html_files_for_pdf = self.generated_html_files.copy()
            ending_page = self.html_output_folder / "endingpage.html"
            
            # Check if endingpage.html exists and add it to the list
            if ending_page.exists():
                html_files_for_pdf.append(ending_page)
                print(f"✓ Including permanent file: endingpage.html")
            else:
                print(f"⚠ Warning: endingpage.html not found at {ending_page}")
            
            self.generated_pdf_path = await self.pdf_converter.run(
                html_files=html_files_for_pdf,
                cleanup=self.cleanup_html
            )
            
            if not self.generated_pdf_path:
                print("❌ PDF conversion failed")
                return False
            
            print(f"✅ PDF generated successfully\n")
            return True
            
        except Exception as e:
            print(f"❌ Error during PDF conversion: {e}")
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
        
        # Success summary
        print("\n" + "=" * 60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📄 Generated PDF: {self.generated_pdf_path}")
        print(f"🎉 Your PDF offer is ready!")
        print("=" * 60 + "\n")
        
        return self.generated_pdf_path
    
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

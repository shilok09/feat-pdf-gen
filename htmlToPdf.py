#!/usr/bin/env python3
"""
Super Simple HTML to PDF Converter using Playwright
Most reliable method - works like printing from a browser
"""

import asyncio
import sys
from pathlib import Path
import tempfile
import json
from typing import List, Union, Optional

class PDFConverter:
    """
    PDF Converter class for converting HTML files to PDF using Playwright.
    
    This class handles the conversion of HTML files to a single PDF document
    using a browser engine for high-quality rendering.
    """
    
    def __init__(self, data_file_path: str = None, html_input_folder: str = None,
                 pdf_output_folder: str = None):
        """
        Initialize the PDFConverter.
        
        Args:
            data_file_path (str): Path to the JSON data file for getting client info.
            html_input_folder (str): Path to folder containing HTML files. 
                                     Defaults to 'htmlGenerated' in current directory.
            pdf_output_folder (str): Path to output folder for PDF. 
                                    Defaults to 'finalPdf' in current directory.
        """
        self.base_dir = Path(__file__).parent
        self.data_file_path = Path(data_file_path) if data_file_path else self.base_dir / 'data.json'
        self.html_input_folder = Path(html_input_folder) if html_input_folder else self.base_dir / 'htmlGenerated'
        self.pdf_output_folder = Path(pdf_output_folder) if pdf_output_folder else self.base_dir / 'finalPdf'
        
        self.data = {}
        self.pdf_filename = "offer.pdf"
    
    def load_data(self):
        """Load data from JSON file to get client information."""
        if not self.data_file_path.exists():
            print(f"⚠ Warning: data.json not found: {self.data_file_path}")
            return
        
        with open(self.data_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Get client company name for PDF filename
        client_company = self.data.get('client', {}).get('company', 'offer')
        # Sanitize filename (remove invalid characters)
        self.pdf_filename = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_' 
            for c in client_company
        ) + ".pdf"
        
        print(f"✓ PDF will be named: {self.pdf_filename}")
    
    def create_output_directory(self):
        """Create PDF output directory if it doesn't exist."""
        self.pdf_output_folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ PDF output directory ready: {self.pdf_output_folder}")
    
    async def convert_html_to_pdf(self, html_files: List[Union[str, Path]], 
                                  output_pdf_path: Optional[Path] = None) -> Optional[str]:
        """
        Convert HTML files to PDF using Playwright (browser-based conversion).
        
        Args:
            html_files (List): List of paths to HTML files to convert.
            output_pdf_path (Path, optional): Output PDF path.
        
        Returns:
            str: Path to the generated PDF file, or None if conversion failed.
        """
        try:
            from playwright.async_api import async_playwright

            # Convert to Path objects
            html_paths = [Path(f).resolve() for f in html_files]

            for html_path in html_paths:
                if not html_path.exists():
                    raise FileNotFoundError(f"HTML file not found: {html_path}")

            # Output PDF path
            if output_pdf_path is None:
                output_pdf_path = self.pdf_output_folder / self.pdf_filename
            else:
                output_pdf_path = Path(output_pdf_path).resolve()

            print(f"Converting {', '.join([f.name for f in html_paths])} to one PDF using browser engine...")

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                # Set base_url to the directory containing your HTML and images
                base_dir = str(html_paths[0].parent.resolve())
                context = await browser.new_context(base_url=f"file://{base_dir}/")
                page = await context.new_page()

                # Combine all HTML files into one temp file with page breaks
                combined_html = ""
                for idx, html_path in enumerate(html_paths):
                    html_content = html_path.read_text(encoding="utf-8")
                    if idx > 0:
                        # Add page break between files
                        combined_html += '<div style="page-break-before: always;"></div>'
                    combined_html += html_content

                with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp:
                    tmp.write(combined_html)
                    tmp_path = Path(tmp.name)

                await page.goto(f"file://{tmp_path}")
                await page.wait_for_load_state('networkidle')
                # Extra explicit wait for network idle
                await asyncio.sleep(1)  # Give browser a moment to finish rendering
                await page.pdf(
                    path=str(output_pdf_path),
                    format='A4',
                    margin={
                        'top': '20mm',
                        'right': '20mm',
                        'bottom': '20mm',
                        'left': '20mm'
                    },
                    print_background=True,
                    prefer_css_page_size=True
                )
                await browser.close()
                
                # Clean up temp file
                tmp_path.unlink(missing_ok=True)

            print(f"✅ PDF generated successfully: {output_pdf_path}")
            
            # Display file size
            if output_pdf_path.exists():
                file_size = output_pdf_path.stat().st_size
                file_size_kb = file_size / 1024
                print(f"📦 File size: {file_size_kb:.1f} KB")
            
            return str(output_pdf_path)

        except ImportError:
            print("❌ playwright is not installed. Installing...")
            await self.install_playwright()
            return await self.convert_html_to_pdf(html_files, output_pdf_path)

        except Exception as e:
            print(f"❌ Error converting HTML to PDF: {e}")
            return None
    
    async def install_playwright(self):
        """Install playwright package and browser."""
        import subprocess
        
        try:
            print("Installing playwright...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            print("Installing chromium browser...")
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("✅ playwright installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install playwright: {e}")
            raise
    
    def cleanup_html_files(self, files_to_delete: List[str] = None):
        """
        Delete specified HTML files from the input folder.
        Note: endingpage.html is permanent and will not be deleted.
        
        Args:
            files_to_delete (List[str]): List of filenames to delete.
        """
        if files_to_delete is None:
            # Only delete generated files, not permanent endingpage.html
            files_to_delete = ["coverpage.html", "page1.html", "page2.html", "page3.html"]
        
        print(f"\n🗑️ Cleaning up generated HTML files...")
        print(f"💡 Note: endingpage.html is permanent and will be preserved")
        for filename in files_to_delete:
            file_path = self.html_input_folder / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"✓ Deleted {filename}")
                except Exception as e:
                    print(f"✗ Failed to delete {filename}: {e}")
            else:
                print(f"⚠ {filename} not found, skipping...")
        print(f"✅ Cleanup completed!")
    
    async def run(self, html_files: List[Union[str, Path]] = None, 
                  cleanup: bool = True) -> Optional[str]:
        """
        Execute the complete PDF conversion workflow.
        
        Args:
            html_files (List): List of HTML file paths to convert. 
                              If None, uses default files from htmlGenerated folder.
            cleanup (bool): Whether to delete HTML files after conversion.
        
        Returns:
            str: Path to generated PDF file, or None if conversion failed.
        """
        print("=" * 60)
        print("PDF CONVERSION WORKFLOW STARTED")
        print("=" * 60)
        
        self.load_data()
        self.create_output_directory()
        
        # Default HTML files if none provided
        if html_files is None:
            html_files = [
                self.html_input_folder / "coverpage.html",
                self.html_input_folder / "page1.html",
                self.html_input_folder / "page2.html",
                self.html_input_folder / "page3.html",
                self.html_input_folder / "endingpage.html"
            ]
        
        # Check for missing files
        missing = [str(f) for f in html_files if not Path(f).exists()]
        if missing:
            print(f"❌ HTML file(s) not found: {', '.join(missing)}")
            return None
        
        # Convert to PDF
        pdf_path = await self.convert_html_to_pdf(html_files)
        
        if pdf_path and cleanup:
            self.cleanup_html_files()
        
        print("=" * 60)
        print("PDF CONVERSION COMPLETED")
        print("=" * 60)
        
        if pdf_path:
            print(f"\n🎉 Success! Your offer has been converted to PDF:")
            print(f"📄 PDF file: {pdf_path}")
            print(f"📏 Format: A4 size with 20mm margins")
            print(f"🎨 Background colors and styling preserved")
        
        return pdf_path


# Legacy function for backward compatibility
async def convert_with_playwright(html_file_path, output_pdf_path=None):
    """
    Legacy function - Convert HTML to PDF using Playwright.
    Maintained for backward compatibility.
    """
    converter = PDFConverter()
    
    if isinstance(html_file_path, (list, tuple)):
        html_files = html_file_path
    else:
        html_files = [html_file_path]
    
    return await converter.convert_html_to_pdf(html_files, output_pdf_path)

async def install_playwright():
    """
    Legacy function - Install playwright package and browser.
    Maintained for backward compatibility.
    """
    converter = PDFConverter()
    await converter.install_playwright()


def main():
    """Main function for standalone execution."""
    async def run():
        converter = PDFConverter()
        await converter.run()

    asyncio.run(run())


if __name__ == "__main__":
    main()
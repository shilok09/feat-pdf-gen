#!/usr/bin/env python3
"""
Super Simple HTML to PDF Converter using Playwright
Most reliable method - works like printing from a browser
"""

import asyncio
import sys
from pathlib import Path
import tempfile

async def convert_with_playwright(html_file_path, output_pdf_path=None):
    """
    Convert HTML to PDF using Playwright (browser-based conversion)
    
    Args:
        html_file_path (str): Path to the HTML file
        output_pdf_path (str, optional): Output PDF path
    
    Returns:
        str: Path to the generated PDF file
    """
    try:
        from playwright.async_api import async_playwright

        # Accept a list of HTML file paths
        if isinstance(html_file_path, (list, tuple)):
            html_files = [Path(f).resolve() for f in html_file_path]
        else:
            html_files = [Path(html_file_path).resolve()]

        for html_path in html_files:
            if not html_path.exists():
                raise FileNotFoundError(f"HTML file not found: {html_path}")

        # Output PDF path
        if output_pdf_path is None:
            output_pdf_path = html_files[0].parent / "offer_playwright.pdf"
        else:
            output_pdf_path = Path(output_pdf_path).resolve()

        print(f"Converting {', '.join([f.name for f in html_files])} to one PDF using browser engine...")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Set base_url to the directory containing your HTML and images
            base_dir = str(html_files[0].parent.resolve())
            context = await browser.new_context(base_url=f"file://{base_dir}/")
            page = await context.new_page()

            # Combine all HTML files into one temp file with page breaks
            combined_html = ""
            for idx, html_path in enumerate(html_files):
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
            # Extra explicit wait for network idle (redundant but sometimes helps)
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

        print(f"✅ PDF generated successfully: {output_pdf_path}")
        return str(output_pdf_path)

    except ImportError:
        print("❌ playwright is not installed. Installing...")
        await install_playwright()
        return await convert_with_playwright(html_file_path, output_pdf_path)

    except Exception as e:
        print(f"❌ Error converting HTML to PDF: {e}")
        return None

async def install_playwright():
    """Install playwright package and browser"""
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

def main():
    """Main function"""
    async def run():
        import json
        
        current_dir = Path(__file__).parent
        
        # Load data.json to get client company name
        data_file = current_dir / "data.json"
        if not data_file.exists():
            print(f"❌ data.json not found: {data_file}")
            return
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get client company name for PDF filename
        client_company = data.get('client', {}).get('company', 'offer')
        # Sanitize filename (remove invalid characters)
        pdf_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in client_company) + ".pdf"
        
        # HTML files from pdfGenerated folder
        pdf_generated_dir = current_dir / "htmlGenerated"
        html_files = [
            pdf_generated_dir / "coverpage.html",
            pdf_generated_dir / "page1.html",
            pdf_generated_dir / "page2.html",
            pdf_generated_dir / "page3.html",
            pdf_generated_dir / "endingpage.html"
        ]
        
        # Create finalPdf folder if it doesn't exist
        final_pdf_dir = current_dir / "finalPdf"
        final_pdf_dir.mkdir(exist_ok=True)
        
        pdf_file = final_pdf_dir / pdf_filename

        missing = [str(f) for f in html_files if not f.exists()]
        if missing:
            print(f"❌ HTML file(s) not found: {', '.join(missing)}")
            return

        result = await convert_with_playwright([str(f) for f in html_files], str(pdf_file))

        if result:
            print(f"\n🎉 Success! Your offer has been converted to PDF:")
            print(f"📄 PDF file: {result}")
            print(f"📏 Format: A4 size with 20mm margins")
            print(f"🎨 Background colors and styling preserved")

            # Check file size
            pdf_path = Path(result)
            if pdf_path.exists():
                file_size = pdf_path.stat().st_size
                file_size_kb = file_size / 1024
                print(f"📦 File size: {file_size_kb:.1f} KB")
            
            # Delete specified HTML files from pdfGenerated folder
            files_to_delete = ["page1.html", "page2.html", "coverpage.html","page3.html"]
            print(f"\n🗑️ Cleaning up generated HTML files...")
            for filename in files_to_delete:
                file_path = pdf_generated_dir / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"✓ Deleted {filename}")
                    except Exception as e:
                        print(f"✗ Failed to delete {filename}: {e}")
                else:
                    print(f"⚠ {filename} not found, skipping...")
            print(f"✅ Cleanup completed!")

    asyncio.run(run())

if __name__ == "__main__":
    main()
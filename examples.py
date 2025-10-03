"""
Example Usage Script

This script demonstrates various ways to use the PDF generation workflow.
"""

import asyncio
from workflow import WorkflowOrchestrator
from htmlGenerator import HTMLGenerator
from htmlToPdf import PDFConverter


async def example_1_basic_workflow():
    """Example 1: Basic workflow using default settings."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Workflow")
    print("=" * 60)
    
    orchestrator = WorkflowOrchestrator()
    pdf_path = await orchestrator.run()
    
    if pdf_path:
        print(f"\n✅ Success! PDF generated at: {pdf_path}")
    else:
        print("\n❌ Failed to generate PDF")


async def example_2_custom_paths():
    """Example 2: Workflow with custom paths."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Paths")
    print("=" * 60)
    
    orchestrator = WorkflowOrchestrator(
        data_file_path="data.json",
        templates_folder="templates",
        html_output_folder="htmlGenerated",
        pdf_output_folder="finalPdf",
        cleanup_html=True  # Clean up HTML files after conversion
    )
    
    pdf_path = await orchestrator.run()
    
    if pdf_path:
        print(f"\n✅ Success! PDF generated at: {pdf_path}")


async def example_3_custom_templates():
    """Example 3: Using custom template list."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Template List")
    print("=" * 60)
    
    orchestrator = WorkflowOrchestrator()
    
    # Use only specific templates
    custom_templates = ['coverpage.html', 'page1.html', 'page2.html']
    
    pdf_path = await orchestrator.run(template_list=custom_templates)
    
    if pdf_path:
        print(f"\n✅ Success! PDF generated at: {pdf_path}")


def example_4_html_only():
    """Example 4: Generate HTML only (no PDF conversion)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: HTML Generation Only")
    print("=" * 60)
    
    generator = HTMLGenerator(
        data_file_path="data.json",
        templates_folder="templates",
        output_folder="htmlGenerated"
    )
    
    html_files = generator.run()
    
    print(f"\n✅ Generated {len(html_files)} HTML files:")
    for html_file in html_files:
        print(f"   - {html_file.name}")


async def example_5_pdf_only():
    """Example 5: Convert existing HTML to PDF (no HTML generation)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: PDF Conversion Only")
    print("=" * 60)
    
    converter = PDFConverter(
        data_file_path="data.json",
        html_input_folder="htmlGenerated",
        pdf_output_folder="finalPdf"
    )
    
    pdf_path = await converter.run(cleanup=False)
    
    if pdf_path:
        print(f"\n✅ Success! PDF generated at: {pdf_path}")


async def example_6_no_cleanup():
    """Example 6: Keep HTML files after PDF generation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Workflow Without Cleanup")
    print("=" * 60)
    
    orchestrator = WorkflowOrchestrator(cleanup_html=False)
    pdf_path = await orchestrator.run()
    
    if pdf_path:
        print(f"\n✅ Success! PDF generated at: {pdf_path}")
        print("💡 HTML files have been preserved in htmlGenerated folder")


async def example_7_multiple_data_files():
    """Example 7: Process multiple data files."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Multiple Data Files")
    print("=" * 60)
    
    data_files = ["data.json"]  # Add more files as needed
    
    orchestrator = WorkflowOrchestrator()
    
    for data_file in data_files:
        print(f"\n📄 Processing: {data_file}")
        pdf_path = await orchestrator.run_with_custom_data(data_file)
        
        if pdf_path:
            print(f"✅ Generated: {pdf_path}")
        else:
            print(f"❌ Failed: {data_file}")


async def run_all_examples():
    """Run all examples sequentially."""
    print("\n" + "=" * 70)
    print("  PDF GENERATION WORKFLOW - EXAMPLE USAGE")
    print("=" * 70)
    
    # Uncomment the examples you want to run:
    
    # await example_1_basic_workflow()
    # await example_2_custom_paths()
    # await example_3_custom_templates()
    # example_4_html_only()
    # await example_5_pdf_only()
    # await example_6_no_cleanup()
    # await example_7_multiple_data_files()
    
    # Run the basic example by default
    await example_1_basic_workflow()
    
    print("\n" + "=" * 70)
    print("  EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_examples())

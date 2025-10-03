"""
Main Entry Point for PDF Generation Workflow

This is the main entry point for the OOP-based PDF generation system.
Simply run this file with a data.json file to generate a complete PDF offer.

Usage:
    python main.py                    # Uses data.json in current directory
    python main.py path/to/data.json  # Uses custom data file
"""

import asyncio
import sys
from pathlib import Path

from workflow import WorkflowOrchestrator


def print_banner():
    """Print application banner."""
    print("\n" + "=" * 70)
    print("  ____  ____  _____    ____                           _             ")
    print(" |  _ \\|  _ \\|  ___|  / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __ ")
    print(" | |_) | | | | |_    | |  _ / _ \\ '_ \\ / _ \\ '__/ _` | __/ _ \\| '__|")
    print(" |  __/| |_| |  _|   | |_| |  __/ | | |  __/ | | (_| | || (_) | |   ")
    print(" |_|   |____/|_|      \\____|\\___|_| |_|\\___|_|  \\__,_|\\__\\___/|_|   ")
    print("                                                                      ")
    print("              CoffeeCups PDF Generation Workflow                     ")
    print("=" * 70 + "\n")


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python main.py                    # Uses data.json in current directory")
    print("  python main.py path/to/data.json  # Uses custom data file")
    print()


async def main():
    """
    Main function to run the PDF generation workflow.
    
    This function:
    1. Parses command line arguments
    2. Initializes the workflow orchestrator
    3. Executes the complete workflow
    4. Reports results
    """
    print_banner()
    
    # Parse command line arguments
    data_file_path = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print_usage()
            return
        data_file_path = sys.argv[1]
        print(f"📥 Using custom data file: {data_file_path}\n")
    else:
        print(f"📥 Using default data file: data.json\n")
    
    try:
        # Initialize workflow orchestrator
        orchestrator = WorkflowOrchestrator(
            data_file_path=data_file_path,
            cleanup_html=True  # Clean up HTML files after PDF generation
        )
        
        # Run the complete workflow
        pdf_path = await orchestrator.run()
        
        if pdf_path:
            print("\n✅ SUCCESS!")
            print(f"Your PDF has been generated: {pdf_path}")
            return 0
        else:
            print("\n❌ FAILED!")
            print("PDF generation workflow failed. Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

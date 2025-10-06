from jinja2 import Environment, FileSystemLoader
import json
import os
from pathlib import Path
from typing import Dict, List, Any


class HTMLGenerator:
    """
    HTML Generator class for rendering Jinja2 templates with JSON data.
    
    This class handles the generation of HTML files from templates using data
    provided in JSON format.
    """
    
    def __init__(self, data_file_path: str = None, templates_folder: str = None, 
                 output_folder: str = None):
        """
        Initialize the HTMLGenerator.
        
        Args:
            data_file_path (str): Path to the JSON data file. Defaults to 'data.json' in current directory.
            templates_folder (str): Path to templates folder. Defaults to 'templates' in current directory.
                                   If None, will be auto-selected based on OfferLanguage in JSON data.
            output_folder (str): Path to output folder. Defaults to 'htmlGenerated' in current directory.
        """
        self.base_dir = Path(__file__).parent
        self.data_file_path = Path(data_file_path) if data_file_path else self.base_dir / 'data.json'
        self.templates_folder_override = Path(templates_folder) if templates_folder else None
        self.templates_folder = None  # Will be set after loading data
        self.output_folder = Path(output_folder) if output_folder else self.base_dir / 'htmlGenerated'
        
        self.data: Dict[str, Any] = {}
        self.env = None
        
    def load_data(self) -> Dict[str, Any]:
        """
        Load data from JSON file and determine the template folder based on OfferLanguage.
        
        Returns:
            Dict containing the loaded data.
            
        Raises:
            FileNotFoundError: If the data file doesn't exist.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        if not self.data_file_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file_path}")
        
        with open(self.data_file_path, encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"✓ Loaded data from: {self.data_file_path}")
        
        # Determine template folder based on OfferLanguage
        if self.templates_folder_override:
            self.templates_folder = self.templates_folder_override
            print(f"✓ Using manually specified templates folder: {self.templates_folder}")
        else:
            offer_language = self.data.get('OfferLanguage', 'English').strip()
            
            if offer_language.lower() == 'polish':
                self.templates_folder = self.base_dir / 'templates-Polish'
                print(f"✓ Language detected: Polish - Using templates-Polish folder")
            elif offer_language.lower() == 'english':
                self.templates_folder = self.base_dir / 'templates-English'
                print(f"✓ Language detected: English - Using templates-English folder")
            else:
                # Default to English if language not recognized
                self.templates_folder = self.base_dir / 'templates-English'
                print(f"⚠ Language '{offer_language}' not recognized. Defaulting to templates-English folder")
        
        return self.data
    
    def setup_jinja_environment(self):
        """
        Set up Jinja2 environment with the templates folder.
        
        Raises:
            FileNotFoundError: If templates folder doesn't exist.
        """
        if not self.templates_folder.exists():
            raise FileNotFoundError(f"Templates folder not found: {self.templates_folder}")
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_folder)),
            autoescape=True
        )
        print(f"✓ Jinja2 environment configured with templates from: {self.templates_folder}")
    
    def create_output_directory(self):
        """Create output directory if it doesn't exist."""
        self.output_folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready: {self.output_folder}")
    
    def render_template(self, template_name: str) -> str:
        """
        Render a single template with the loaded data.
        
        Args:
            template_name (str): Name of the template file to render.
            
        Returns:
            str: Rendered HTML content.
            
        Raises:
            Exception: If template rendering fails.
        """
        if self.env is None:
            raise RuntimeError("Jinja2 environment not initialized. Call setup_jinja_environment() first.")
        
        if not self.data:
            raise RuntimeError("No data loaded. Call load_data() first.")
        
        template = self.env.get_template(template_name)
        output_html = template.render(**self.data)
        return output_html
    
    def save_html(self, filename: str, content: str):
        """
        Save HTML content to a file.
        
        Args:
            filename (str): Name of the output file.
            content (str): HTML content to save.
        """
        output_path = self.output_folder / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Generated {filename}")
    
    def generate_html_files(self, template_list: List[str] = None) -> List[Path]:
        """
        Generate HTML files from templates.
        
        Args:
            template_list (List[str]): List of template names to render.
                                       Defaults to common templates including endingpage.
        
        Returns:
            List[Path]: List of paths to generated HTML files.
        """
        if template_list is None:
            template_list = ['coverpage.html', 'page1.html', 'page2.html', 'page3.html', 'endingpage.html']
        
        generated_files = []
        
        for template_name in template_list:
            try:
                output_html = self.render_template(template_name)
                self.save_html(template_name, output_html)
                generated_files.append(self.output_folder / template_name)
            except Exception as e:
                print(f"✗ Error generating {template_name}: {e}")
        
        print(f"\n✅ All files generated in: {self.output_folder}")
        return generated_files
    
    def run(self, template_list: List[str] = None) -> List[Path]:
        """
        Execute the complete HTML generation workflow.
        
        Args:
            template_list (List[str]): List of template names to render.
        
        Returns:
            List[Path]: List of paths to generated HTML files.
        """
        print("=" * 60)
        print("HTML GENERATION WORKFLOW STARTED")
        print("=" * 60)
        
        self.load_data()
        self.setup_jinja_environment()
        self.create_output_directory()
        generated_files = self.generate_html_files(template_list)
        
        print("=" * 60)
        print("HTML GENERATION COMPLETED")
        print("=" * 60)
        
        return generated_files


# For backward compatibility and direct script execution
def main():
    """Main function for standalone execution."""
    generator = HTMLGenerator()
    generator.run()


if __name__ == '__main__':
    main()

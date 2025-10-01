from jinja2 import Environment, FileSystemLoader
import json
import os

# Load data from JSON file (example path)
with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

# Set up Jinja2 environment - use templates folder
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_FOLDER = os.path.join(TEMPLATE_DIR, 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER), autoescape=True)

# Create output directory if it doesn't exist
output_dir = os.path.join(TEMPLATE_DIR, 'htmlGenerated')
os.makedirs(output_dir, exist_ok=True)

# List of templates to render
templates = ['coverpage.html', 'page1.html', 'page2.html','page3.html']

# Render each template
for template_name in templates:
    try:
        template = env.get_template(template_name)
        
        # Render template with data
        output_html = template.render(**data)
        
        # Save rendered HTML to pdfGenerated folder with same filename
        output_path = os.path.join(output_dir, template_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        
        print(f'✓ Generated {template_name}')
    except Exception as e:
        print(f'✗ Error generating {template_name}: {e}')

print(f'\nAll files generated in: {output_dir}')

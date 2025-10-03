# PDF Generation Workflow - OOP Implementation

An object-oriented PDF generation system that automatically converts JSON data into professional PDF documents through HTML templating.

## 🚀 Features

- **OOP Architecture**: Clean, maintainable object-oriented design
- **Automated Workflow**: Data → HTML → PDF in one command
- **Template-based**: Uses Jinja2 templates for flexible HTML generation
- **High-Quality Output**: Browser-based PDF rendering with Playwright
- **Automatic Cleanup**: Removes intermediate HTML files after PDF generation
- **Error Handling**: Comprehensive validation and error reporting

## 📁 Project Structure

```
pdfGen/
├── main.py                 # Main entry point
├── workflow.py             # Workflow orchestrator class
├── htmlGenerator.py        # HTML generation class
├── htmlToPdf.py           # PDF conversion class
├── data.json              # Input data file
├── templates/             # Jinja2 HTML templates
│   ├── coverpage.html
│   ├── page1.html
│   ├── page2.html
│   ├── page3.html
│   └── endingpage.html
├── htmlGenerated/         # Intermediate HTML files (auto-cleaned)
└── finalPdf/              # Output PDF files
```

## 🏗️ Architecture

### Class Diagram

```
WorkflowOrchestrator
    ├── HTMLGenerator
    │   └── Generates HTML from templates + data
    └── PDFConverter
        └── Converts HTML to PDF using Playwright
```

### Components

1. **HTMLGenerator** (`htmlGenerator.py`)
   - Loads JSON data
   - Renders Jinja2 templates
   - Generates HTML files

2. **PDFConverter** (`htmlToPdf.py`)
   - Converts HTML to PDF
   - Uses Playwright for browser-based rendering
   - Handles cleanup

3. **WorkflowOrchestrator** (`workflow.py`)
   - Coordinates the entire workflow
   - Validates inputs
   - Manages component lifecycle

4. **Main Entry Point** (`main.py`)
   - CLI interface
   - Handles arguments
   - Reports results

## 📦 Installation

### Prerequisites

- Python 3.7+
- pip

### Install Dependencies

```bash
pip install jinja2 playwright
python -m playwright install chromium
```

## 🎯 Usage

### Basic Usage

Simply run the main script with your `data.json` file:

```bash
# Uses data.json in current directory
python main.py

# Uses custom data file
python main.py path/to/your/data.json
```

### Advanced Usage

#### Using Workflow Orchestrator Directly

```python
import asyncio
from workflow import WorkflowOrchestrator

async def generate_pdf():
    orchestrator = WorkflowOrchestrator(
        data_file_path="data.json",
        cleanup_html=True
    )
    pdf_path = await orchestrator.run()
    print(f"PDF generated: {pdf_path}")

asyncio.run(generate_pdf())
```

#### Using Individual Components

```python
# Generate HTML only
from htmlGenerator import HTMLGenerator

generator = HTMLGenerator(data_file_path="data.json")
html_files = generator.run()
print(f"Generated {len(html_files)} HTML files")

# Convert HTML to PDF only
import asyncio
from htmlToPdf import PDFConverter

async def convert():
    converter = PDFConverter(data_file_path="data.json")
    pdf_path = await converter.run()
    print(f"PDF: {pdf_path}")

asyncio.run(convert())
```

#### Custom Template List

```python
import asyncio
from workflow import WorkflowOrchestrator

async def generate_with_custom_templates():
    orchestrator = WorkflowOrchestrator()
    
    # Use only specific templates
    template_list = ['coverpage.html', 'page1.html']
    
    pdf_path = await orchestrator.run(template_list=template_list)
    print(f"PDF generated: {pdf_path}")

asyncio.run(generate_with_custom_templates())
```

## 📝 Input Data Format

The `data.json` file should contain:

```json
{
  "offer_id": "1045",
  "date": "2025-11-12",
  "seller": {
    "company": "Company Name",
    "address": "Address",
    "nip": "Tax ID",
    "email": "email@company.com",
    "phone": "+48 123 456 789",
    "website": "www.company.com",
    "iban": "Bank Account"
  },
  "client": {
    "company": "Client Company",
    "email": "client@company.com",
    "phone": "123 456 789",
    "address": "Client Address"
  },
  "items": [
    {
      "id": 1,
      "name": "Product Name",
      "quantity": 100,
      "unit_price": 50.00,
      "discount": 10,
      "vat": 23,
      "total": 4500.00
    }
  ],
  "summary": {
    "vat": 1035.00,
    "total": 5535.00
  },
  "images": {
    "clientLogo": "url_or_path",
    "front": "url_or_path",
    "lid": "url_or_path"
  }
}
```

## 🎨 Templates

Templates are stored in the `templates/` folder and use Jinja2 syntax:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Offer {{ offer_id }}</title>
</head>
<body>
    <h1>{{ client.company }}</h1>
    <p>Date: {{ date }}</p>
    
    {% for item in items %}
    <div>
        <h3>{{ item.name }}</h3>
        <p>Price: {{ item.unit_price }}</p>
    </div>
    {% endfor %}
</body>
</html>
```

## ⚙️ Configuration

### Customizing Paths

```python
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    data_file_path="custom/path/data.json",
    templates_folder="custom/templates",
    html_output_folder="custom/html",
    pdf_output_folder="custom/pdf",
    cleanup_html=False  # Keep HTML files
)
```

### PDF Settings

Modify `htmlToPdf.py` in the `PDFConverter.convert_html_to_pdf()` method:

```python
await page.pdf(
    path=str(output_pdf_path),
    format='A4',  # or 'Letter', 'A3', etc.
    margin={
        'top': '20mm',
        'right': '20mm',
        'bottom': '20mm',
        'left': '20mm'
    },
    print_background=True,
    prefer_css_page_size=True
)
```

## 🔄 Workflow Process

1. **Validation Phase**
   - Check if data.json exists
   - Verify templates folder exists
   - Validate template files

2. **HTML Generation Phase**
   - Load JSON data
   - Initialize Jinja2 environment
   - Render each template with data
   - Save HTML files

3. **PDF Conversion Phase**
   - Load HTML files
   - Launch Playwright browser
   - Combine HTML files with page breaks
   - Generate PDF with proper formatting
   - Save to finalPdf folder

4. **Cleanup Phase** (optional)
   - Remove intermediate HTML files
   - Display success message

## 🐛 Troubleshooting

### Playwright Not Installed

```bash
pip install playwright
python -m playwright install chromium
```

### Template Not Found

- Ensure template files exist in `templates/` folder
- Check template names in `data.json` or code

### JSON Decode Error

- Validate your JSON file at [jsonlint.com](https://jsonlint.com)
- Ensure proper UTF-8 encoding

### Permission Errors

- Run with appropriate permissions
- Check folder write permissions

## 🧪 Testing

Test individual components:

```bash
# Test HTML generation only
python htmlGenerator.py

# Test PDF conversion only
python htmlToPdf.py

# Test complete workflow
python main.py
```

## 📄 Output

- **HTML Files**: Generated in `htmlGenerated/` (auto-deleted after PDF creation)
- **PDF File**: Generated in `finalPdf/` with client company name
  - Format: A4 with 20mm margins
  - Includes all styling and backgrounds
  - File naming: `{ClientCompanyName}.pdf`

## 🤝 Contributing

This is an internal project. For modifications:

1. Maintain OOP principles
2. Add docstrings to new methods
3. Update README for new features
4. Test thoroughly before deployment

## 📋 Requirements

- Python 3.7+
- jinja2
- playwright
- asyncio (built-in)

## 📞 Support

For issues or questions, contact the development team.

## 📜 License

Internal use only - CoffeeCups Sp. z o.o.

---

**Made with ☕ by CoffeeCups Team**

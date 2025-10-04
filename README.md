# PDF Generation API - Production Ready

A robust FastAPI-based PDF generation service that converts structured JSON data into professional PDF documents through HTML templating. Built with enterprise-grade error handling, validation, and production deployment support.

## 🚀 Features

- **REST API**: Professional FastAPI endpoints with OpenAPI documentation
- **Data Validation**: Comprehensive Pydantic models for input validation
- **Automated Workflow**: JSON → HTML → PDF in a single API call
- **High-Quality Output**: Browser-based PDF rendering with Playwright
- **Error Handling**: Detailed error responses and logging
- **Production Ready**: Windows compatibility, proper async handling, and monitoring
- **Auto-cleanup**: Removes intermediate files after PDF generation

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Production Deployment](#-production-deployment)
- [Configuration](#%EF%B8%8F-configuration)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

## 📦 Installation

### Prerequisites

- **Python 3.8+** (Required for Windows ProactorEventLoop)
- **pip** package manager
- **Windows/Linux/macOS** support

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd pdfGen
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```bash
python -m playwright install chromium
```

This downloads the Chromium browser (~150MB) required for PDF generation.

## 🎯 Quick Start

### Start the Server

**Development Mode:**
```bash
python main.py
```

**Production Mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --loop asyncio
```

**Windows Production (Recommended):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1
```

### Access API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Make Your First Request

**Using curl:**
```bash
curl -X POST "http://localhost:8000/generate-pdf" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

**Using Python:**
```python
import requests

with open('sample_request.json', 'r') as f:
    data = f.read()

response = requests.post(
    'http://localhost:8000/generate-pdf',
    headers={'Content-Type': 'application/json'},
    data=data
)

print(response.json())
```

## 📚 API Documentation

### Endpoints

#### `GET /`
Root endpoint - API information

**Response:**
```json
{
  "message": "PDF Generation API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### `GET /health`
Health check endpoint for monitoring

**Response:**
```json
{
  "status": "healthy",
  "service": "pdf-generation-api"
}
```

#### `POST /generate-pdf`
Generate PDF from offer data

**Request Body:**
```json
{
  "offer_id": "1045",
  "date": "2025-11-12",
  "seller": {
    "company": "CoffeeCups Sp. z o.o.",
    "address": "ul. Leśna 2, 55-220 Chwałowice",
    "nip": "9121725385",
    "email": "hello@coffeecups.com.pl",
    "phone": "+48 978 820 53",
    "website": "www.coffeecups.com.pl",
    "iban": "56 1050 1575 1000 0097 5152 2518"
  },
  "client": {
    "company": "Client Company Name",
    "email": "client@company.com",
    "phone": "+48 123 456 789",
    "address": "Client Address, City, Country"
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
    "clientLogo": "https://example.com/logo.jpg",
    "front": "https://example.com/front.jpg",
    "lid": "https://example.com/lid.jpg",
    "three_quarter": "https://example.com/three_quarter.jpg",
    "brand": "https://example.com/brand.jpg",
    "giftset": "https://example.com/giftset.jpg"
  }
}
```

**Success Response (201):**
```json
{
  "status": "success",
  "message": "PDF generated successfully",
  "pdf_path": "finalPdf/Client Company Name.pdf"
}
```

**Error Responses:**

**422 - Validation Error:**
```json
{
  "status": "error",
  "message": "Validation error - Invalid JSON structure",
  "details": "Field 'email' is not a valid email address"
}
```

**500 - Server Error:**
```json
{
  "status": "error",
  "message": "PDF generation workflow failed",
  "details": "Internal server error"
}
```

**504 - Timeout:**
```json
{
  "status": "error",
  "message": "PDF generation timed out - process took longer than 5 minutes"
}
```

### Request Validation Rules

| Field | Type | Validation |
|-------|------|------------|
| `offer_id` | string | Required, min length 1 |
| `date` | date | Required, ISO format (YYYY-MM-DD) |
| `seller.email` | string | Required, valid email format |
| `client.email` | string | Required, valid email format |
| `items` | array | Required, min 1 item |
| `items[].quantity` | integer | Required, > 0 |
| `items[].unit_price` | float | Required, > 0 |
| `items[].vat` | float | Required, 0-100 |
| `summary.total` | float | Required, > 0 |
| `images.*` | URL | Required, valid HTTP/HTTPS URL |

## 🚀 Production Deployment

### Environment Variables

Create a `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Paths
TEMPLATES_FOLDER=templates
HTML_OUTPUT_FOLDER=htmlGenerated
PDF_OUTPUT_FOLDER=finalPdf

# Timeouts (seconds)
PDF_GENERATION_TIMEOUT=300

# Cleanup
AUTO_CLEANUP_HTML=true
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p htmlGenerated finalPdf

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
```

**Build and Run:**
```bash
docker build -t pdf-generation-api .
docker run -p 8000:8000 -v $(pwd)/finalPdf:/app/finalPdf pdf-generation-api
```

### Windows Production Server

**Important for Windows:**

The API includes special handling for Windows event loop compatibility with Playwright.

**Start Command:**
```bash
# Single worker (recommended for Windows)
uvicorn main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1

# With auto-reload disabled (production)
python main.py
```

**Why `--loop asyncio`?**
- Forces uvicorn to use ProactorEventLoop on Windows
- Required for Playwright subprocess support
- Prevents `NotImplementedError` when launching browsers

### Linux/Unix Production Server

**Using systemd:**

Create `/etc/systemd/system/pdf-api.service`:

```ini
[Unit]
Description=PDF Generation API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pdf-api
Environment="PATH=/opt/pdf-api/venv/bin"
ExecStart=/opt/pdf-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --loop asyncio
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable pdf-api
sudo systemctl start pdf-api
sudo systemctl status pdf-api
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Increase timeout for PDF generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

### Load Balancing Considerations

**Important:** Due to Playwright's browser process management:

- **Single worker per instance** recommended
- Use multiple server instances with load balancer
- Each instance should have dedicated resources
- Avoid thread-based workers on Windows

## ⚙️ Configuration

### Application Configuration

Edit `main.py` configuration:

```python
# Logging level
logging.basicConfig(level=logging.INFO)  # Change to WARNING in production

# Timeout for PDF generation (seconds)
PDF_GENERATION_TIMEOUT = 300  # 5 minutes

# FastAPI configuration
app = FastAPI(
    title="PDF Generation API",
    description="API for generating PDFs from structured JSON data",
    version="1.0.0",
    docs_url="/docs",  # Set to None to disable in production
    redoc_url="/redoc"  # Set to None to disable in production
)
```

### Workflow Configuration

Customize workflow behavior in code:

```python
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    data_file_path="custom/data.json",
    templates_folder="custom/templates",
    html_output_folder="temp/html",
    pdf_output_folder="output/pdf",
    cleanup_html=True  # Auto-delete HTML files
)
```

### PDF Settings

Modify PDF generation settings in `htmlToPdf.py`:

```python
await page.pdf(
    path=str(output_pdf_path),
    format='A4',  # Paper size: A4, Letter, A3, etc.
    margin={
        'top': '20mm',
        'right': '20mm',
        'bottom': '20mm',
        'left': '20mm'
    },
    print_background=True,  # Include CSS backgrounds
    prefer_css_page_size=True,  # Use CSS @page size
    display_header_footer=False,  # Add header/footer
    scale=1.0  # Page scale (0.1 to 2.0)
)
```

## 🏗️ Architecture

### Project Structure

```
pdfGen/
├── main.py                    # FastAPI application & API endpoints
├── workflow.py                # Workflow orchestrator
├── htmlGenerator.py           # HTML template renderer
├── htmlToPdf.py              # PDF converter using Playwright
├── requirements.txt          # Python dependencies
├── sample_request.json       # Example API request
├── API_USAGE.md             # API usage examples
│
├── templates/               # Jinja2 HTML templates
│   ├── coverpage.html       # Cover page template
│   ├── page1.html          # Product details page
│   ├── page2.html          # Additional details
│   ├── page3.html          # Final page
│   └── endingpage.html     # Back cover
│
├── htmlGenerated/          # Temporary HTML files (auto-cleaned)
├── finalPdf/              # Generated PDF files
└── logos/                 # Static logo images
    ├── coffeecups.jpg
    └── client.jpg
```

### Component Architecture

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│              (main.py)                      │
│  - Request validation (Pydantic)            │
│  - Error handling                           │
│  - Response formatting                      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│       WorkflowOrchestrator                  │
│          (workflow.py)                      │
│  - Coordinates workflow                     │
│  - Validates inputs                         │
│  - Manages component lifecycle              │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌─────────────────┐  ┌──────────────────────┐
│ HTMLGenerator   │  │   PDFConverter       │
│                 │  │                      │
│ - Loads JSON    │  │ - Launches browser   │
│ - Renders       │  │ - Converts HTML      │
│   templates     │  │ - Generates PDF      │
│ - Saves HTML    │  │ - Cleanup files      │
└─────────────────┘  └──────────────────────┘
```

### Data Flow

```
JSON Request → Pydantic Validation → Save to File
                                          ↓
                                 WorkflowOrchestrator
                                          ↓
                                   HTMLGenerator
                                          ↓
                              Generate HTML Files
                                          ↓
                                   PDFConverter
                                          ↓
                              Launch Playwright Browser
                                          ↓
                                 Render & Print PDF
                                          ↓
                                  Cleanup HTML
                                          ↓
                              Return PDF Path
```

### Windows-Specific Implementation

The application includes special handling for Windows:

```python
# Line 18-20 in main.py
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

**Why this is needed:**
- Playwright launches browser as subprocess
- Windows default `SelectorEventLoop` doesn't support subprocesses
- `ProactorEventLoop` provides subprocess support
- Must be set before FastAPI/uvicorn starts

## 🐛 Troubleshooting

### Common Issues

#### 1. NotImplementedError on Windows

**Symptom:**
```
NotImplementedError at asyncio.create_subprocess_exec
```

**Solution:**
- Ensure `loop="asyncio"` in uvicorn.run()
- Restart server after changes
- Use `reload=False` in production

**Verify fix:**
```python
# Check main.py line 18-20
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Check main.py line 264
uvicorn.run(..., loop="asyncio")
```

#### 2. Playwright Browser Not Found

**Symptom:**
```
Error: Executable doesn't exist at ...
```

**Solution:**
```bash
python -m playwright install chromium
```

#### 3. Timeout Error

**Symptom:**
```
"detail": "PDF generation timed out"
```

**Solution:**
- Increase timeout in main.py (default 300s)
- Check server resources (CPU, RAM)
- Reduce image sizes in request
- Check network connectivity for remote images

#### 4. Memory Issues

**Symptom:**
- Server crashes during PDF generation
- Out of memory errors

**Solution:**
- Increase server RAM
- Use single worker mode
- Implement request queuing
- Clean up old PDF files regularly

#### 5. Permission Denied Errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'finalPdf/...'
```

**Solution:**
```bash
# Linux/Mac
chmod -R 755 finalPdf htmlGenerated

# Windows (run as administrator)
icacls finalPdf /grant Users:F
```

#### 6. Template Not Found

**Symptom:**
```
TemplateNotFound: coverpage.html
```

**Solution:**
- Verify templates folder exists
- Check template file names (case-sensitive on Linux)
- Ensure templates have .html extension

### Debug Mode

Enable detailed logging:

```python
# In main.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Monitoring

```bash
# Check if service is responding
curl http://localhost:8000/health

# Monitor logs (Linux with systemd)
sudo journalctl -u pdf-api -f

# Monitor logs (Docker)
docker logs -f <container_id>
```

## 📊 Performance

### Benchmarks

Typical performance metrics:

| Operation | Time | Notes |
|-----------|------|-------|
| API validation | <50ms | Pydantic validation |
| HTML generation | 100-300ms | Depends on template complexity |
| PDF conversion | 2-5s | Depends on page count & images |
| Total request | 3-8s | End-to-end |

### Optimization Tips

1. **Image Optimization**
   - Use compressed images
   - Prefer JPEG over PNG for photos
   - Resize images before upload

2. **Caching**
   - Cache template renders
   - Use CDN for static assets
   - Cache logo images

3. **Resource Management**
   - Clean old PDFs regularly
   - Monitor disk space
   - Set file retention policies

4. **Scaling**
   - Use multiple instances
   - Implement request queue
   - Consider async workers

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Disable `/docs` and `/redoc` in production
- [ ] Implement API authentication (API keys, JWT)
- [ ] Add rate limiting
- [ ] Validate and sanitize all inputs
- [ ] Use HTTPS (SSL/TLS)
- [ ] Set up firewall rules
- [ ] Implement request logging
- [ ] Regular security updates
- [ ] File upload size limits
- [ ] Sanitize file paths

### Example: Add API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secure-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/generate-pdf", dependencies=[Depends(verify_api_key)])
async def generate_pdf(offer_data: OfferData):
    # ... existing code
```

## 📝 Logging

### Log Levels

- **INFO**: Normal operations (API requests, PDF generation)
- **WARNING**: Recoverable issues (missing optional data)
- **ERROR**: Operation failures (PDF generation failed)
- **DEBUG**: Detailed debugging information

### Log Files

Configure log file output:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'pdf_api.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logging.getLogger().addHandler(handler)
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor error logs
- Check disk space

**Weekly:**
- Clean old PDF files
- Review performance metrics

**Monthly:**
- Update dependencies
- Security patches
- Backup configurations

### Getting Help

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review application logs
3. Test with `sample_request.json`
4. Contact development team

## 📄 License

Internal use only - CoffeeCups Sp. z o.o.

---

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Python](https://playwright.dev/python/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Made with ☕ by CoffeeCups Team**

# PDF Generation API Usage Guide

## Overview

This FastAPI application provides a REST API for generating PDFs from structured JSON data using the existing WorkflowOrchestrator.

## Features

- ✅ **Comprehensive Data Validation**: Pydantic models with detailed validation rules
- ✅ **Async Processing**: Non-blocking PDF generation using async/await
- ✅ **Error Handling**: Proper HTTP status codes and error responses
- ✅ **API Documentation**: Auto-generated OpenAPI/Swagger docs
- ✅ **Production Ready**: Logging, health checks, and proper exception handling

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python main.py
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Generate PDF
```bash
curl -X POST "http://localhost:8000/generate-pdf" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## Sample Request

Use the provided `sample_request.json` file or create your own JSON with the following structure:

```json
{
  "offer_id": "string",
  "date": "YYYY-MM-DD",
  "seller": {
    "company": "string",
    "address": "string", 
    "nip": "string",
    "email": "valid@email.com",
    "phone": "string",
    "website": "string",
    "iban": "string"
  },
  "client": {
    "company": "string",
    "email": "valid@email.com",
    "phone": "string",
    "address": "string"
  },
  "items": [
    {
      "id": 1,
      "name": "string",
      "quantity": 1,
      "unit_price": 0.0,
      "discount": 0.0,
      "vat": 0.0,
      "total": 0.0
    }
  ],
  "summary": {
    "vat": 0.0,
    "total": 0.0
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

## Response Format

### Success Response (201 Created)
```json
{
  "status": "success",
  "message": "PDF generated",
  "pdf_path": "/path/to/generated/file.pdf"
}
```

### Validation Error (422 Unprocessable Entity)
```json
{
  "status": "error",
  "message": "Validation error - Invalid JSON structure",
  "details": "Field 'email' is not a valid email address"
}
```

### Server Error (500 Internal Server Error)
```json
{
  "status": "error",
  "message": "Internal server error",
  "details": "PDF generation failed: [specific error message]"
}
```

## Testing with curl

### Basic Test
```bash
curl -X POST "http://localhost:8000/generate-pdf" \
  -H "Content-Type: application/json" \
  -d @sample_request.json \
  -w "\nHTTP Status: %{http_code}\n"
```

### Test with Pretty Print
```bash
curl -X POST "http://localhost:8000/generate-pdf" \
  -H "Content-Type: application/json" \
  -d @sample_request.json \
  | python -m json.tool
```

### Test Validation Error
```bash
curl -X POST "http://localhost:8000/generate-pdf" \
  -H "Content-Type: application/json" \
  -d '{"offer_id": "test", "invalid_field": "test"}' \
  -w "\nHTTP Status: %{http_code}\n"
```

## Data Validation Rules

### Required Fields
- All fields are required unless specified otherwise
- `items` array must contain at least one item
- All URLs in `images` must be valid HTTP/HTTPS URLs

### Validation Rules
- **Email fields**: Must be valid email format
- **Numeric fields**: 
  - `quantity`, `id`: Must be positive integers
  - `unit_price`, `total`: Must be positive floats
  - `discount`, `vat`: Must be non-negative floats
  - `vat`: Must be between 0 and 100 (percentage)
- **String fields**: Must be non-empty strings
- **Date field**: Must be valid ISO date format (YYYY-MM-DD)

## Error Handling

The API provides comprehensive error handling:

1. **422 Validation Error**: Invalid JSON structure or data types
2. **500 Internal Server Error**: PDF generation workflow failures
3. **Global Exception Handler**: Catches unexpected errors

## Logging

The application logs all operations:
- Request processing
- Data validation
- PDF generation workflow
- Errors and exceptions

Logs are written to stdout with INFO level by default.

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Configure database connections, API keys
2. **Reverse Proxy**: Use nginx or similar
3. **Process Manager**: Use gunicorn with uvicorn workers
4. **Monitoring**: Add health checks and metrics
5. **Security**: Add authentication and rate limiting

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

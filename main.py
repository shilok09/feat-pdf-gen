"""
FastAPI PDF Generation Service

This module provides a REST API for generating PDFs from JSON data using the existing
WorkflowOrchestrator. It includes comprehensive Pydantic models for data validation
and proper error handling following FastAPI best practices.
"""

import json
import logging
from datetime import date as Date
from pathlib import Path
from typing import List, Optional
import uuid
import asyncio
import sys

# Fix for Playwright on Windows - must be set before any async operations
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl, ValidationError, ConfigDict

from workflow import WorkflowOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Generation API",
    description="API for generating PDFs from structured JSON data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Pydantic Models for Data Validation
class SellerInfo(BaseModel):
    """Seller information model."""
    company: str = Field(..., min_length=1, description="Company name")
    address: str = Field(..., min_length=1, description="Company address")
    nip: str = Field(..., min_length=1, description="Tax identification number")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Email address")
    phone: str = Field(..., min_length=1, description="Phone number")
    website: str = Field(..., min_length=1, description="Website URL")
    iban: str = Field(..., min_length=1, description="IBAN number")


class ClientInfo(BaseModel):
    """Client information model."""
    company: str = Field(..., min_length=1, description="Client company name")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Client email address")
    phone: str = Field(..., min_length=1, description="Client phone number")
    address: str = Field(..., min_length=1, description="Client address")


class Item(BaseModel):
    """Individual item model."""
    id: int = Field(..., gt=0, description="Item ID")
    name: str = Field(..., min_length=1, description="Item name")
    quantity: int = Field(..., gt=0, description="Item quantity")
    unit_price: float = Field(..., gt=0, description="Unit price")
    discount: float = Field(..., ge=0, description="Discount percentage")
    vat: float = Field(..., ge=0, le=100, description="VAT percentage")
    total: float = Field(..., gt=0, description="Total price for this item")


class Summary(BaseModel):
    """Summary information model."""
    vat: float = Field(..., ge=0, description="Total VAT amount")
    total: float = Field(..., gt=0, description="Total amount")


class Images(BaseModel):
    """Images URLs model."""
    clientLogo: HttpUrl = Field(..., description="Client logo URL")
    front: HttpUrl = Field(..., description="Front view image URL")
    lid: HttpUrl = Field(..., description="Lid view image URL")
    three_quarter: HttpUrl = Field(..., description="Three quarter view image URL")
    brand: HttpUrl = Field(..., description="Brand image URL")
    giftset: HttpUrl = Field(..., description="Gift set image URL")


class OfferData(BaseModel):
    """Main offer data model for PDF generation."""
    offer_id: str = Field(..., min_length=1, description="Unique offer identifier")
    date: Date = Field(..., description="Offer date")
    seller: SellerInfo = Field(..., description="Seller information")
    client: ClientInfo = Field(..., description="Client information")
    items: List[Item] = Field(..., min_items=1, description="List of items in the offer")
    summary: Summary = Field(..., description="Offer summary")
    images: Images = Field(..., description="Image URLs")

    model_config = ConfigDict(
        json_encoders={
            Date: lambda v: v.isoformat()
        }
    )


class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation endpoint."""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF file")


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(..., description="Error status")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "PDF Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pdf-generation-api"}


@app.post(
    "/generate-pdf",
    response_model=PDFGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Validation Error - Invalid JSON structure"
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal Server Error - PDF generation failed"
        }
    }
)
async def generate_pdf(offer_data: OfferData) -> PDFGenerationResponse:
    """
    Generate PDF from offer data.
    
    This endpoint accepts structured offer data, validates it using Pydantic models,
    saves it to data.json, and triggers the PDF generation workflow.
    
    Args:
        offer_data: Validated offer data containing all necessary information
        
    Returns:
        PDFGenerationResponse: Status and path to generated PDF
        
    Raises:
        HTTPException: 422 for validation errors, 500 for processing errors
    """
    try:
        logger.info(f"Received PDF generation request for offer ID: {offer_data.offer_id}")
        
        # Save the validated data to data.json
        data_file_path = Path(f"data_{offer_data.offer_id}_{uuid.uuid4().hex[:8]}.json")
        with open(data_file_path, "w", encoding="utf-8") as f:
            json.dump(offer_data.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
        logger.info("Successfully saved offer data to data.json")
        
        # Simply call the workflow - it handles everything
        logger.info("Starting PDF generation workflow...")
        orchestrator = WorkflowOrchestrator()
        pdf_path = await asyncio.wait_for(
            orchestrator.run_with_custom_data(str(data_file_path)),
            timeout=300  # 5 minutes
        )
        
        # Validate PDF was generated successfully
        if pdf_path is None:
            logger.error("Workflow returned None - PDF generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF generation workflow failed"
            )
        
        # Validate PDF file exists
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found at path: {pdf_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF file not created at expected path: {pdf_path}"
            )
        
        logger.info(f"PDF generated successfully at: {pdf_path}")
        return PDFGenerationResponse(
            status="success",
            message="PDF generated successfully",
            pdf_path=pdf_path
        )
            
    except asyncio.TimeoutError:
        logger.error("PDF generation timed out after 5 minutes")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="PDF generation timed out - process took longer than 5 minutes"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in generate_pdf: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error - Invalid JSON structure",
            "details": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc) if app.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload on Windows for Playwright compatibility
        log_level="info",
        loop="asyncio"  # Force asyncio loop (uses ProactorEventLoop on Windows)
    )
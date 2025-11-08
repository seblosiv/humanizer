"""
FastAPI server for ClearCraft web application.

Provides REST API and serves HTMX+Tailwind frontend.
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn
from pathlib import Path

from clearcraft.config import settings
from clearcraft.analysis import TextAnalyzer, ReadabilityMetrics
from clearcraft.selector import TextSelector, RewriteResult
from clearcraft.exceptions import (
    ClearCraftError,
    SimilarityViolationError,
    ChangeRatioViolationError,
    DisallowedIntentError,
    TextTooLongError,
)

# Initialize FastAPI app
app = FastAPI(
    title="ClearCraft",
    description="Production-grade text clarity and readability enhancement API",
    version="1.0.0",
)

# Setup static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories if they don't exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize components
text_analyzer = TextAnalyzer()


# Pydantic models
class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint."""

    text: str = Field(..., min_length=1, max_length=50000)


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""

    metrics: Dict[str, Any]
    warnings: List[str] = []


class RewriteRequest(BaseModel):
    """Request model for rewrite endpoint."""

    text: str = Field(..., min_length=1, max_length=50000)
    tone: str = Field(default="neutral", pattern="^(neutral|academic|conversational)$")
    target_sentence_length_min: int = Field(default=14, ge=5, le=30)
    target_sentence_length_max: int = Field(default=22, ge=10, le=50)
    max_change_ratio: float = Field(default=0.30, ge=0.0, le=1.0)
    similarity_min: float = Field(default=0.92, ge=0.0, le=1.0)
    enable_llm: bool = Field(default=False)
    enable_disclosure: bool = Field(default=True)


class RewriteResponse(BaseModel):
    """Response model for rewrite endpoint."""

    original_text: str
    rewritten_text: str
    original_metrics: Dict[str, Any]
    rewritten_metrics: Dict[str, Any]
    changes: List[Dict[str, Any]]
    overall_similarity: float
    total_change_ratio: float
    disclosure_added: bool


# Helper functions
def metrics_to_dict(metrics: ReadabilityMetrics) -> Dict[str, Any]:
    """Convert ReadabilityMetrics to dictionary."""
    return {
        "flesch_reading_ease": round(metrics.flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(metrics.flesch_kincaid_grade, 2),
        "gunning_fog": round(metrics.gunning_fog, 2),
        "smog_index": round(metrics.smog_index, 2),
        "sentence_count": metrics.sentence_count,
        "avg_sentence_length": round(metrics.avg_sentence_length, 2),
        "avg_word_length": round(metrics.avg_word_length, 2),
        "mtld": round(metrics.mtld, 2) if metrics.mtld else None,
        "ttr": round(metrics.ttr, 3),
        "unique_words": metrics.unique_words,
        "total_words": metrics.total_words,
        "passive_ratio": round(metrics.passive_ratio, 3),
        "repetition_ratio": round(metrics.repetition_ratio, 3),
    }


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve main web interface."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "deepinfra_enabled": settings.is_deepinfra_enabled,
        },
    )


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for readability metrics.

    Args:
        request: AnalyzeRequest with text.

    Returns:
        AnalyzeResponse with metrics and warnings.

    Raises:
        HTTPException: If analysis fails.
    """
    try:
        # Check text length
        if len(request.text) > settings.max_text_length:
            raise TextTooLongError(len(request.text), settings.max_text_length)

        # Analyze
        analysis_result = text_analyzer.analyze(request.text)
        metrics = metrics_to_dict(analysis_result.metrics)

        # Generate warnings
        warnings = []
        if analysis_result.metrics.avg_sentence_length > 25:
            warnings.append("Average sentence length is high. Consider breaking up long sentences.")

        if analysis_result.metrics.passive_ratio > 0.20:
            warnings.append(
                f"High passive voice usage ({analysis_result.metrics.passive_ratio:.1%}). "
                "Consider using more active voice."
            )

        if analysis_result.metrics.repetition_ratio > 0.15:
            warnings.append("High repetition detected. Consider varying your language.")

        return AnalyzeResponse(metrics=metrics, warnings=warnings)

    except TextTooLongError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClearCraftError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    """
    Rewrite text for improved clarity.

    Args:
        request: RewriteRequest with text and options.

    Returns:
        RewriteResponse with original, rewritten text and metrics.

    Raises:
        HTTPException: If rewriting fails or violates guardrails.
    """
    try:
        # Check text length
        if len(request.text) > settings.max_text_length:
            raise TextTooLongError(len(request.text), settings.max_text_length)

        # Initialize selector
        selector = TextSelector(
            target_avg_sentence_length=(
                request.target_sentence_length_min,
                request.target_sentence_length_max,
            ),
            max_change_ratio=request.max_change_ratio,
            similarity_min=request.similarity_min,
            enable_llm=request.enable_llm,
        )

        # Rewrite
        result = selector.rewrite(
            text=request.text,
            tone=request.tone,
            enable_disclosure=request.enable_disclosure,
        )

        # Convert to response
        changes = [
            {
                "pass_name": op.pass_name,
                "tokens_changed": op.tokens_changed,
                "confidence": round(op.confidence, 2),
                "reason": op.reason,
                "similarity_score": round(op.similarity_score, 3) if op.similarity_score else None,
            }
            for op in result.change_operations
        ]

        return RewriteResponse(
            original_text=result.original_text,
            rewritten_text=result.rewritten_text,
            original_metrics=metrics_to_dict(result.original_metrics),
            rewritten_metrics=metrics_to_dict(result.rewritten_metrics),
            changes=changes,
            overall_similarity=round(result.overall_similarity, 3),
            total_change_ratio=round(result.total_change_ratio, 3),
            disclosure_added=result.disclosure_added,
        )

    except DisallowedIntentError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SimilarityViolationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Similarity violation: {e.similarity:.3f} < {e.threshold:.3f}. "
            "Changes would alter meaning too much.",
        )
    except ChangeRatioViolationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Change ratio violation: {e.change_ratio:.3f} > {e.max_ratio:.3f}. "
            "Too many changes requested.",
        )
    except TextTooLongError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClearCraftError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(e)}")


# HTMX endpoints for real-time UI updates
@app.post("/htmx/analyze", response_class=HTMLResponse)
async def htmx_analyze(request: Request, text: str = Form(...)):
    """HTMX endpoint for real-time analysis."""
    try:
        analysis_result = text_analyzer.analyze(text)
        metrics = metrics_to_dict(analysis_result.metrics)

        return templates.TemplateResponse(
            "components/analyze.html",
            {
                "request": request,
                "metrics": metrics,
            },
        )
    except Exception as e:
        return f'<div class="text-red-600">Analysis failed: {str(e)}</div>'


def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "clearcraft.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run_server()

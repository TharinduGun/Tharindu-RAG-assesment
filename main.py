# FastAPi endpoint to handle RAG assessment requests
"""
FastAPI application exposing a RAG endpoint for the Transformer paper.

The API provides a single main endpoint:
- POST /ask: accepts a natural-language question and returns an answer
  generated using retrieval-augmented generation (RAG) over the paper

health check endpoint is also provided.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import AnswerResponse, Question
from rag_engine import RagEngine

# Configure basic logging for the API module.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from a .env file if present.
# This is where GEMINI_API_KEY would typically be defined.
load_dotenv()

app = FastAPI(
    title="RAG API - Attention Is All You Need",
    description=(
        "A Retrieval-Augmented Generation (RAG) service that answers "
        "questions about the paper 'Attention Is All You Need'."
    ),
    version="0.1.0",
)
# Configure CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global reference to the RAG engine instance.
_rag_engine: Optional[RagEngine] = None


@app.on_event("startup")
def startup_event() -> None:
    """
    Application startup hook.

    This function is executed once when the FastAPI application starts. It
    initialises the RagEngine by ingesting the source PDF and building the
    vector store and LLM client. If initialisation fails, the exception is
    logged and the engine will remain unavailable until the issue is fixed.
    """
    global _rag_engine

    pdf_path = Path("data/attention.pdf")
    logger.info("Initialising RagEngine with PDF: %s", pdf_path)

    try:
        _rag_engine = RagEngine(pdf_path=pdf_path)
        logger.info("System initialised successfully.")
    except Exception as exc:  
        logger.exception("Failed to initialise system: %s", exc)
        _rag_engine = None


@app.get("/health", summary="Health check")
def health_check() -> dict[str, str]:
    """
    Simple health-check endpoint.

    Returns a basic status message indicating whether the API is running and
    the RAG system has been initialised.
    """
    engine_status = "ready" if _rag_engine is not None else "uninitialised"
    return {"status": "ok", "rag_engine": engine_status}


@app.post(
    "/ask",
    response_model=AnswerResponse,
    summary="Ask a question about the Transformer paper",
)
def ask(question: Question) -> AnswerResponse:
    """
    Answer a question about the paper usibg retrieval-augmented generation.
    """
    if _rag_engine is None:
        raise HTTPException(
            status_code=503, detail="RAG engine is not initialised. Check server logs."
        )

    try:
        return _rag_engine.answer_question(question.question)
    except HTTPException:
        # Propagate FastAPI HTTPExceptions unchanged.
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error while answering question: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the answer.",
        ) from exc

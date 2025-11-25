"""
Streamlit UI for the RAG API
"""
from __future__ import annotations
import os
from typing import Any, Dict
import requests
import streamlit as st

# API URL
DEFAULT_API_URL = "http://localhost:8000/ask"
API_URL = os.getenv("RAG_API_URL", DEFAULT_API_URL)

def call_rag_api(question: str) -> Dict[str, Any]:
    """
     POST/ask endpoint is called with given question in natural language with parsed JSON response from the API.
    """
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": f"Request to RAG API failed: {exc}"}


def main() -> None:
    """
    Main Streamlit app function.
    """
    st.set_page_config(page_title="RAG: Chat with Transformer Paper", layout="wide")

    st.title("Chat with your Document using RAG powered by Gemini")
    st.markdown(
        "Ask questions about the research paper **'Attention Is All You Need'**. "
        
    )

    with st.sidebar:
        st.header("API Configuration")
        st.text_input(
            "RAG API URL",
            value=API_URL,
            help="URL of the FastAPI /ask endpoint.",
            key="api_url_display",
            disabled=True,
        )

    question: str = st.text_area(
        "Your question",
        placeholder="e.g. What problem does the Transformer architecture solve?",
        height=100,
    )

    if st.button("Submit", type="primary"):
        if not question.strip():
            st.warning("Please enter a question before submitting.")
            return

        with st.spinner("Querying RAG API and generating answer..."):
            result = call_rag_api(question.strip())

        if "error" in result:
            st.error(result["error"])
            return

        st.subheader("Answer")
        st.write(result.get("answer", ""))

        st.subheader("Context (retrieved from the paper)")
        st.text_area(
            label="",
            value=result.get("context", ""),
            height=300,
        )


if __name__ == "__main__":
    main()

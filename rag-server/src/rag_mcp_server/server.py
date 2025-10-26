#!/usr/bin/env python3
import argparse
import json
from typing import Optional, Dict, Any
from pathlib import Path
from .core.db import RAGDatabase
from fastmcp import FastMCP
from .models.models import (
    QuestionRequest,
    EmbedDocumentResponse,
    SearchDocumentsResponse,
    DatabaseStatsResponse,
    DeleteDocumentResponse,
    ListDocumentsResponse,
    GetDocumentResponse,
    DocumentChunk,
    DocumentInfo,
    QuestionAnswer
)
from dotenv import load_dotenv
import logging
import os
import sys
# Load environment variables from .env file
load_dotenv()

# Initialize the RAG database with the provided path
# db_path = os.getenv("RAG_DB_PATH", "src/database/rag_database.db")
# rag_db = None  # Will be initialized after parsing arguments

# Create FastMCP server
mcp = FastMCP(
    name="RAG Server", 
    instructions="""
    You are a Retrieval-Augmented Generation (RAG) server that manages a vector database of documents.
    You can embed documents, search for similar documents, and manage the database.
    Use the tools provided to interact with the database.
    """
)

# Configure logger
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("rag_mcp_server")

@mcp.tool()
def embed_document(file_path: str, metadata: Optional[dict] = None) -> EmbedDocumentResponse:
    """
    Embed a document file into the vector database.
    
    Args:
        file_path: Path to the document file to embed (PDF, DOCX, TXT, MD)
        metadata: Optional metadata dictionary to store with the document
    
    Returns:
        Status message about the embedding operation
    """
    result = rag_db.embed_document(file_path, metadata)
    if result["success"]:
        return EmbedDocumentResponse(
            success=True,
            filename=result.get("filename"),
            chunks_added=result.get("chunks_added"),
            total_characters=result.get("total_characters"),
            message=f"✅ Document '{result['filename']}' embedded! {result['chunks_added']} chunks created from {result['total_characters']} characters. 🚀"
        )
    else:
        return EmbedDocumentResponse(
            success=False,
            error=result.get("error"),
            message=f"❌ Oops! Failed to embed document: {result['error']} 😢"
        )

@mcp.tool()
def search_documents(query: str, top_k: int = 5, min_similarity: float = 0.4) -> SearchDocumentsResponse:
    """
    Search for similar documents using natural language query.
    
    Args:
        query: Natural language search query
        top_k: Number of results to return (default: 5)
        min_similarity: Minimum similarity threshold (default: 0.4)
    
    Returns:
        Formatted search results with similarity scores
    """
    results = rag_db.search_similar(query, top_k, min_similarity)
    if not results:
        return SearchDocumentsResponse(results=[], message="🔍 No similar documents found for your query. Try another search! 🕵️‍♂️")
    return SearchDocumentsResponse(
        results=results,
        message=f"🔍 Found {len(results)} similar document{'s' if len(results)!=1 else ''}! 📄✨"
    )

@mcp.tool()
def get_database_stats() -> DatabaseStatsResponse:
    """
    Get comprehensive statistics about the RAG database.
    
    Returns:
        Formatted database statistics including file counts and embedding info
    """
    stats = rag_db.get_stats()
    # If get_stats returns a DocumentInfo summary, wrap in list for files
    files = [stats] if isinstance(stats, DocumentInfo) else getattr(stats, 'files', [])
    return DatabaseStatsResponse(
        total_documents=len(files),
        total_chunks=getattr(stats, 'chunks', 0),
        embedding_model=getattr(stats, 'embedding_model', ''),
        database_path=getattr(stats, 'database_path', ''),
        files=files,
        message=f"📊 Database loaded! {len(files)} document{'s' if len(files)!=1 else ''} and {getattr(stats, 'chunks', 0)} chunk{'s' if getattr(stats, 'chunks', 0)!=1 else ''} stored. 🗂️"
    )

@mcp.tool()
def delete_document(filename: str) -> DeleteDocumentResponse:
    """
    Delete all chunks of a specific document from the database.
    
    Args:
        filename: Name of the file to delete from the database
    
    Returns:
        Status message about the deletion operation
    """
    result = rag_db.delete_document(filename)
    if result["success"]:
        return DeleteDocumentResponse(
            success=True,
            filename=result.get("filename"),
            chunks_deleted=result.get("chunks_deleted"),
            message=f"🗑️ Document '{result['filename']}' deleted! {result['chunks_deleted']} chunks removed. 👋"
        )
    else:
        return DeleteDocumentResponse(
            success=False,
            error=result.get("error"),
            message=f"❌ Could not delete document: {result['error']} 😬"
        )

@mcp.tool()
def list_documents() -> ListDocumentsResponse:
    """
    List all documents currently in the database.
    
    Returns:
        Formatted list of all documents with their chunk counts
    """
    stats = rag_db.get_stats()
    files = [stats] if isinstance(stats, DocumentInfo) else getattr(stats, 'files', [])
    return ListDocumentsResponse(
        total_documents=len(files),
        files=files,
        message=(
            f"📚 {len(files)} document{'s' if len(files)!=1 else ''} in the database! 🗃️" if files else "📭 No documents in database. Add some to get started! ✨"
        )
    )

@mcp.tool()
async def ask_question(request: QuestionRequest) -> QuestionAnswer:
    """Ask a question and get an answer using RAG
    
    Args:
        question: The question to answer
        context_limit: Maximum number of context chunks (default: 5)
        similarity_threshold: Minimum similarity for context (optional)
    
    Returns:
        Answer with context, sources, and confidence score
    """
    try:
        answer = await rag_db.ask_question(
            question=request.question,
            context_limit=request.context_limit,
            similarity_threshold=request.similarity_threshold
        )
        return answer
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return QuestionAnswer(
            question=request.question,
            answer="I'm sorry, I couldn't process your question due to an error.",
            context_chunks=[],
            sources=[],
            confidence=0.0
        )

@mcp.tool()
async def get_document(document_id: str) -> GetDocumentResponse:
    """Get detailed information about a specific document
    
    Args:
        document_id: ID of the document to retrieve
    
    Returns:
        Document information or error message
    """
    try:
        doc_info = await rag_db.get_document_info(document_id)
        if doc_info:
            return GetDocumentResponse(document=doc_info)
        else:
            return GetDocumentResponse(error=f"Document {document_id} not found", document_id=document_id)
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return GetDocumentResponse(error=str(e), document_id=document_id)

def run():
    parser = argparse.ArgumentParser(description="Run the RAG MCP server using HTTP or stdio transport")
    parser.add_argument("--mode", choices=["http", "stdio"], default=os.getenv("MCP_TRANSPORT", "http"),
                        help="Transport mode to run the MCP server: 'http' (default) or 'stdio'")
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"), help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", 8000)), help="Port for HTTP transport")
    parser.add_argument("--db-path", default=os.getenv("RAG_DB_PATH", "./data/rag_database.db"),
                        help="Path to the SQLite database file (default: ./data/rag_database.db)")
    parser.add_argument("--hf-key", default=os.getenv("HF_TOKEN", None),
                        help="Hugging Face API key/token. If provided, will set HUGGINGFACEHUB_API_TOKEN and HF_HUB_TOKEN env vars.")
    args = parser.parse_args()

    # If a Hugging Face key was provided, export it for downstream libraries
    if args.hf_key:
        os.environ.setdefault("HF_HUB_TOKEN", args.hf_key)

    # Create database directory if it doesn't exist
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize the RAG database with the provided path
    global rag_db
    rag_db = RAGDatabase(db_path=str(db_path))

    if args.mode == "http":
        logger.info(f"Starting MCP server over HTTP on {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        logger.info("Starting MCP server over stdio")
        # FastMCP supports multiple transports; if stdio is supported we pass it directly.
        # If the installed FastMCP does not support stdio transport, this will raise and surface the error.
        try:
            mcp.run(transport="stdio")
            # Fallback: if fastmcp doesn't accept 'stdio' as a transport argument, attempt to call without kwargs
            # or re-raise to let the user know.
        except Exception as e:
            logger.error("Failed to start stdio transport: %s", e)
            raise

if __name__ == "__main__":
    run()

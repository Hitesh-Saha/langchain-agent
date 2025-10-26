from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import sqlite3
import numpy as np
import PyPDF2
from docx import Document
import json
from ..models.models import QuestionAnswer, DocumentChunk, DocumentInfo, EmbedDocumentResponse, DeleteDocumentResponse
from .config import get_Embedder

class RAGDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model = get_Embedder()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing documents and embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename);
        ''')
        
        conn.commit()
        conn.close()
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() == '.pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        
        elif path.suffix.lower() == '.docx':
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        elif path.suffix.lower() in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def embed_document(self, file_path: str, metadata: Optional[Dict] = None) -> EmbedDocumentResponse:
        """Process and embed documents into the vector database"""
        try:
            text = self.extract_text_from_file(file_path)
            chunks = self.chunk_text(text)
            if not chunks:
                raise ValueError("No content could be extracted from the file")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            filename = Path(file_path).name
            documents_added = 0
            for i, chunk in enumerate(chunks):
                embedding = self.model.feature_extraction(chunk)
                embedding_blob = embedding.tobytes()
                cursor.execute('''
                    INSERT INTO documents (filename, content, chunk_id, embedding, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filename, chunk, i, embedding_blob, json.dumps(metadata or {})))
                documents_added += 1
            conn.commit()
            conn.close()
            return EmbedDocumentResponse(
                success=True,
                filename=filename,
                chunks_added=documents_added,
                total_characters=len(text),
                message=f"Successfully embedded '{filename}' - {documents_added} chunks created from {len(text)} characters."
            )
        except Exception as e:
            return EmbedDocumentResponse(
                success=False,
                error=str(e),
                message=f"Failed to embed document: {str(e)}"
            )
    
    def search_similar(self, query: str, top_k: int = 5, min_similarity: float = 0.0) -> List[DocumentChunk]:
        """Search for similar documents using vector similarity"""
        query_embedding = self.model.feature_extraction(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, content, chunk_id, embedding, metadata, created_at 
            FROM documents
        ''')
        results = []
        for row in cursor.fetchall():
            doc_id, filename, content, chunk_id, embedding_blob, metadata, created_at = row
            doc_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            if similarity >= min_similarity:
                results.append(DocumentChunk(
                    id=doc_id,
                    filename=filename,
                    content=content,
                    chunk_id=chunk_id,
                    similarity=float(similarity),
                    metadata=json.loads(metadata) if metadata else {},
                    created_at=created_at
                ))
        conn.close()
        results.sort(key=lambda x: x.similarity if x.similarity is not None else 0, reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> DocumentInfo:
        """Get statistics about the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        total_chunks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT filename) FROM documents')
        unique_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT filename, COUNT(*) as chunk_count FROM documents GROUP BY filename')
        files_info = cursor.fetchall()
        
        conn.close()
        
        # Compose DocumentInfo for each file
        files = [
            DocumentInfo(
                filename=f[0],
                chunks=f[1],
                embedding_model='all-MiniLM-L6-v2',
                database_path=self.db_path
            ) for f in files_info
        ]
        # Return a summary DocumentInfo (for backward compatibility)
        return DocumentInfo(
            filename='*',
            chunks=total_chunks,
            chunk_details=None,
            embedding_model='all-MiniLM-L6-v2',
            database_path=self.db_path
        )
    
    def delete_document(self, filename: str) -> DeleteDocumentResponse:
        """Delete all chunks of a specific document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents WHERE filename = ?', (filename,))
        chunks_to_delete = cursor.fetchone()[0]
        
        if chunks_to_delete == 0:
            conn.close()
            return DeleteDocumentResponse(
                success=False,
                error="Document not found",
                message="Document not found"
            )
        cursor.execute('DELETE FROM documents WHERE filename = ?', (filename,))
        conn.commit()
        conn.close()
        return DeleteDocumentResponse(
            success=True,
            filename=filename,
            chunks_deleted=chunks_to_delete,
            message=f"Successfully deleted '{filename}' - {chunks_to_delete} chunks removed."
        )

    async def ask_question(
        self, 
        question: str, 
        context_limit: int = 5,
        similarity_threshold: float = None
    ) -> QuestionAnswer:
        """Answer a question using RAG"""
        try:
            # Search for relevant context
            search_results = await self.search_similar(
                question, 
                limit=context_limit,
                similarity_threshold=similarity_threshold
            )
            
            if not search_results:
                return QuestionAnswer(
                    question=question,
                    answer="I couldn't find any relevant information to answer your question.",
                    context_chunks=[],
                    sources=[],
                    confidence=0.0
                )
            
            # TODO: Integrate with LLM for answer generation
            # For now, return context-based response
            context_text = "\n\n".join([
                f"Source: {result.filename}\n{result.content}"
                for result in search_results
            ])
            
            # Calculate confidence based on top similarity scores
            top_scores = [result.similarity for result in search_results[:3]]
            confidence = sum(top_scores) / len(top_scores) if top_scores else 0.0
            
            # Placeholder answer - replace with actual LLM integration
            answer = (
                f"Based on the available documents, here's what I found:\n\n"
                f"The most relevant information comes from {len(search_results)} sources. "
                f"Here are the key points from the top results:\n\n"
                + "\n".join([
                    f"• {result.content[:200]}..." 
                    for result in search_results[:3]
                ])
                + f"\n\n[Note: This is a placeholder response. "
                f"Integrate with an LLM service for proper answer generation.]"
            )
            
            sources = list(set([result.filename for result in search_results]))
            
            logger.info(f"Generated answer for question with {len(search_results)} context chunks")
            
            return QuestionAnswer(
                question=question,
                answer=answer,
                context_chunks=search_results,
                sources=sources,
                confidence=min(confidence, 1.0)
            )
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            raise

    def get_document_info(self, document_id: str) -> Optional[DocumentChunk]:
        """Retrieve detailed information about a specific document by its ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, content, chunk_id, metadata, created_at 
                FROM documents WHERE id = ?
            ''', (document_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                doc_id, filename, content, chunk_id, metadata, created_at = row
                return DocumentChunk(
                    id=doc_id,
                    filename=filename,
                    content=content,
                    chunk_id=chunk_id,
                    metadata=json.loads(metadata) if metadata else {},
                    created_at=created_at
                )
            return None

        except Exception as e:
            logger.error(f"Error retrieving document info: {e}")
            return None
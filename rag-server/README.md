# RAG MCP Server

A Retrieval Augmented Generation (RAG) server implementing the Model Context Protocol (MCP). This server allows you to embed, search, and manage documents using vector database technology, making it perfect for use with AI tools and Large Language Models (LLMs).

## ✨ Features

- 📚 **Document Embedding**: Support for multiple document formats (PDF, DOCX, TXT, MD)
- 🔍 **Semantic Search**: Search through documents using natural language queries
- 💾 **Vector Database**: Efficient storage and retrieval of document embeddings
- 🤖 **MCP Protocol**: Implements the Model Context Protocol for standardized AI/ML service interactions
- 🔧 **Easy-to-use API**: Simple interface for document management and search
- 🔄 **Dual Mode**: Supports both HTTP and stdio communication modes

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip for package management
- Docker (optional, for containerized deployment)

### Installation Methods

#### 1. Using `uv` (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/Hitesh-Saha/RAG-MCP-Server.git
cd RAG-MCP-Server

# Install dependencies
uv sync
```

#### 2. Using `pip`

```bash
git clone https://github.com/Hitesh-Saha/RAG-MCP-Server.git
cd RAG-MCP-Server
pip install -e .
```

## 🖥️ Running the Server

### 1. Local Run (Source Mode)

#### HTTP Mode
```bash
# Run using the src package layout
PYTHONPATH=src python -m rag_mcp_server.server --mode http --port 8000
```

#### stdio Mode
```bash
# For stdio mode (useful for IDE integrations)
PYTHONPATH=src python -m rag_mcp_server.server --mode stdio
```

### 2. Using `uv run`

```bash
# HTTP mode
uv run rag-mcp-server --mode http --port 8000

# stdio mode
uv run rag-mcp-server --mode stdio
```

### 3. Docker Setup

```bash
# Build the image
docker build -t rag-mcp-server .

# Run in HTTP mode
docker run -p 8000:8000 rag-mcp-server

# Run in stdio mode
docker run -i rag-mcp-server --mode stdio
```

## 🔌 IDE Integration

### VS Code Setup

1. Install the Claude AI Assistant or GitHub Copilot extension

2. Configure the MCP Server:
   - Start the RAG MCP server in either HTTP or stdio mode
   - For HTTP mode, use endpoint: `http://localhost:8000/mcp`
   - For stdio mode, point the extension to the server process

3. VS Code Settings:
   ```jsonc
   {
     "claude.mcp.endpoint": "http://localhost:8000/mcp",  // For HTTP mode
     // OR
     "github.copilot.advanced": {
       "mcpServer": "http://localhost:8000/mcp"  // For HTTP mode
     }
   }
   ```

### Claude Desktop Setup

1. Start the RAG MCP server in HTTP mode:
   ```bash
   uv run rag-mcp-server --mode http --port 8000
   ```

2. Configure Claude Desktop:
   - Open Settings
   - Navigate to the "Advanced" section
   - Set MCP Server URL to: `http://localhost:8000/mcp`
   - Click "Test Connection" to verify

## 🧪 Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/Hitesh-Saha/RAG-MCP-Server.git
cd RAG-MCP-Server

# Install in editable mode with dev dependencies
uv sync

# Run tests
python -m pytest

# Run with auto-reload for development
uvicorn rag_mcp_server.server:app --reload --port 8000
```

### Environment Variables

Create a `.env` file in the project root:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_DB_PATH=./data/vector_db
LOG_LEVEL=INFO
```

## 📦 Building and Distribution

### Build Package

```bash
# Using uv
uv pip build .

# Using pip
pip install build
python -m build
```

### Install from Built Package

```bash
uv pip install dist/rag_mcp_server-0.1.0.whl
```

## � API Documentation

When running in HTTP mode, visit:
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Spec: `http://localhost:8000/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
license = { text = "MIT" }
keywords = ["mcp", "rag", "vector", "embedding"]
classifiers = [
	"Development Status :: 4 - Beta",
	"License :: OSI Approved :: MIT License",
	"Programming Language :: Python :: 3",
]
```

2) Ensure console script entry point is configured

We added a console script in `pyproject.toml`:

```toml
[project.scripts]
rag-mcp-server = "rag_mcp_server.cli:run"
```

This maps the `rag-mcp-server` command to `rag_mcp_server.cli.run()`.

3) Build distributions

Install build tools (if you don't have them):

```bash
pip install --upgrade build twine
```

Build source and wheel:

```bash
python -m build
# artifacts appear in dist/
```

4) Test upload to Test PyPI (recommended)

```bash
python -m twine upload --repository testpypi dist/*

# Verify install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps rag-mcp-server
```

5) Publish to PyPI

When ready, upload to the real PyPI:

```bash
python -m twine upload dist/*
```

6) Verify

```bash
pip install rag-mcp-server
rag-mcp-server --mode http --port 8000
```

Tips & best practices

- Use a dedicated PyPI account and enable 2FA.
- Increment the `version` for each release and tag releases in Git (e.g. `git tag v0.1.0`).
- Add automated publishing via GitHub Actions on tag push to streamline releases (I can add a template workflow if you want).
- Keep secrets out of the repo; store PyPI API tokens in CI secrets and use Twine in CI for publishing.

## 🧭 Install & run after publishing

Once published to PyPI, users can install and run the server easily.

Install via pip:

```bash
pip install rag-mcp-server
```

Run with `uv` (recommended) — `uv` will locate the package's entry point and run it. Example (after installing `uv`):

```bash
# Run the server (default HTTP on 127.0.0.1:8000)
uv run rag-mcp-server

# Or run via the console script directly (if project.scripts was configured):
rag-mcp-server --mode http --port 8000
```

If you'd rather run the module directly:

```bash
python -m rag_mcp_server.server --mode http
```

## 🧪 Smoke test / verification

After installing, try a quick health check (HTTP mode):

```bash
curl -v http://127.0.0.1:8000/health || true
```

For stdio mode, use a compliant MCP client that writes Content-Length framed JSON requests and reads framed responses.

## 🐳 Docker notes (packaged)

The included `Dockerfile` already uses `uv` to run the server. When packaging, you can either:

- Build the Docker image from the source (as-is), or
- Use the PyPI package inside a smaller runtime image (multi-stage build): install the published wheel with `pip install rag-mcp-server` and run the console script.

Example Docker command (after publishing to PyPI):

```Dockerfile
FROM python:3.12-slim
RUN pip install rag-mcp-server uv
CMD ["uv", "run", "rag-mcp-server"]
```


---

## �🛠️ API & Tool Usage


### 📥 Embed a Document
Embed a document into the vector database:
```python
embed_document(file_path: str, metadata: Optional[dict] = None) -> EmbedDocumentResponse
```
**Response Model:** `EmbedDocumentResponse`
**Example Response:**
```
✅ Document 'example.pdf' embedded! 3 chunks created from 7539 characters. 🚀
```



### 🔍 Search Documents
Search through embedded documents using natural language:
```python
search_documents(query: str, top_k: int = 5, min_similarity: float = 0.4) -> SearchDocumentsResponse
```
**Response Model:** `SearchDocumentsResponse`
**Example Response:**
```
🔍 Found 2 similar documents! 📄✨
1. 📄 somatosensory.pdf (chunk 0) | 📊 Similarity: 0.53
   📝 This is a sample document to showcase page-based formatting...
```



### 📚 List Documents
View all documents in the database:
```python
list_documents() -> ListDocumentsResponse
```
**Response Model:** `ListDocumentsResponse`
**Example Response:**
```
📚 2 documents in the database! 🗃️
1. 📄 somatosensory.pdf (3 chunks)
2. 📄 TopCSSFrameworks.docx (2 chunks)
```



### 📊 Get Database Stats
View statistics about the database:
```python
get_database_stats() -> DatabaseStatsResponse
```
**Response Model:** `DatabaseStatsResponse`
**Example Response:**
```
📊 Database loaded! 2 documents and 5 chunks stored. 🗂️
```



### 🗑️ Delete Document
Remove a document from the database:
```python
delete_document(filename: str) -> DeleteDocumentResponse
```
**Response Model:** `DeleteDocumentResponse`
**Example Response:**
```
🗑️ Document 'example.pdf' deleted! 3 chunks removed. 👋
```

### ❓ Ask a Question
Ask a question and get an answer using the RAG system:
```python
ask_question(request: QuestionRequest) -> QuestionAnswer
```
**Request Model:** `QuestionRequest`
**Response Model:** `QuestionAnswer`
**Example Response:**
```
🤖 Answer: The somatosensory system consists of sensors in the skin, muscles, tendons, and joints...
Sources: somatosensory.pdf
Confidence: 0.92
```

### 📄 Get Document Details
Get detailed information about a specific document chunk by its ID:
```python
get_document(document_id: str) -> GetDocumentResponse
```
**Response Model:** `GetDocumentResponse`
**Example Response:**
```
{
	"document": {
		"id": 3,
		"filename": "somatosensory.pdf",
		"content": "This is a sample document...",
		"chunk_id": 0,
		"metadata": {},
		"created_at": "2025-08-20 09:38:11"
	}
}
```


---

## ⚙️ Technical Details

- Embedding Model: all-MiniLM-L6-v2
- Database: SQLite-based vector database
- Protocol: Model Context Protocol (MCP) via FastMCP


---

## 📄 License

This project is licensed under the terms included in the LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

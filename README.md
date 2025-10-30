# langchain-agent

A small example workspace that includes:

- a lightweight RAG MCP server (`rag-server`) which exposes tools for embedding, searching, listing and managing documents
- an example agent integration that connects to the RAG MCP server and can use the RAG tools

This README describes how to set up the environment, start the RAG server, and run the agent or example client code.

## Prerequisites

- Python 3.12 or newer
- git (optional)
- uv
- Huggingface API Key
- Google Gemini API Key

The repository uses two separate Python packages under this folder:

- `.` — the `langchain-agent` package (main agent code) (pyproject.toml present)
- `./rag-server` — the RAG MCP server package (pyproject.toml present)

## Quick setup

From the project root (/workspaces/codespaces-blank/langchain-agent):

1. Create and activate a virtual environment

```bash

    uv sync --frozen

```

2. Create a .env file in the project root with the required environment variables (see below).

```bash

    GOOGLE_API_KEY=<your_google_api_key_here>
    RAG_MCP_SERVER_URL=<your_rag_mcp_server_url_here>
    LANGSMITH_API_KEY=<your_langsmith_api_key_here>
    GOOGLE_GEMINI_MODEL_NAME=<your_google_gemini_model_name_here>

    RAG_DB_PATH=<your_custom_rag_db_path_here>
    HF_TOKEN=<your_hf_token_here>
    MCP_PORT=<your_port_here>

```

3. Install the submodule mcp RAG server

```bash

    git submodule init
    git submodule update

```

4. Start the RAG server package

```bash

    cd rag-server
    uv run rag-mcp-server

```

5. In a separate terminal, activate the virtual environment:

For Windows:

```bash
    source .venv/Scripts/activate
```

For Linux/Mac:
```bash
    source .venv/bin/activate
```

6. Run the agent code in the project root:

```bash
    langgraph dev --port 8080 --allow-blocking
```

## Environment variables

The server and agent use a few environment variables:

- RAG_MCP_SERVER_URL — URL the agent will use to contact the running RAG MCP server (e.g. http://127.0.0.1:8000)
- HF_TOKEN — Hugging Face token used by embedding code if required
- MCP_TRANSPORT, MCP_HOST, MCP_PORT — optional defaults used when launching the MCP server from the command line
- GOOGLE_API_KEY — Google API key for Google Gemini LLM access

You can put these into a .env file in rag-server/src or set them in your shell before starting services.

## RAG MCP server

You can also manually start the RAG MCP server separately in HTTP mode (default) so the agent can connect:

    uv run rag-mcp-server --mode http --host 127.0.0.1 --port 8000 --db-path ./data/rag_database.db

This will:
- create ./data/rag_database.db (directory will be created automatically)
- start the FastMCP server exposing the RAG tools (embed/search/list/delete/get/ask_question)

If you prefer to run in stdio mode for local testing with an MCP client that uses stdio transport, use --mode stdio.

## Common workflows

- Ingest a document:
  - Call embed_document(file_path, metadata) to add a file and create embedding chunks
- Search for context:
  - Call search_documents(query, top_k, min_similarity) to retrieve similar chunks and scores
- Ask a question (recommended):
  - Use ask_question({"question":..., "context_limit":N, "similarity_threshold":X}) to run an end-to-end RAG Q/A and receive an answer with sources
- Manage database:
  - list_documents() — list files
  - get_database_stats() — get counts and database info
  - delete_document(filename) — remove a file's chunks

## Troubleshooting

- If the agent can't connect to the RAG MCP server, check RAG_MCP_SERVER_URL and make sure the server is running and reachable.
- If embedding fails due to missing model keys, set HF_TOKEN or provider-specific credentials.

## Contributing

Feel free to open issues or PRs. Keep changes small and add minimal tests when adding new behavior.

## License

See the top-level project license files (if any).

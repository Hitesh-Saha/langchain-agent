import os
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


def get_Embedder():
    """Create and return a Hugging Face InferenceClient embedder.

    The API key is read from environment variables in this order of preference:
      1. HF_HUB_TOKEN
      2. HF_TOKEN (legacy)

    This allows `--hf-key` from the CLI (which sets HF_HUB_TOKEN)
    to be used here without further wiring.
    """
    token = (
        os.getenv("HF_HUB_TOKEN")
        or os.getenv("HF_TOKEN")
    )

    if not token:
        logger.warning(
            "No Hugging Face API token found in env vars (HUGGINGFACEHUB_API_TOKEN, HF_HUB_TOKEN, HF_TOKEN, RAG_HF_KEY)."
        )

    client = InferenceClient(
        provider="hf-inference",
        api_key=token,
        model="sentence-transformers/all-MiniLM-L6-v2",
    )
    return client
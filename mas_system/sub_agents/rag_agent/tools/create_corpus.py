# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Create a new Vertex AI RAG corpus."""

from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..config import DEFAULT_EMBEDDING_MODEL
from ..utils import sanitize_corpus_name, check_corpus_exists


def create_corpus(corpus_name: str, description: str = None, tool_context: ToolContext = None) -> dict:
    """
    Create a new Vertex AI RAG corpus with the specified name.
    
    Args:
        corpus_name: The name for the new corpus
        description: Optional description for the corpus
        tool_context: The tool context containing state (optional)
        
    Returns:
        A dictionary with:
        - status: "success", "error", or "info"
        - message: Human-readable message about the operation
        - data: Additional information about the created corpus
    """
    try:
        # Sanitize the corpus name
        display_name = sanitize_corpus_name(corpus_name)
        
        # Check if corpus already exists
        if tool_context and check_corpus_exists(display_name, tool_context):
            return {
                "status": "info",
                "message": f"Corpus '{display_name}' already exists. Use it for queries or add new documents.",
                "data": {
                    "corpus_name": display_name,
                    "exists": True
                }
            }
        
        # Configure embedding model
        embedding_model_config = rag.EmbeddingModelConfig(
            publisher_model=f"publishers/google/models/{DEFAULT_EMBEDDING_MODEL}"
        )
        
        # Create the corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            description=description or f"RAG corpus for {display_name}",
            embedding_model_config=embedding_model_config,
        )
        
        # Update state to track corpus existence and set as current
        if tool_context:
            tool_context.state[f"corpus_exists_{display_name}"] = True
            tool_context.state["current_corpus"] = rag_corpus.name
            tool_context.state["current_corpus_display_name"] = display_name
        
        return {
            "status": "success",
            "message": f"Successfully created corpus '{display_name}'. It's now set as the current corpus for queries and document additions.",
            "data": {
                "corpus_name": rag_corpus.name,
                "display_name": display_name,
                "corpus_created": True,
                "embedding_model": DEFAULT_EMBEDDING_MODEL,
                "vector_search_enabled": True
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating corpus: {str(e)}",
            "data": {
                "corpus_name": corpus_name,
                "error_details": str(e)
            }
        }
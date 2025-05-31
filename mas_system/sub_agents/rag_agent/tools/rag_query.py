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

"""Query a Vertex AI RAG corpus with a user question."""

from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..config import DEFAULT_TOP_K, DEFAULT_DISTANCE_THRESHOLD
from ..utils import check_corpus_exists, get_corpus_resource_name


def rag_query(corpus_name: str, query: str, tool_context: ToolContext = None) -> dict:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.
    
    Args:
        corpus_name: The name of the corpus to query (empty string uses current corpus)
        query: The user's question or search query
        tool_context: The tool context containing state
        
    Returns:
        A dictionary with:
        - status: "success" or "error"
        - message: Human-readable message with the answer or error
        - data: Query results including source documents and relevance scores
    """
    try:
        # Use current corpus if corpus_name is empty
        if not corpus_name:
            if tool_context:
                corpus_name = tool_context.state.get("current_corpus_display_name", "")
            if not corpus_name:
                return {
                    "status": "error",
                    "message": "No corpus specified and no current corpus set. Please specify a corpus name or create one first.",
                    "data": {}
                }
        
        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist. Please create it first.",
                "data": {"corpus_name": corpus_name}
            }
        
        # Validate query
        if not query or not query.strip():
            return {
                "status": "error",
                "message": "Please provide a query to search for.",
                "data": {}
            }
        
        # Get corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        
        # Perform the query
        response = rag.retrieval_query(
            text=query,
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            similarity_top_k=DEFAULT_TOP_K,
            vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD,
        )
        
        # Process results
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": ctx_group.source_uri if hasattr(ctx_group, "source_uri") else "",
                    "source_name": ctx_group.source_display_name if hasattr(ctx_group, "source_display_name") else "",
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)
        
        if not results:
            return {
                "status": "success",
                "message": f"No relevant information found for '{query}' in corpus '{corpus_name}'.",
                "data": {
                    "query": query,
                    "corpus_name": corpus_name,
                    "results": [],
                    "results_count": 0
                }
            }
        
        # Build response message with top results
        message_parts = [f"Found {len(results)} relevant result(s) for '{query}' in corpus '{corpus_name}':\n"]
        
        for i, result in enumerate(results[:3]):  # Show top 3 results in message
            message_parts.append(f"\n{i+1}. From {result['source_name'] or 'Unknown source'} (score: {result['score']:.2f}):")
            # Truncate text if too long
            text = result['text']
            if len(text) > 300:
                text = text[:300] + "..."
            message_parts.append(f"   {text}")
        
        if len(results) > 3:
            message_parts.append(f"\n... and {len(results) - 3} more result(s)")
        
        return {
            "status": "success",
            "message": "\n".join(message_parts),
            "data": {
                "query": query,
                "corpus_name": corpus_name,
                "results": results,
                "results_count": len(results),
                "top_k": DEFAULT_TOP_K,
                "distance_threshold": DEFAULT_DISTANCE_THRESHOLD
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error querying corpus: {str(e)}",
            "data": {
                "query": query,
                "corpus_name": corpus_name,
                "error_details": str(e)
            }
        }
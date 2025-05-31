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

"""List all available Vertex AI RAG corpora."""

from google.adk.tools import ToolContext
from vertexai.preview import rag


def list_corpora(tool_context: ToolContext = None) -> dict:
    """
    List all available Vertex AI RAG corpora.
    
    Args:
        tool_context: The tool context containing state (optional)
        
    Returns:
        A dictionary with:
        - status: "success" or "error"
        - message: Human-readable message about the operation
        - data: List of available corpora with their details
    """
    try:
        # List all corpora
        corpora = rag.list_corpora()
        
        # Format corpus information
        corpus_list = []
        for corpus in corpora:
            corpus_info = {
                "resource_name": corpus.name,
                "display_name": corpus.display_name,
                "create_time": str(corpus.create_time) if hasattr(corpus, 'create_time') else "",
                "update_time": str(corpus.update_time) if hasattr(corpus, 'update_time') else "",
            }
            corpus_list.append(corpus_info)
            
            # Update state to track corpus existence
            if corpus.display_name and tool_context:
                tool_context.state[f"corpus_exists_{corpus.display_name}"] = True
        
        # Get current corpus from state
        current_corpus = tool_context.state.get("current_corpus_display_name", "") if tool_context else ""
        
        if not corpus_list:
            return {
                "status": "success",
                "message": "No corpora found. Create a new corpus to get started.",
                "data": {
                    "corpora": [],
                    "count": 0
                }
            }
        
        # Build message with corpus list
        message_parts = [f"Found {len(corpus_list)} corpus(es):"]
        for corpus in corpus_list:
            is_current = " (current)" if corpus["display_name"] == current_corpus else ""
            message_parts.append(f"- {corpus['display_name']}{is_current}")
        
        return {
            "status": "success",
            "message": "\n".join(message_parts),
            "data": {
                "corpora": corpus_list,
                "count": len(corpus_list),
                "current_corpus": current_corpus
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing corpora: {str(e)}",
            "data": {
                "corpora": [],
                "error_details": str(e)
            }
        }
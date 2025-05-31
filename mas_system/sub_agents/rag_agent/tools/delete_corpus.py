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

"""Delete a Vertex AI RAG corpus."""

from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..utils import check_corpus_exists, get_corpus_resource_name


def delete_corpus(corpus_name: str, confirm: bool, tool_context: ToolContext = None) -> dict:
    """
    Delete a Vertex AI RAG corpus when it's no longer needed. Requires confirmation.
    
    Args:
        corpus_name: The name of the corpus to delete
        confirm: Must be True to confirm deletion
        tool_context: The tool context containing state
        
    Returns:
        A dictionary with:
        - status: "success", "error", or "info"
        - message: Human-readable message about the operation
        - data: Details about the deletion
    """
    # Remove initialization of tool_context - can't create without invocation_context
    
    try:
        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist.",
                "data": {"corpus_name": corpus_name}
            }
        
        # Require explicit confirmation
        if not confirm:
            return {
                "status": "info",
                "message": f"Deletion of corpus '{corpus_name}' requires confirmation. Set confirm=True to delete this corpus and all its documents.",
                "data": {
                    "corpus_name": corpus_name,
                    "requires_confirmation": True
                }
            }
        
        # Get corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        
        # Delete the corpus
        rag.delete_corpus(name=corpus_resource_name)
        
        # Update state only if tool_context is available
        if tool_context:
            state_key = f"corpus_exists_{corpus_name}"
            if state_key in tool_context.state:
                tool_context.state[state_key] = False
            
            # Clear current corpus if it was deleted
            if tool_context.state.get("current_corpus_display_name") == corpus_name:
                tool_context.state["current_corpus"] = ""
                tool_context.state["current_corpus_display_name"] = ""
        
        return {
            "status": "success",
            "message": f"Successfully deleted corpus '{corpus_name}' and all its documents.",
            "data": {
                "corpus_name": corpus_name,
                "deleted": True
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting corpus: {str(e)}",
            "data": {
                "corpus_name": corpus_name,
                "error_details": str(e)
            }
        }
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

"""Delete a specific document from a Vertex AI RAG corpus."""

from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..utils import check_corpus_exists, get_corpus_resource_name


def delete_document(corpus_name: str, document_id: str, tool_context: ToolContext = None) -> dict:
    """
    Delete a specific document from a Vertex AI RAG corpus.
    
    Args:
        corpus_name: The name of the corpus containing the document
        document_id: The ID of the document to delete
        tool_context: The tool context containing state
        
    Returns:
        A dictionary with:
        - status: "success" or "error"
        - message: Human-readable message about the operation
        - data: Details about the deletion
    """
    # Initialize tool_context if not provided
    if tool_context is None:
        tool_context = ToolContext()
    
    try:
        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist.",
                "data": {"corpus_name": corpus_name}
            }
        
        # Validate document ID
        if not document_id or not document_id.strip():
            return {
                "status": "error",
                "message": "Please provide a document ID to delete.",
                "data": {}
            }
        
        # Get corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        
        # Construct the full RAG file path
        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        
        # Delete the file
        rag.delete_file(name=rag_file_path)
        
        return {
            "status": "success",
            "message": f"Successfully deleted document '{document_id}' from corpus '{corpus_name}'.",
            "data": {
                "corpus_name": corpus_name,
                "document_id": document_id,
                "deleted": True
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting document: {str(e)}",
            "data": {
                "corpus_name": corpus_name,
                "document_id": document_id,
                "error_details": str(e)
            }
        }
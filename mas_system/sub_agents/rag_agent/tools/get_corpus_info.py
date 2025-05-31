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

"""Get detailed information about a specific RAG corpus."""

from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..utils import check_corpus_exists, get_corpus_resource_name, format_document_info


def get_corpus_info(corpus_name: str, tool_context: ToolContext = None) -> dict:
    """
    Get detailed information about a specific RAG corpus, including its files.
    
    Args:
        corpus_name: The name of the corpus to get info for (empty string uses current corpus)
        tool_context: The tool context containing state
        
    Returns:
        A dictionary with:
        - status: "success" or "error"
        - message: Human-readable message about the corpus
        - data: Detailed corpus information including files
    """
    # Remove initialization of tool_context - can't create without invocation_context
    
    try:
        # Use current corpus if corpus_name is empty
        if not corpus_name:
            if tool_context:
                corpus_name = tool_context.state.get("current_corpus_display_name", "")
            if not corpus_name:
                return {
                    "status": "error",
                    "message": "No corpus specified and no current corpus set. Please specify a corpus name.",
                    "data": {}
                }
        
        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist.",
                "data": {"corpus_name": corpus_name}
            }
        
        # Get corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        
        # List files in the corpus
        files = rag.list_files(corpus_resource_name)
        
        # Format file information
        file_details = []
        for rag_file in files:
            file_info = format_document_info(rag_file)
            file_details.append(file_info)
        
        # Build message
        message_parts = [f"Corpus '{corpus_name}' contains {len(file_details)} file(s):"]
        
        if file_details:
            for i, file_info in enumerate(file_details[:5]):  # Show first 5 files
                message_parts.append(f"{i+1}. {file_info['display_name'] or file_info['file_id']}")
                if file_info['source_uri']:
                    message_parts.append(f"   Source: {file_info['source_uri']}")
            
            if len(file_details) > 5:
                message_parts.append(f"... and {len(file_details) - 5} more file(s)")
        else:
            message_parts.append("No files in this corpus yet. Add documents to get started.")
        
        return {
            "status": "success",
            "message": "\n".join(message_parts),
            "data": {
                "corpus_name": corpus_resource_name,
                "corpus_display_name": corpus_name,
                "file_count": len(file_details),
                "files": file_details
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting corpus info: {str(e)}",
            "data": {
                "corpus_name": corpus_name,
                "error_details": str(e)
            }
        }
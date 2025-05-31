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

"""Utility functions for the RAG agent."""

import re
from typing import Optional
from vertexai.preview import rag
from typing import Optional
from google.adk.tools import ToolContext


def sanitize_corpus_name(name: str) -> str:
    """
    Clean corpus name to meet Vertex AI naming requirements.
    
    Args:
        name: The original corpus name
        
    Returns:
        A sanitized corpus name that meets Vertex AI requirements
    """
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Remove consecutive underscores
    sanitized = re.sub(r"_{2,}", "_", sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_-")
    # Ensure it's not empty and not too long (max 63 chars)
    if not sanitized:
        sanitized = "corpus"
    if len(sanitized) > 63:
        sanitized = sanitized[:63]
    return sanitized


def check_corpus_exists(corpus_name: str, tool_context: Optional[ToolContext] = None) -> bool:
    """
    Check if a corpus exists by checking the state or listing corpora.
    
    Args:
        corpus_name: The name or display name of the corpus
        tool_context: The tool context containing state
        
    Returns:
        True if the corpus exists, False otherwise
    """
    # First check state if tool_context is available
    if tool_context:
        state_key = f"corpus_exists_{corpus_name}"
        if tool_context.state.get(state_key):
            return True
    
    # Otherwise, list corpora to check
    try:
        corpora = rag.list_corpora()
        for corpus in corpora:
            if corpus.display_name == corpus_name or corpus.name == corpus_name:
                # Update state for future reference if tool_context is available
                if tool_context:
                    tool_context.state[f"corpus_exists_{corpus.display_name}"] = True
                return True
    except Exception:
        pass
    
    return False


def get_corpus_resource_name(corpus_name: str) -> Optional[str]:
    """
    Get the full resource name of a corpus from its display name.
    
    Args:
        corpus_name: The display name or full resource name of the corpus
        
    Returns:
        The full resource name if found, otherwise the original name
    """
    # If it already looks like a full resource name, return it
    if corpus_name.startswith("projects/"):
        return corpus_name
    
    # Otherwise, try to find it by display name
    try:
        corpora = rag.list_corpora()
        for corpus in corpora:
            if corpus.display_name == corpus_name:
                return corpus.name
    except Exception:
        pass
    
    # If not found, return the original name
    return corpus_name


def format_document_info(rag_file) -> dict:
    """
    Format RAG file information into a consistent dictionary.
    
    Args:
        rag_file: A RAG file object from Vertex AI
        
    Returns:
        A dictionary with formatted file information
    """
    file_id = rag_file.name.split("/")[-1] if hasattr(rag_file, 'name') else ""
    
    # Determine source URI
    source_uri = ""
    if hasattr(rag_file, 'gcs_uri') and rag_file.gcs_uri and hasattr(rag_file.gcs_uri, 'uris') and rag_file.gcs_uri.uris:
        source_uri = rag_file.gcs_uri.uris[0]
    elif hasattr(rag_file, 'drive_uri') and rag_file.drive_uri:
        if hasattr(rag_file.drive_uri, 'resource_id'):
            source_uri = f"drive://{rag_file.drive_uri.resource_id}"
        elif hasattr(rag_file.drive_uri, 'uris') and rag_file.drive_uri.uris:
            source_uri = rag_file.drive_uri.uris[0]
    
    return {
        "file_id": file_id,
        "display_name": rag_file.display_name if hasattr(rag_file, 'display_name') else "",
        "source_uri": source_uri,
        "create_time": str(rag_file.create_time) if hasattr(rag_file, 'create_time') else "",
        "update_time": str(rag_file.update_time) if hasattr(rag_file, 'update_time') else "",
    }


def convert_docs_url_to_drive(url: str) -> tuple[str, bool]:
    """
    Convert Google Docs/Sheets/Slides URLs to Drive format.
    
    Args:
        url: The original URL
        
    Returns:
        A tuple of (converted_url, was_converted)
    """
    docs_match = re.match(
        r"https://docs\.google\.com/(?:document|spreadsheets|presentation)/d/([^/]+)/.*", 
        url
    )
    
    if docs_match:
        file_id = docs_match.group(1)
        drive_url = f"https://drive.google.com/file/d/{file_id}/view"
        return drive_url, True
    
    return url, False
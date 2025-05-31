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

"""Add new data sources to a Vertex AI RAG corpus."""

from typing import List
from google.adk.tools import ToolContext
from vertexai.preview import rag
from ..utils import check_corpus_exists, get_corpus_resource_name, convert_docs_url_to_drive


def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext = None) -> dict:
    """
    Add new data sources to a Vertex AI RAG corpus.
    
    Args:
        corpus_name: The name of the corpus to add data to (empty string uses current corpus)
        paths: List of paths to add (local file paths or GCS paths)
        tool_context: The tool context containing state (optional)
        
    Supported formats:
        - Local file paths: /path/to/file.pdf
        - GCS: gs://bucket/path/to/file
        
    Note: Direct Google Drive URLs are not supported by the upload_file API.
    To use Google Drive files, download them first or use GCS.
        
    Returns:
        A dictionary with:
        - status: "success", "error", or "info" 
        - message: Human-readable message about the operation
        - data: Details about the added files
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
        
        # Validate inputs
        if not paths or not isinstance(paths, list):
            return {
                "status": "error",
                "message": "Please provide a list of paths to add.",
                "data": {}
            }
        
        # Process and validate paths
        validated_paths = []
        invalid_paths = []
        conversions = []
        
        for path in paths:
            if not isinstance(path, str):
                invalid_paths.append({"path": str(path), "reason": "Path must be a string"})
                continue
            
            # Convert Google Docs/Sheets/Slides URLs to Drive format
            converted_path, was_converted = convert_docs_url_to_drive(path)
            if was_converted:
                conversions.append({"original": path, "converted": converted_path})
                # Note: Drive URLs still can't be directly uploaded
                invalid_paths.append({
                    "path": path,
                    "reason": "Direct Google Drive upload not supported. Please download the file and upload from local path or use GCS."
                })
            elif path.startswith("https://drive.google.com/"):
                invalid_paths.append({
                    "path": path,
                    "reason": "Direct Google Drive upload not supported. Please download the file and upload from local path or use GCS."
                })
            elif path.startswith("gs://") or path.startswith("/") or path.startswith("./"):
                # GCS paths or local file paths
                validated_paths.append(path)
            else:
                invalid_paths.append({
                    "path": path, 
                    "reason": "Invalid format. Use local file paths or GCS paths (gs://)"
                })
        
        if not validated_paths:
            return {
                "status": "error",
                "message": "No valid paths to add. Please provide local file paths or GCS paths.",
                "data": {"invalid_paths": invalid_paths}
            }
        
        # Get corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        
        # Upload files to the corpus
        uploaded_files = []
        failed_paths = []
        
        for path in validated_paths:
            try:
                # Upload the file
                rag_file = rag.upload_file(
                    corpus_name=corpus_resource_name,
                    path=path,
                    display_name=path.split('/')[-1],  # Use filename as display name
                    description=f"Uploaded from {path}"
                )
                uploaded_files.append(rag_file)
                
            except Exception as e:
                failed_paths.append({
                    "path": path,
                    "reason": str(e)
                })
        
        # Calculate total files added
        files_added = len(uploaded_files)
        
        # Set this as the current corpus if not already set
        if tool_context and not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_resource_name
            tool_context.state["current_corpus_display_name"] = corpus_name
        
        # Build response
        if files_added == 0 and not failed_paths:
            return {
                "status": "error",
                "message": "No files were added. Please check your paths.",
                "data": {
                    "corpus_name": corpus_name,
                    "invalid_paths": invalid_paths
                }
            }
        
        message_parts = []
        if files_added > 0:
            message_parts.append(f"Successfully added {files_added} file(s) to corpus '{corpus_name}'.")
        if failed_paths:
            message_parts.append(f"Failed to add {len(failed_paths)} file(s).")
        if conversions:
            message_parts.append("Note: Google Drive URLs are not supported for direct upload.")
        if invalid_paths:
            message_parts.append(f"Skipped {len(invalid_paths)} invalid path(s).")
        
        return {
            "status": "success" if files_added > 0 else "error",
            "message": " ".join(message_parts),
            "data": {
                "corpus_name": corpus_name,
                "files_added": files_added,
                "paths": validated_paths,
                "invalid_paths": invalid_paths,
                "failed_paths": failed_paths,
                "conversions": conversions,
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding data to corpus: {str(e)}",
            "data": {
                "corpus_name": corpus_name,
                "error_details": str(e)
            }
        }
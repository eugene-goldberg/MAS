"""
Google Cloud Function for reactive RAG document ingestion.
Triggered by file uploads to Cloud Storage bucket.
"""

import functions_framework
from google.cloud import storage
from google.cloud import aiplatform
import vertexai
from vertexai.preview import rag
import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import traceback

# Configure logging
logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.html': 'text/html',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc': 'application/msword',
    '.json': 'application/json',
    '.csv': 'text/csv'
}

# Configuration from environment
PROJECT_ID = os.environ.get('GCP_PROJECT', '')
LOCATION = os.environ.get('GCP_LOCATION', 'us-central1')
CORPUS_NAME = os.environ.get('RAG_CORPUS_NAME', 'mas-rag-corpus')
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '512'))
CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '100'))


@functions_framework.cloud_event
def process_rag_upload(cloud_event):
    """
    Cloud Function triggered by Cloud Storage file upload.
    Processes the file and ingests it into Vertex AI RAG.
    """
    data = cloud_event.data
    
    # Extract file information
    bucket_name = data["bucket"]
    file_name = data["name"]
    
    # Skip if file is in processed or failed folder
    if file_name.startswith(('processed/', 'failed/')):
        logger.info(f"Skipping file in {file_name.split('/')[0]} folder")
        return {"status": "skipped", "reason": "File in processed/failed folder"}
    
    logger.info(f"Processing file: gs://{bucket_name}/{file_name}")
    
    try:
        # Validate file type
        if not validate_file_type(file_name):
            raise ValueError(f"Unsupported file type: {file_name}")
        
        # Extract metadata
        metadata = extract_metadata(bucket_name, file_name)
        logger.info(f"File metadata: {json.dumps(metadata)}")
        
        # Ingest to RAG
        result = ingest_to_rag(bucket_name, file_name, metadata)
        
        # Move to processed folder
        move_to_processed(bucket_name, file_name)
        
        logger.info(f"Successfully processed {file_name}")
        return result
        
    except Exception as e:
        error_msg = f"Error processing {file_name}: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        
        # Handle error
        handle_error(bucket_name, file_name, error_msg)
        
        # Return error response
        return {
            "status": "error",
            "file": file_name,
            "error": str(e)
        }


def validate_file_type(file_name: str) -> bool:
    """Validate if file type is supported."""
    _, ext = os.path.splitext(file_name.lower())
    return ext in SUPPORTED_EXTENSIONS


def extract_metadata(bucket_name: str, file_name: str) -> Dict:
    """Extract metadata from file for RAG context."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # Reload to get latest metadata
    blob.reload()
    
    metadata = {
        "original_name": file_name,
        "size": blob.size,
        "content_type": blob.content_type,
        "created": blob.time_created.isoformat() if blob.time_created else None,
        "md5_hash": blob.md5_hash,
        "custom_metadata": blob.metadata or {},
        "gcs_uri": f"gs://{bucket_name}/{file_name}"
    }
    
    return metadata


def get_or_create_corpus(corpus_display_name: str) -> Tuple[str, bool]:
    """
    Get existing corpus or create new one.
    Returns (corpus_name, created_new).
    """
    try:
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # List existing corpora
        corpora = rag.list_corpora()
        
        # Check if corpus exists
        for corpus in corpora:
            if corpus.display_name == corpus_display_name:
                logger.info(f"Found existing corpus: {corpus.name}")
                return corpus.name, False
        
        # Create new corpus if not found
        logger.info(f"Creating new corpus: {corpus_display_name}")
        
        try:
            # Try the working API format
            embedding_model_config = rag.EmbeddingModelConfig(
                publisher_model="publishers/google/models/text-embedding-005"
            )
            
            corpus = rag.create_corpus(
                display_name=corpus_display_name,
                description="MAS RAG corpus for document storage (auto-created by Cloud Function)",
                embedding_model_config=embedding_model_config
            )
        except AttributeError:
            # Fallback to simpler API if needed
            logger.warning("Using fallback corpus creation method")
            corpus = rag.create_corpus(
                display_name=corpus_display_name,
                description="MAS RAG corpus for document storage (auto-created by Cloud Function)"
            )
        
        logger.info(f"Created new corpus: {corpus.name}")
        return corpus.name, True
        
    except Exception as e:
        logger.error(f"Error managing corpus: {str(e)}")
        raise


def ingest_to_rag(bucket_name: str, file_name: str, metadata: Dict) -> Dict:
    """Ingest file into Vertex AI RAG."""
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Get or create corpus
    corpus_name, created_new = get_or_create_corpus(CORPUS_NAME)
    
    # Create GCS URI
    gcs_uri = f"gs://{bucket_name}/{file_name}"
    
    # Import file to RAG
    logger.info(f"Importing {file_name} to corpus {corpus_name}")
    
    response = rag.import_files(
        corpus_name=corpus_name,
        paths=[gcs_uri],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    # Log operation name for tracking
    logger.info(f"Import operation started: {response.operation_name if hasattr(response, 'operation_name') else 'Success'}")
    
    # Create success response
    result = {
        "status": "success",
        "file": file_name,
        "corpus": corpus_name,
        "corpus_created": created_new,
        "operation": str(response) if response else "completed",
        "metadata": metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return result


def move_to_processed(bucket_name: str, file_name: str):
    """Move successfully processed file to processed folder."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    source_blob = bucket.blob(file_name)
    destination_name = f"processed/{file_name}"
    
    # Copy to processed folder
    destination_blob = bucket.blob(destination_name)
    destination_blob.upload_from_string(
        source_blob.download_as_bytes(),
        content_type=source_blob.content_type
    )
    
    # Copy metadata
    if source_blob.metadata:
        destination_blob.metadata = source_blob.metadata
        destination_blob.metadata['original_upload_time'] = datetime.utcnow().isoformat()
        destination_blob.metadata['processing_status'] = 'success'
        destination_blob.patch()
    
    # Delete original
    source_blob.delete()
    
    logger.info(f"Moved {file_name} to processed folder")


def handle_error(bucket_name: str, file_name: str, error: str):
    """Handle processing errors by moving file and creating error log."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Move to failed folder
        source_blob = bucket.blob(file_name)
        destination_name = f"failed/{file_name}"
        
        if source_blob.exists():
            destination_blob = bucket.blob(destination_name)
            destination_blob.upload_from_string(
                source_blob.download_as_bytes(),
                content_type=source_blob.content_type
            )
            source_blob.delete()
        
        # Create error log file
        error_data = {
            "file": file_name,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "function_version": os.environ.get('K_REVISION', 'unknown')
        }
        
        error_blob = bucket.blob(f"failed/{file_name}.error.json")
        error_blob.upload_from_string(
            json.dumps(error_data, indent=2),
            content_type='application/json'
        )
        
        logger.error(f"Moved {file_name} to failed folder with error log")
        
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")


# Health check endpoint for monitoring
@functions_framework.http
def health_check(request):
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "project": PROJECT_ID,
        "location": LOCATION,
        "corpus": CORPUS_NAME,
        "version": os.environ.get('K_REVISION', 'unknown')
    }, 200
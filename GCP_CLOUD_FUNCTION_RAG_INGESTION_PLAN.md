# GCP Cloud Function for Reactive RAG Ingestion Plan

## Overview
Create a Google Cloud Function that automatically ingests documents into Vertex AI RAG when files are uploaded to a Cloud Storage bucket. This enables real-time document processing for the MAS RAG agent.

## Architecture

### Components
1. **Cloud Storage Bucket** - Trigger source for document uploads
2. **Cloud Function** - Serverless function for RAG ingestion
3. **Vertex AI RAG API** - Document processing and storage
4. **Pub/Sub (Optional)** - For async processing and error handling

### Data Flow
```
User uploads file → GCS Bucket → Triggers Cloud Function → Processes file → Adds to RAG Corpus
                                                         ↓
                                                    Error → Pub/Sub → Error Handler
```

## Implementation Plan

### Phase 1: Infrastructure Setup

#### 1.1 Cloud Storage Setup
- Create dedicated GCS bucket for RAG document uploads
- Configure bucket lifecycle policies
- Set up folder structure:
  ```
  gs://mas-rag-documents/
  ├── pending/      # Files awaiting processing
  ├── processed/    # Successfully processed files
  └── failed/       # Failed processing attempts
  ```

#### 1.2 IAM Permissions
- Cloud Function service account needs:
  - `storage.objectViewer` on source bucket
  - `storage.objectAdmin` for moving files
  - `aiplatform.user` for Vertex AI RAG
  - `logging.logWriter` for logging

#### 1.3 Vertex AI RAG Setup
- Ensure RAG corpus exists or create logic to create one
- Configure embedding model (text-embedding-005)
- Set up vector search index

### Phase 2: Cloud Function Development

#### 2.1 Function Structure
```python
# main.py
import functions_framework
from google.cloud import storage
from google.cloud import aiplatform
import vertexai
from vertexai.preview import rag
import logging
import os
import json
from datetime import datetime

@functions_framework.cloud_event
def process_rag_upload(cloud_event):
    """Triggered by Cloud Storage when file is uploaded."""
    data = cloud_event.data
    
    # Extract file information
    bucket_name = data["bucket"]
    file_name = data["name"]
    
    # Process the file
    try:
        result = ingest_to_rag(bucket_name, file_name)
        move_to_processed(bucket_name, file_name)
        return result
    except Exception as e:
        handle_error(bucket_name, file_name, str(e))
        raise
```

#### 2.2 Core Functions

```python
def ingest_to_rag(bucket_name: str, file_name: str) -> dict:
    """Ingest file into Vertex AI RAG."""
    # Initialize Vertex AI
    project_id = os.environ.get('GCP_PROJECT')
    location = os.environ.get('GCP_LOCATION', 'us-central1')
    corpus_name = os.environ.get('RAG_CORPUS_NAME', 'mas-rag-corpus')
    
    vertexai.init(project=project_id, location=location)
    
    # Get or create corpus
    corpus = get_or_create_corpus(corpus_name)
    
    # Create GCS URI
    gcs_uri = f"gs://{bucket_name}/{file_name}"
    
    # Import file to RAG
    import_request = rag.ImportRagFilesRequest(
        corpus=corpus,
        import_rag_files_config=rag.ImportRagFilesConfig(
            gcs_source=rag.GcsSource(uris=[gcs_uri]),
            chunk_size=512,
            chunk_overlap=100
        )
    )
    
    response = rag.RagDataService.import_rag_files(request=import_request)
    
    # Log success
    logging.info(f"Successfully ingested {file_name} to corpus {corpus_name}")
    
    return {
        "status": "success",
        "file": file_name,
        "corpus": corpus_name,
        "operation": response.name
    }

def get_or_create_corpus(corpus_name: str) -> str:
    """Get existing corpus or create new one."""
    try:
        # List existing corpora
        corpora = rag.RagDataService.list_rag_corpora()
        
        for corpus in corpora:
            if corpus.display_name == corpus_name:
                return corpus.name
        
        # Create new corpus if not found
        embedding_model_config = rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        )
        
        corpus = rag.RagDataService.create_rag_corpus(
            display_name=corpus_name,
            description="MAS RAG corpus for document storage",
            embedding_model_config=embedding_model_config
        )
        
        return corpus.name
        
    except Exception as e:
        logging.error(f"Error managing corpus: {str(e)}")
        raise

def move_to_processed(bucket_name: str, file_name: str):
    """Move successfully processed file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    source_blob = bucket.blob(file_name)
    destination_name = f"processed/{file_name}"
    
    # Copy to processed folder
    bucket.copy_blob(source_blob, bucket, destination_name)
    
    # Delete original
    source_blob.delete()
    
    logging.info(f"Moved {file_name} to processed folder")

def handle_error(bucket_name: str, file_name: str, error: str):
    """Handle processing errors."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Move to failed folder
    source_blob = bucket.blob(file_name)
    destination_name = f"failed/{file_name}"
    
    bucket.copy_blob(source_blob, bucket, destination_name)
    source_blob.delete()
    
    # Create error log file
    error_data = {
        "file": file_name,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    error_blob = bucket.blob(f"failed/{file_name}.error.json")
    error_blob.upload_from_string(json.dumps(error_data))
    
    logging.error(f"Failed to process {file_name}: {error}")
```

#### 2.3 Requirements File
```txt
# requirements.txt
functions-framework==3.*
google-cloud-storage==2.*
google-cloud-aiplatform==1.*
vertexai==1.*
```

#### 2.4 Environment Variables
```yaml
# .env.yaml
GCP_PROJECT: "your-project-id"
GCP_LOCATION: "us-central1"
RAG_CORPUS_NAME: "mas-rag-corpus"
LOG_LEVEL: "INFO"
```

### Phase 3: Advanced Features

#### 3.1 File Type Support
```python
SUPPORTED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.html': 'text/html',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

def validate_file_type(file_name: str) -> bool:
    """Validate if file type is supported."""
    _, ext = os.path.splitext(file_name.lower())
    return ext in SUPPORTED_EXTENSIONS
```

#### 3.2 Metadata Extraction
```python
def extract_metadata(bucket_name: str, file_name: str) -> dict:
    """Extract metadata from file for RAG context."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    metadata = {
        "original_name": file_name,
        "size": blob.size,
        "content_type": blob.content_type,
        "created": blob.time_created.isoformat(),
        "md5_hash": blob.md5_hash,
        "custom_metadata": blob.metadata or {}
    }
    
    return metadata
```

#### 3.3 Batch Processing
```python
def process_batch_upload(cloud_event):
    """Handle multiple file uploads efficiently."""
    # Implementation for processing multiple files
    # Use async operations for better performance
    pass
```

### Phase 4: Deployment

#### 4.1 Deploy Command
```bash
gcloud functions deploy rag-ingestion-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_rag_upload \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=mas-rag-documents" \
  --env-vars-file=.env.yaml \
  --service-account=rag-function-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

#### 4.2 Testing Script
```python
# test_function.py
from google.cloud import storage
import time

def test_rag_ingestion():
    """Test the Cloud Function by uploading a test file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket('mas-rag-documents')
    
    # Upload test file
    test_content = "This is a test document for RAG ingestion."
    blob = bucket.blob('test_document.txt')
    blob.upload_from_string(test_content)
    
    print("Test file uploaded. Check logs for processing status.")
    
    # Wait and check if moved to processed
    time.sleep(10)
    
    processed_blob = bucket.blob('processed/test_document.txt')
    if processed_blob.exists():
        print("✓ File successfully processed!")
    else:
        print("✗ File processing failed. Check failed folder.")
```

### Phase 5: Monitoring and Observability

#### 5.1 Logging
- Structured logging for all operations
- Log levels: INFO for success, ERROR for failures
- Include trace IDs for debugging

#### 5.2 Metrics
- Processing time per file
- Success/failure rates
- File size distribution
- Corpus growth over time

#### 5.3 Alerts
- Failed ingestion alerts
- High error rate alerts
- Storage quota alerts

### Phase 6: Integration with MAS

#### 6.1 Update RAG Agent
- Ensure RAG agent uses same corpus name
- Add function to check ingestion status

#### 6.2 User Interface
- Create simple UI for file upload
- Display processing status
- Show corpus statistics

## Error Handling

### Common Errors and Solutions
1. **File Too Large**: Split into chunks or increase function memory
2. **Unsupported Format**: Return clear error message
3. **Corpus Not Found**: Auto-create corpus
4. **Rate Limiting**: Implement exponential backoff
5. **Network Timeout**: Retry with larger timeout

## Security Considerations

1. **File Validation**
   - Virus scanning
   - File size limits
   - Content type verification

2. **Access Control**
   - Least privilege IAM
   - VPC Service Controls
   - Audit logging

3. **Data Privacy**
   - Encryption at rest
   - Encryption in transit
   - PII detection (optional)

## Cost Optimization

1. **Function Configuration**
   - Appropriate memory allocation
   - Concurrent execution limits
   - Timeout settings

2. **Storage Management**
   - Lifecycle policies for processed files
   - Compression for archives
   - Regional storage for cost savings

## Testing Strategy

### Unit Tests
- File validation logic
- Metadata extraction
- Error handling

### Integration Tests
- End-to-end file processing
- RAG corpus operations
- Error scenarios

### Load Tests
- Bulk file uploads
- Concurrent processing
- Rate limit testing

## Rollout Plan

1. **Week 1**: Infrastructure setup and basic function
2. **Week 2**: Core RAG integration and testing
3. **Week 3**: Advanced features and error handling
4. **Week 4**: Monitoring, alerts, and optimization
5. **Week 5**: Integration with MAS and final testing

## Success Metrics

1. **Performance**
   - < 30s processing time for average document
   - > 95% success rate
   - < 1% duplicate processing

2. **Reliability**
   - 99.9% uptime
   - Automatic retry for transient failures
   - Clear error reporting

3. **Scalability**
   - Handle 1000+ documents/day
   - Auto-scale with load
   - No manual intervention required

## Next Steps

1. Review and approve plan
2. Set up GCP project and permissions
3. Create development environment
4. Begin Phase 1 implementation
5. Schedule regular check-ins
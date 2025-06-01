# RAG Ingestion Cloud Function

Automatically ingests documents into Vertex AI RAG when files are uploaded to a Google Cloud Storage bucket.

## Features

- **Automatic Triggering**: Processes files immediately upon upload to GCS
- **Multiple File Formats**: Supports PDF, TXT, MD, HTML, DOCX, JSON, CSV
- **Error Handling**: Moves failed files to a separate folder with error logs
- **Corpus Management**: Auto-creates RAG corpus if it doesn't exist
- **Metadata Tracking**: Preserves file metadata throughout processing
- **Scalable**: Handles concurrent uploads with configurable limits

## Architecture

```
User uploads file → GCS Bucket → Triggers Cloud Function → Vertex AI RAG
                                            ↓
                                    Success → processed/
                                    Failure → failed/ + error.json
```

## Setup Instructions

### 1. Prerequisites

- Google Cloud Project with billing enabled
- gcloud CLI installed and configured
- Appropriate IAM permissions

### 2. Configure Environment

1. Copy the environment template:
   ```bash
   cp .env.yaml .env.yaml.local
   ```

2. Edit `.env.yaml.local` with your project details:
   ```yaml
   GCP_PROJECT: "your-project-id"
   GCP_LOCATION: "us-central1"
   RAG_CORPUS_NAME: "mas-rag-corpus"
   ```

### 3. Set Up Infrastructure

Run the setup script to create necessary GCP resources:

```bash
./scripts/setup_infrastructure.sh [dev|prod]
```

This creates:
- Cloud Storage bucket with folder structure
- Service account with required permissions
- Enables necessary APIs

### 4. Deploy the Function

Deploy to Google Cloud Functions:

```bash
./scripts/deploy.sh [dev|prod]
```

### 5. Test the Deployment

Test the function with a sample file:

```bash
./scripts/test_function.sh [dev|prod] [test_file.txt]
```

## File Processing Flow

1. **Upload Detection**: Function triggered by file upload to bucket
2. **Validation**: Checks if file type is supported
3. **Metadata Extraction**: Captures file information
4. **RAG Ingestion**: Adds document to Vertex AI corpus
5. **File Movement**: 
   - Success → `processed/` folder
   - Failure → `failed/` folder with error log

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT` | Google Cloud Project ID | Required |
| `GCP_LOCATION` | Deployment region | us-central1 |
| `RAG_CORPUS_NAME` | Name of RAG corpus | mas-rag-corpus |
| `CHUNK_SIZE` | Document chunk size | 512 |
| `CHUNK_OVERLAP` | Chunk overlap size | 100 |
| `LOG_LEVEL` | Logging verbosity | INFO |

## Monitoring

### View Function Logs

```bash
gcloud functions logs read rag-ingestion-function-dev \
  --region=us-central1 \
  --limit=50
```

### Check Processing Status

```bash
# List processed files
gsutil ls gs://mas-rag-documents-dev/processed/

# List failed files
gsutil ls gs://mas-rag-documents-dev/failed/

# View error details
gsutil cat gs://mas-rag-documents-dev/failed/[filename].error.json
```

## Testing

### Unit Tests

```bash
cd cloud_functions/rag_ingestion
python -m pytest tests/test_main.py -v
```

### Integration Tests

```bash
python tests/integration_test.py
```

## Troubleshooting

### Common Issues

1. **Function not triggering**
   - Check Eventarc permissions
   - Verify bucket event configuration
   - Check function deployment status

2. **Permission errors**
   - Verify service account has all required roles
   - Check Vertex AI API is enabled
   - Ensure corpus permissions are correct

3. **Processing failures**
   - Check file format is supported
   - Verify file size is within limits
   - Review error logs in failed/ folder

### Debug Commands

```bash
# Check function status
gcloud functions describe rag-ingestion-function-dev --region=us-central1

# Test IAM permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --filter="bindings.members:serviceAccount:rag-function-sa-dev*"

# Verify APIs enabled
gcloud services list --enabled --filter="name:aiplatform"
```

## Security Considerations

- Files are validated before processing
- Service account follows least-privilege principle
- All data encrypted in transit and at rest
- Audit logging enabled for compliance

## Cost Optimization

- Function memory: 512MB (adjust based on file sizes)
- Timeout: 9 minutes (sufficient for most documents)
- Max instances: 10 (prevents runaway costs)
- Consider lifecycle policies for processed files

## Integration with MAS

The processed documents are automatically available to the MAS RAG agent:

```python
# In MAS, the RAG agent can query ingested documents
response = rag_agent.send("search for information about cloud functions")
```

## Next Steps

1. Set up monitoring alerts for failures
2. Implement file size limits
3. Add support for batch processing
4. Create dashboard for ingestion metrics
5. Implement PII detection (optional)
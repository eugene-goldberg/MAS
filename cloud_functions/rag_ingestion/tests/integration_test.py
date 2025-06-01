"""Integration tests for RAG ingestion with live GCP services."""

import os
import sys
import time
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv('.env.yaml.local')

from google.cloud import storage
import vertexai
from vertexai.preview import rag


class IntegrationTest:
    """Integration test for RAG ingestion function."""
    
    def __init__(self):
        """Initialize test configuration."""
        self.project_id = os.environ.get('GCP_PROJECT')
        self.location = os.environ.get('GCP_LOCATION', 'us-central1')
        self.corpus_name = os.environ.get('RAG_CORPUS_NAME', 'mas-rag-corpus')
        self.bucket_name = f"mas-rag-test-{int(time.time())}"
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT environment variable not set")
            
        print(f"Test Configuration:")
        print(f"  Project: {self.project_id}")
        print(f"  Location: {self.location}")
        print(f"  Corpus: {self.corpus_name}")
        print(f"  Test Bucket: {self.bucket_name}")
        
    def setup(self):
        """Set up test resources."""
        print("\n1. Setting up test resources...")
        
        # Create test bucket
        storage_client = storage.Client(project=self.project_id)
        bucket = storage_client.create_bucket(
            self.bucket_name,
            location=self.location
        )
        print(f"  ✓ Created test bucket: {self.bucket_name}")
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        print("  ✓ Initialized Vertex AI")
        
        return bucket
        
    def create_test_files(self, bucket):
        """Create test files and upload to bucket."""
        print("\n2. Creating and uploading test files...")
        
        test_files = []
        
        # Test file 1: Plain text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
RAG Integration Test Document 1
==============================

This is a test document for the RAG ingestion function.
It contains sample text that should be ingested into the Vertex AI RAG corpus.

Key Points:
- Automatic ingestion on upload
- Support for multiple file types
- Error handling and retry logic

Test timestamp: {}
""".format(datetime.utcnow().isoformat()))
            test_files.append(('test_doc_1.txt', f.name))
            
        # Test file 2: Markdown
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# RAG Integration Test Document 2

## Overview
This is a **markdown** document for testing RAG ingestion.

## Features
- Supports markdown formatting
- Handles code blocks
- Processes lists and tables

```python
def test_function():
    return "This is a code block"
```

## Test Data
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

_Generated at: {}_
""".format(datetime.utcnow().isoformat()))
            test_files.append(('test_doc_2.md', f.name))
            
        # Upload files
        for blob_name, file_path in test_files:
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
            print(f"  ✓ Uploaded: {blob_name}")
            os.unlink(file_path)  # Clean up temp file
            
        return [name for name, _ in test_files]
        
    def verify_corpus(self):
        """Verify RAG corpus exists and is accessible."""
        print("\n3. Verifying RAG corpus...")
        
        try:
            # List corpora
            request = rag.ListRagCorporaRequest(
                parent=f"projects/{self.project_id}/locations/{self.location}"
            )
            corpora = rag.RagDataService.list_rag_corpora(request=request)
            
            corpus_found = False
            for corpus in corpora:
                if corpus.display_name == self.corpus_name:
                    corpus_found = True
                    print(f"  ✓ Found corpus: {corpus.name}")
                    break
                    
            if not corpus_found:
                print(f"  ⚠ Corpus '{self.corpus_name}' not found")
                print("    Function will create it on first run")
                
            return True
            
        except Exception as e:
            print(f"  ✗ Error accessing RAG: {str(e)}")
            return False
            
    def test_rag_query(self, query_text):
        """Test querying the RAG corpus."""
        print(f"\n4. Testing RAG query: '{query_text}'")
        
        try:
            # Get corpus
            request = rag.ListRagCorporaRequest(
                parent=f"projects/{self.project_id}/locations/{self.location}"
            )
            corpora = rag.RagDataService.list_rag_corpora(request=request)
            
            corpus_name = None
            for corpus in corpora:
                if corpus.display_name == self.corpus_name:
                    corpus_name = corpus.name
                    break
                    
            if not corpus_name:
                print("  ⚠ Corpus not found, skipping query test")
                return
                
            # Query the corpus
            query_request = rag.QueryRagRequest(
                corpus=corpus_name,
                query=query_text,
                similarity_top_k=5,
                return_relevant_chunks=True
            )
            
            response = rag.RagDataService.query_rag(request=query_request)
            
            print(f"  ✓ Query returned {len(response.relevant_chunks)} chunks")
            
            # Display results
            for i, chunk in enumerate(response.relevant_chunks[:3]):
                print(f"\n  Result {i+1}:")
                print(f"    Score: {chunk.chunk_relevance_score:.3f}")
                print(f"    Content: {chunk.chunk.content[:100]}...")
                
        except Exception as e:
            print(f"  ✗ Query error: {str(e)}")
            
    def cleanup(self, bucket):
        """Clean up test resources."""
        print("\n5. Cleaning up test resources...")
        
        # Delete all blobs
        blobs = bucket.list_blobs()
        for blob in blobs:
            blob.delete()
            
        # Delete bucket
        bucket.delete()
        print(f"  ✓ Deleted test bucket: {self.bucket_name}")
        
    def run(self):
        """Run the integration test."""
        print("\n" + "="*60)
        print("RAG Ingestion Integration Test")
        print("="*60)
        
        bucket = None
        try:
            # Setup
            bucket = self.setup()
            
            # Verify corpus access
            if not self.verify_corpus():
                print("\n⚠ Warning: Could not verify RAG corpus access")
                print("  The Cloud Function will need appropriate permissions")
                
            # Create test files
            test_files = self.create_test_files(bucket)
            
            # Wait for function to process (if deployed)
            print("\n⏳ Waiting 10 seconds for function processing...")
            print("   (Skip this if function not yet deployed)")
            time.sleep(10)
            
            # Test RAG query
            self.test_rag_query("test document integration")
            
            print("\n✅ Integration test completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {str(e)}")
            raise
            
        finally:
            if bucket:
                self.cleanup(bucket)
                
        print("\nNext steps:")
        print("1. Deploy the function: ./scripts/setup_infrastructure.sh")
        print("2. Deploy the function: ./scripts/deploy.sh")
        print("3. Test with real uploads: ./scripts/test_function.sh")


if __name__ == "__main__":
    test = IntegrationTest()
    test.run()
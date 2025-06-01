"""Unit tests for RAG ingestion Cloud Function."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the google modules before importing main
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.storage'] = MagicMock()
sys.modules['google.cloud.aiplatform'] = MagicMock()
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.preview'] = MagicMock()
sys.modules['vertexai.preview.rag'] = MagicMock()

import main


class TestRAGIngestion(unittest.TestCase):
    """Test cases for RAG ingestion function."""
    
    def setUp(self):
        """Set up test environment."""
        os.environ['GCP_PROJECT'] = 'test-project'
        os.environ['GCP_LOCATION'] = 'us-central1'
        os.environ['RAG_CORPUS_NAME'] = 'test-corpus'
        
    def test_validate_file_type(self):
        """Test file type validation."""
        # Valid file types
        self.assertTrue(main.validate_file_type('document.pdf'))
        self.assertTrue(main.validate_file_type('text.txt'))
        self.assertTrue(main.validate_file_type('README.md'))
        self.assertTrue(main.validate_file_type('page.html'))
        
        # Invalid file types
        self.assertFalse(main.validate_file_type('image.png'))
        self.assertFalse(main.validate_file_type('video.mp4'))
        self.assertFalse(main.validate_file_type('script.exe'))
        
    @patch('main.storage.Client')
    def test_extract_metadata(self, mock_storage):
        """Test metadata extraction."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.size = 1024
        mock_blob.content_type = 'text/plain'
        mock_blob.time_created = datetime.utcnow()
        mock_blob.md5_hash = 'abc123'
        mock_blob.metadata = {'custom': 'value'}
        
        # Mock bucket and client
        mock_bucket = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_client = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        
        # Test metadata extraction
        metadata = main.extract_metadata('test-bucket', 'test.txt')
        
        self.assertEqual(metadata['original_name'], 'test.txt')
        self.assertEqual(metadata['size'], 1024)
        self.assertEqual(metadata['content_type'], 'text/plain')
        self.assertEqual(metadata['gcs_uri'], 'gs://test-bucket/test.txt')
        self.assertIn('custom', metadata['custom_metadata'])
        
    @patch('main.process_rag_upload')
    def test_skip_processed_files(self, mock_process):
        """Test that files in processed/failed folders are skipped."""
        # Create mock cloud event
        cloud_event = Mock()
        
        # Test processed folder
        cloud_event.data = {
            'bucket': 'test-bucket',
            'name': 'processed/file.txt'
        }
        result = main.process_rag_upload(cloud_event)
        self.assertEqual(result['status'], 'skipped')
        
        # Test failed folder
        cloud_event.data = {
            'bucket': 'test-bucket',
            'name': 'failed/file.txt'
        }
        result = main.process_rag_upload(cloud_event)
        self.assertEqual(result['status'], 'skipped')
        
    @patch('main.vertexai')
    @patch('main.rag')
    def test_get_or_create_corpus(self, mock_rag, mock_vertexai):
        """Test corpus creation and retrieval."""
        # Mock existing corpus
        existing_corpus = Mock()
        existing_corpus.display_name = 'test-corpus'
        existing_corpus.name = 'projects/test/locations/us-central1/corpora/12345'
        
        # Mock list response
        mock_rag.RagDataService.list_rag_corpora.return_value = [existing_corpus]
        
        # Test getting existing corpus
        corpus_name, created = main.get_or_create_corpus('test-corpus')
        self.assertEqual(corpus_name, existing_corpus.name)
        self.assertFalse(created)
        
        # Test creating new corpus
        mock_rag.RagDataService.list_rag_corpora.return_value = []
        
        new_corpus = Mock()
        new_corpus.name = 'projects/test/locations/us-central1/corpora/67890'
        
        operation = Mock()
        operation.result.return_value = new_corpus
        mock_rag.RagDataService.create_rag_corpus.return_value = operation
        
        corpus_name, created = main.get_or_create_corpus('new-corpus')
        self.assertEqual(corpus_name, new_corpus.name)
        self.assertTrue(created)
        
    @patch('main.storage.Client')
    def test_move_to_processed(self, mock_storage):
        """Test moving file to processed folder."""
        # Mock source blob
        mock_source_blob = Mock()
        mock_source_blob.download_as_bytes.return_value = b'file content'
        mock_source_blob.content_type = 'text/plain'
        mock_source_blob.metadata = {'test': 'metadata'}
        
        # Mock destination blob
        mock_dest_blob = Mock()
        
        # Mock bucket
        mock_bucket = Mock()
        mock_bucket.blob.side_effect = lambda name: (
            mock_source_blob if name == 'test.txt' else mock_dest_blob
        )
        
        # Mock client
        mock_client = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        
        # Test move operation
        main.move_to_processed('test-bucket', 'test.txt')
        
        # Verify operations
        mock_bucket.blob.assert_any_call('test.txt')
        mock_bucket.blob.assert_any_call('processed/test.txt')
        mock_dest_blob.upload_from_string.assert_called_once()
        mock_source_blob.delete.assert_called_once()
        
    @patch('main.storage.Client')
    def test_handle_error(self, mock_storage):
        """Test error handling."""
        # Mock blobs
        mock_source_blob = Mock()
        mock_source_blob.exists.return_value = True
        mock_source_blob.download_as_bytes.return_value = b'file content'
        mock_source_blob.content_type = 'text/plain'
        
        mock_error_blob = Mock()
        
        # Mock bucket
        mock_bucket = Mock()
        def get_blob(name):
            if name == 'test.txt':
                return mock_source_blob
            elif name.endswith('.error.json'):
                return mock_error_blob
            else:
                return Mock()
                
        mock_bucket.blob.side_effect = get_blob
        
        # Mock client
        mock_client = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        
        # Test error handling
        main.handle_error('test-bucket', 'test.txt', 'Test error message')
        
        # Verify error log was created
        mock_error_blob.upload_from_string.assert_called_once()
        error_data = json.loads(mock_error_blob.upload_from_string.call_args[0][0])
        self.assertEqual(error_data['file'], 'test.txt')
        self.assertEqual(error_data['error'], 'Test error message')
        self.assertIn('timestamp', error_data)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete flow."""
    
    @patch('main.ingest_to_rag')
    @patch('main.move_to_processed')
    @patch('main.extract_metadata')
    @patch('main.validate_file_type')
    def test_successful_processing(self, mock_validate, mock_metadata, 
                                 mock_move, mock_ingest):
        """Test successful file processing."""
        # Set up mocks
        mock_validate.return_value = True
        mock_metadata.return_value = {'test': 'metadata'}
        mock_ingest.return_value = {
            'status': 'success',
            'file': 'test.pdf',
            'corpus': 'test-corpus'
        }
        
        # Create cloud event
        cloud_event = Mock()
        cloud_event.data = {
            'bucket': 'test-bucket',
            'name': 'test.pdf'
        }
        
        # Process file
        result = main.process_rag_upload(cloud_event)
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        mock_validate.assert_called_once_with('test.pdf')
        mock_metadata.assert_called_once()
        mock_ingest.assert_called_once()
        mock_move.assert_called_once()
        
    @patch('main.handle_error')
    @patch('main.validate_file_type')
    def test_invalid_file_type(self, mock_validate, mock_error):
        """Test handling of invalid file type."""
        # Set up mocks
        mock_validate.return_value = False
        
        # Create cloud event
        cloud_event = Mock()
        cloud_event.data = {
            'bucket': 'test-bucket',
            'name': 'image.png'
        }
        
        # Process file
        result = main.process_rag_upload(cloud_event)
        
        # Verify result
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unsupported file type', result['error'])
        mock_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
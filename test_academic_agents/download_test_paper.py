#!/usr/bin/env python3
"""Download a test academic paper for PDF parsing."""

import requests
import os

def download_test_paper():
    """Download the Attention Is All You Need paper from arXiv."""
    
    # URL for the Transformer paper PDF from arXiv
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
    
    # Download location
    output_path = "test_academic_agents/attention_is_all_you_need.pdf"
    
    print(f"Downloading paper from: {pdf_url}")
    
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        # Save to file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded to: {output_path}")
        print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
        return output_path
        
    except Exception as e:
        print(f"Error downloading paper: {e}")
        return None

if __name__ == "__main__":
    download_test_paper()
#!/usr/bin/env python3
"""
Test individual tools directly without agent wrappers.
This helps isolate tool-specific issues.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
import vertexai
from google.adk.tools import ToolContext

# Load environment
load_dotenv()

# Initialize Vertex AI
project = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
vertexai.init(project=project, location=location)


def test_weather_tools():
    """Test weather agent tools directly"""
    print("\n" + "="*60)
    print("TESTING WEATHER TOOLS DIRECTLY")
    print("="*60)
    
    from mas_system.sub_agents.weather_agent.tools import get_weather, get_forecast
    
    # Test get_weather
    print("\n1. Testing get_weather('San Francisco')...")
    result = get_weather("San Francisco")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result['status'] == 'success':
        data = result['data']
        print(f"   Temperature: {data['temperature']}°C")
        print(f"   Conditions: {data['conditions']}")
        
    # Test get_forecast
    print("\n2. Testing get_forecast('New York', days=3)...")
    result = get_forecast("New York", days=3)
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result['status'] == 'success':
        print(f"   Forecast days: {len(result['data']['forecast'])}")


def test_rag_tools():
    """Test RAG tools directly"""
    print("\n" + "="*60)
    print("TESTING RAG TOOLS DIRECTLY")
    print("="*60)
    
    from mas_system.sub_agents.rag_agent.tools import (
        list_corpora, create_corpus, add_data, rag_query, get_corpus_info
    )
    
    tool_context = ToolContext()
    
    # Test list_corpora
    print("\n1. Testing list_corpora()...")
    result = list_corpora(tool_context)
    print(f"   Status: {result['status']}")
    print(f"   Found {result['data']['count']} corpora")
    
    # Test create_corpus
    print("\n2. Testing create_corpus()...")
    test_corpus_name = f"test_tool_corpus_{int(os.urandom(4).hex(), 16)}"
    result = create_corpus(
        corpus_name=test_corpus_name,
        description="Test corpus for tool testing",
        tool_context=tool_context
    )
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    # Test add_data
    print("\n3. Testing add_data()...")
    test_content = """
    This is a test document for tool testing.
    It contains sample content about agents and testing.
    The weather agent can provide weather information.
    The RAG agent manages document collections.
    """
    result = add_data(
        content=test_content,
        title="Tool Test Document",
        tool_context=tool_context
    )
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    # Test rag_query
    print("\n4. Testing rag_query()...")
    import time
    time.sleep(3)  # Wait for indexing
    result = rag_query(
        query="What agents are mentioned?",
        tool_context=tool_context
    )
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Found {len(result['data']['results'])} chunks")
        if result['data']['results']:
            print(f"   Top result preview: {result['data']['results'][0]['content'][:100]}...")
            
    # Test get_corpus_info
    print("\n5. Testing get_corpus_info()...")
    result = get_corpus_info(tool_context)
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Corpus: {result['data']['display_name']}")
        print(f"   Document count: {result['data'].get('document_count', 'N/A')}")


def test_academic_tools():
    """Test academic tools directly"""
    print("\n" + "="*60)
    print("TESTING ACADEMIC TOOLS DIRECTLY")
    print("="*60)
    
    from mas_system.sub_agents.academic_tools import (
        analyze_seminal_paper, prepare_paper_for_citation_search,
        get_example_pdf_url
    )
    
    # Get example PDF
    pdf_url = get_example_pdf_url()
    print(f"\n1. Using example PDF: {pdf_url}")
    
    # Test analyze_seminal_paper
    print("\n2. Testing analyze_seminal_paper()...")
    result = analyze_seminal_paper(pdf_url)
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        data = result['data']
        print(f"   Title: {data.get('title', 'N/A')}")
        print(f"   Authors: {data.get('authors', 'N/A')[:50]}...")
        print(f"   Year: {data.get('year', 'N/A')}")
        
    # Test prepare_paper_for_citation_search
    print("\n3. Testing prepare_paper_for_citation_search()...")
    result = prepare_paper_for_citation_search(pdf_url)
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        formatted = result['data']['formatted_paper']
        print(f"   Formatted length: {len(formatted)} characters")
        print(f"   Preview: {formatted[:150]}...")


def main():
    """Run all tool tests"""
    print("="*60)
    print("DIRECT TOOL TESTING")
    print("="*60)
    print("Testing tools without agent wrappers to isolate issues")
    
    try:
        test_weather_tools()
    except Exception as e:
        print(f"\n❌ Weather tools error: {e}")
        
    try:
        test_rag_tools()
    except Exception as e:
        print(f"\n❌ RAG tools error: {e}")
        
    try:
        test_academic_tools()
    except Exception as e:
        print(f"\n❌ Academic tools error: {e}")
        
    print("\n" + "="*60)
    print("TOOL TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
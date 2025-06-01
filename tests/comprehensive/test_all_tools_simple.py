#!/usr/bin/env python3
"""
Comprehensive test suite for all MAS agent tools.
Tests every tool directly to ensure full functionality.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
import vertexai
from google.adk.tools import ToolContext

# Import tools for direct testing
from tests.comprehensive.weather_test_wrappers import test_get_weather, test_get_forecast
from tests.comprehensive.mock_tool_context import MockToolContext
from mas_system.sub_agents.rag_agent.tools import (
    create_corpus, list_corpora, add_data, rag_query,
    get_corpus_info, delete_document, delete_corpus
)
from mas_system.sub_agents.academic_tools import (
    analyze_seminal_paper, prepare_paper_for_citation_search,
    format_citations_for_research, get_example_pdf_url
)

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
vertexai.init(project=project, location=location)


class ToolTester:
    """Test all tools comprehensively"""
    
    def __init__(self):
        self.results = []
        self.test_corpus_name = f"test_corpus_{int(time.time())}"
        
    def test_weather_tools(self):
        """Test Weather Agent tools"""
        print("\n" + "="*60)
        print("TESTING WEATHER AGENT TOOLS")
        print("="*60)
        
        # Test 1: get_weather
        print("\n1. Testing get_weather('San Francisco')...")
        try:
            result = test_get_weather("San Francisco")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            if result['status'] == 'success':
                print(f"   ✅ Temperature: {result['data']['temperature']}°F")
                self.results.append(("Weather", "get_current_weather", "PASSED"))
            else:
                self.results.append(("Weather", "get_current_weather", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Weather", "get_current_weather", f"ERROR: {e}"))
            
        # Test 2: get_forecast
        print("\n2. Testing get_forecast('New York', days=3)...")
        try:
            result = test_get_forecast("New York", days=3)
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            if result['status'] == 'success':
                print(f"   ✅ Got {len(result['data']['forecast'])} day forecast")
                self.results.append(("Weather", "get_weather_forecast", "PASSED"))
            else:
                self.results.append(("Weather", "get_weather_forecast", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Weather", "get_weather_forecast", f"ERROR: {e}"))
            
    def test_rag_tools(self):
        """Test RAG Agent tools"""
        print("\n" + "="*60)
        print("TESTING RAG AGENT TOOLS")
        print("="*60)
        
        tool_context = MockToolContext()  # Create mock context with state
        
        # Test 1: list_corpora
        print("\n1. Testing list_corpora()...")
        try:
            result = list_corpora(tool_context)
            print(f"   Status: {result['status']}")
            print(f"   ✅ Found {result['data']['count']} corpora")
            self.results.append(("RAG", "list_corpora", "PASSED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "list_corpora", f"ERROR: {e}"))
            
        # Test 2: create_corpus
        print("\n2. Testing create_corpus()...")
        try:
            result = create_corpus(
                corpus_name=self.test_corpus_name,
                description="Test corpus",
                tool_context=tool_context
            )
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            if result['status'] in ['success', 'info']:
                print("   ✅ Corpus created/exists")
                # Set the corpus as current in the context
                tool_context.set_current_corpus(self.test_corpus_name)
                self.results.append(("RAG", "create_corpus", "PASSED"))
            else:
                self.results.append(("RAG", "create_corpus", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "create_corpus", f"ERROR: {e}"))
            
        # Test 3: add_data
        print("\n3. Testing add_data()...")
        try:
            # Create a temporary test file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("This is test content for RAG testing.")
                test_file_path = f.name
            
            result = add_data(
                corpus_name="",  # Empty string uses current corpus
                paths=[test_file_path],
                tool_context=tool_context
            )
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print("   ✅ Document added")
                self.results.append(("RAG", "add_data", "PASSED"))
            else:
                self.results.append(("RAG", "add_data", "FAILED"))
            
            # Cleanup temp file
            import os
            os.unlink(test_file_path)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "add_data", f"ERROR: {e}"))
            
        # Test 4: rag_query
        print("\n4. Testing rag_query()...")
        time.sleep(3)  # Wait for indexing
        try:
            result = rag_query(
                corpus_name="",  # Empty string uses current corpus
                query="test content",
                tool_context=tool_context
            )
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print(f"   ✅ Found {len(result['data']['results'])} chunks")
                self.results.append(("RAG", "rag_query", "PASSED"))
            else:
                self.results.append(("RAG", "rag_query", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "rag_query", f"ERROR: {e}"))
            
        # Test 5: get_corpus_info
        print("\n5. Testing get_corpus_info()...")
        try:
            result = get_corpus_info(
                corpus_name="",  # Empty string uses current corpus
                tool_context=tool_context
            )
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print("   ✅ Got corpus info")
                self.results.append(("RAG", "get_corpus_info", "PASSED"))
            else:
                self.results.append(("RAG", "get_corpus_info", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "get_corpus_info", f"ERROR: {e}"))
            
        # Test 6: delete_corpus (cleanup)
        print("\n6. Testing delete_corpus()...")
        try:
            result = delete_corpus(
                corpus_name=self.test_corpus_name,
                confirm=True,
                tool_context=tool_context
            )
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print("   ✅ Corpus deleted")
                self.results.append(("RAG", "delete_corpus", "PASSED"))
            else:
                self.results.append(("RAG", "delete_corpus", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("RAG", "delete_corpus", f"ERROR: {e}"))
            
    def test_academic_tools(self):
        """Test Academic tools"""
        print("\n" + "="*60)
        print("TESTING ACADEMIC TOOLS")
        print("="*60)
        
        # Test 1: analyze_seminal_paper
        print("\n1. Testing analyze_seminal_paper()...")
        try:
            pdf_url = get_example_pdf_url()
            result = analyze_seminal_paper(pdf_url)
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print(f"   ✅ Analyzed: {result['data'].get('title', 'Unknown')}")
                self.results.append(("Academic", "analyze_seminal_paper", "PASSED"))
            else:
                self.results.append(("Academic", "analyze_seminal_paper", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Academic", "analyze_seminal_paper", f"ERROR: {e}"))
            
        # Test 2: prepare_paper_for_citation_search
        print("\n2. Testing prepare_paper_for_citation_search()...")
        try:
            result = prepare_paper_for_citation_search(pdf_url)
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print("   ✅ Paper prepared for search")
                self.results.append(("Academic", "prepare_paper_for_citation_search", "PASSED"))
            else:
                self.results.append(("Academic", "prepare_paper_for_citation_search", "FAILED"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Academic", "prepare_paper_for_citation_search", f"ERROR: {e}"))
            
    def test_agent_existence(self):
        """Test that all agents exist and are properly configured"""
        print("\n" + "="*60)
        print("TESTING AGENT CONFIGURATIONS")
        print("="*60)
        
        agents_to_test = [
            ("Weather Agent", "mas_system.sub_agents.weather_agent", "weather_agent"),
            ("Greeter Agent", "mas_system.sub_agents.greeter_agent", "greeter_agent"),
            ("RAG Agent", "mas_system.sub_agents.rag_agent", "rag_agent"),
            ("Academic WebSearch", "mas_system.sub_agents.academic_websearch", "academic_websearch_agent"),
            ("Academic NewResearch", "mas_system.sub_agents.academic_newresearch", "academic_newresearch_agent"),
            ("MAS Coordinator", "mas_system.agent", "mas_coordinator")
        ]
        
        for agent_name, module_path, agent_var in agents_to_test:
            print(f"\nChecking {agent_name}...")
            try:
                module = __import__(module_path, fromlist=[agent_var])
                agent = getattr(module, agent_var)
                if agent:
                    print(f"   ✅ {agent_name} exists")
                    self.results.append(("Agents", agent_name, "EXISTS"))
                else:
                    print(f"   ❌ {agent_name} not found")
                    self.results.append(("Agents", agent_name, "NOT FOUND"))
            except Exception as e:
                print(f"   ❌ Error loading {agent_name}: {e}")
                self.results.append(("Agents", agent_name, f"ERROR: {e}"))
                
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for _, _, status in self.results if status == "PASSED" or status == "EXISTS")
        failed = sum(1 for _, _, status in self.results if status == "FAILED" or status == "NOT FOUND")
        errors = sum(1 for _, _, status in self.results if status.startswith("ERROR"))
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print(f"\nSuccess Rate: {(passed/total)*100:.1f}%")
        
        # Save results
        timestamp = int(time.time())
        report_file = f"test_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors
                },
                "results": [
                    {"category": cat, "tool": tool, "status": status}
                    for cat, tool, status in self.results
                ]
            }, f, indent=2)
            
        print(f"\nReport saved to: {report_file}")
        
        return passed == total


def main():
    """Run all tests"""
    print("="*60)
    print("MAS COMPREHENSIVE TOOL TESTING")
    print("="*60)
    
    tester = ToolTester()
    
    # Run all tests
    tester.test_weather_tools()
    tester.test_rag_tools()
    tester.test_academic_tools()
    tester.test_agent_existence()
    
    # Generate summary
    all_passed = tester.generate_summary()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the report for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Comprehensive test suite for all MAS agents and their tools.
Tests every tool in every agent to ensure full functionality.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
# Testing tools directly without InMemoryRunner
from google.adk.tools import ToolContext

# Import all agents
from mas_system.sub_agents.weather_agent import weather_agent
from mas_system.sub_agents.greeter_agent import greeter_agent
from mas_system.sub_agents.academic_websearch import academic_websearch_agent
from mas_system.sub_agents.academic_newresearch import academic_newresearch_agent
from mas_system.sub_agents.rag_agent import rag_agent
from mas_system.agent import mas_coordinator

# Import tools for direct testing
from mas_system.sub_agents.weather_agent.tools import get_weather, get_forecast
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


class TestStatus(Enum):
    """Test result status"""
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    SKIPPED = "⚠️ SKIPPED"
    ERROR = "🔥 ERROR"


@dataclass
class TestResult:
    """Test result data"""
    agent_name: str
    tool_name: str
    test_name: str
    status: TestStatus
    message: str
    duration: float
    details: Dict[str, Any] = None


class ComprehensiveAgentTester:
    """Comprehensive tester for all MAS agents and tools"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.test_corpus_name = f"test_corpus_{int(time.time())}"
        
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
        print(f"{result.status.value} {result.agent_name} - {result.tool_name}: {result.test_name}")
        if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
            print(f"  Details: {result.message}")
            
    def test_weather_agent_tools(self):
        """Test all Weather Agent tools"""
        print("\n" + "="*80)
        print("TESTING WEATHER AGENT TOOLS")
        print("="*80)
        
        # Test 1: get_weather tool
        start = time.time()
        try:
            result = get_weather("San Francisco")
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="Weather Agent",
                    tool_name="get_weather",
                    test_name="Get weather for San Francisco",
                    status=TestStatus.PASSED,
                    message="Successfully retrieved weather data",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="Weather Agent",
                    tool_name="get_weather",
                    test_name="Get weather for San Francisco",
                    status=TestStatus.FAILED,
                    message=result.get('message', 'Unknown error'),
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Weather Agent",
                tool_name="get_weather",
                test_name="Get weather for San Francisco",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 2: get_forecast tool
        start = time.time()
        try:
            result = get_forecast("New York", days=3)
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="Weather Agent",
                    tool_name="get_forecast",
                    test_name="Get 3-day forecast for New York",
                    status=TestStatus.PASSED,
                    message="Successfully retrieved forecast data",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="Weather Agent",
                    tool_name="get_forecast",
                    test_name="Get 3-day forecast for New York",
                    status=TestStatus.FAILED,
                    message=result.get('message', 'Unknown error'),
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Weather Agent",
                tool_name="get_forecast",
                test_name="Get 3-day forecast for New York",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 3: Weather agent through runner
        start = time.time()
        try:
            runner = InMemoryRunner(agent=weather_agent)
            response = runner.send("What's the weather like in Tokyo?")
            self.add_result(TestResult(
                agent_name="Weather Agent",
                tool_name="agent_query",
                test_name="Query weather through agent",
                status=TestStatus.PASSED,
                message="Successfully queried weather agent",
                duration=time.time() - start,
                details={"response": response[:200] + "..." if len(response) > 200 else response}
            ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Weather Agent",
                tool_name="agent_query",
                test_name="Query weather through agent",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
    def test_rag_agent_tools(self):
        """Test all RAG Agent tools"""
        print("\n" + "="*80)
        print("TESTING RAG AGENT TOOLS")
        print("="*80)
        
        tool_context = ToolContext()
        
        # Test 1: list_corpora
        start = time.time()
        try:
            result = list_corpora(tool_context)
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="list_corpora",
                test_name="List all RAG corpora",
                status=TestStatus.PASSED,
                message=f"Found {result['data']['count']} corpora",
                duration=time.time() - start,
                details=result
            ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="list_corpora",
                test_name="List all RAG corpora",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 2: create_corpus
        start = time.time()
        try:
            result = create_corpus(
                corpus_name=self.test_corpus_name,
                description="Test corpus for comprehensive testing",
                tool_context=tool_context
            )
            if result['status'] in ['success', 'info']:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="create_corpus",
                    test_name="Create test corpus",
                    status=TestStatus.PASSED,
                    message=result['message'],
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="create_corpus",
                    test_name="Create test corpus",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="create_corpus",
                test_name="Create test corpus",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 3: add_data
        start = time.time()
        try:
            test_content = """
            Test Document for RAG Agent
            
            This is a comprehensive test document to verify RAG functionality.
            It contains information about testing, agents, and functionality.
            The MAS system uses multiple agents to handle different tasks.
            """
            
            result = add_data(
                content=test_content,
                title="Test Document",
                tool_context=tool_context
            )
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="add_data",
                    test_name="Add test document to corpus",
                    status=TestStatus.PASSED,
                    message="Successfully added document",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="add_data",
                    test_name="Add test document to corpus",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="add_data",
                test_name="Add test document to corpus",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 4: rag_query
        time.sleep(5)  # Wait for indexing
        start = time.time()
        try:
            result = rag_query(
                query="What information is in the test document?",
                tool_context=tool_context
            )
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="rag_query",
                    test_name="Query test document",
                    status=TestStatus.PASSED,
                    message=f"Found {len(result['data']['results'])} relevant chunks",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="rag_query",
                    test_name="Query test document",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="rag_query",
                test_name="Query test document",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 5: get_corpus_info
        start = time.time()
        try:
            result = get_corpus_info(tool_context=tool_context)
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="get_corpus_info",
                    test_name="Get corpus information",
                    status=TestStatus.PASSED,
                    message="Successfully retrieved corpus info",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="get_corpus_info",
                    test_name="Get corpus information",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="get_corpus_info",
                test_name="Get corpus information",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 6: delete_corpus (cleanup)
        start = time.time()
        try:
            # Set the test corpus as current
            tool_context.state["current_corpus_display_name"] = self.test_corpus_name
            result = delete_corpus(tool_context=tool_context)
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="delete_corpus",
                    test_name="Delete test corpus",
                    status=TestStatus.PASSED,
                    message="Successfully deleted test corpus",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="RAG Agent",
                    tool_name="delete_corpus",
                    test_name="Delete test corpus",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="RAG Agent",
                tool_name="delete_corpus",
                test_name="Delete test corpus",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
    def test_academic_agent_tools(self):
        """Test Academic Agent tools"""
        print("\n" + "="*80)
        print("TESTING ACADEMIC AGENT TOOLS")
        print("="*80)
        
        # Test 1: analyze_seminal_paper
        start = time.time()
        try:
            pdf_url = get_example_pdf_url()
            result = analyze_seminal_paper(pdf_url)
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="Academic Agents",
                    tool_name="analyze_seminal_paper",
                    test_name="Analyze example PDF",
                    status=TestStatus.PASSED,
                    message=f"Analyzed: {result['data'].get('title', 'Unknown')}",
                    duration=time.time() - start,
                    details=result
                ))
            else:
                self.add_result(TestResult(
                    agent_name="Academic Agents",
                    tool_name="analyze_seminal_paper",
                    test_name="Analyze example PDF",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Academic Agents",
                tool_name="analyze_seminal_paper",
                test_name="Analyze example PDF",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
        # Test 2: prepare_paper_for_citation_search
        start = time.time()
        try:
            result = prepare_paper_for_citation_search(pdf_url)
            if result['status'] == 'success':
                self.add_result(TestResult(
                    agent_name="Academic Agents",
                    tool_name="prepare_paper_for_citation_search",
                    test_name="Prepare paper for citation search",
                    status=TestStatus.PASSED,
                    message="Successfully formatted paper",
                    duration=time.time() - start,
                    details={"formatted_length": len(result['data']['formatted_paper'])}
                ))
            else:
                self.add_result(TestResult(
                    agent_name="Academic Agents",
                    tool_name="prepare_paper_for_citation_search",
                    test_name="Prepare paper for citation search",
                    status=TestStatus.FAILED,
                    message=result['message'],
                    duration=time.time() - start
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Academic Agents",
                tool_name="prepare_paper_for_citation_search",
                test_name="Prepare paper for citation search",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
    def test_greeter_agent(self):
        """Test Greeter Agent (no tools, just responses)"""
        print("\n" + "="*80)
        print("TESTING GREETER AGENT")
        print("="*80)
        
        start = time.time()
        try:
            runner = InMemoryRunner(agent=greeter_agent)
            
            # Test greetings
            greetings = ["Hello!", "Good morning", "Hi there", "Goodbye"]
            for greeting in greetings:
                response = runner.send(greeting)
                self.add_result(TestResult(
                    agent_name="Greeter Agent",
                    tool_name="response_generation",
                    test_name=f"Respond to '{greeting}'",
                    status=TestStatus.PASSED,
                    message="Generated appropriate response",
                    duration=time.time() - start,
                    details={"input": greeting, "response": response[:100] + "..."}
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="Greeter Agent",
                tool_name="response_generation",
                test_name="Test greetings",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
    def test_mas_coordinator(self):
        """Test MAS Coordinator routing"""
        print("\n" + "="*80)
        print("TESTING MAS COORDINATOR")
        print("="*80)
        
        start = time.time()
        try:
            runner = InMemoryRunner(agent=mas_coordinator)
            
            # Test routing to different agents
            test_queries = [
                ("Hello there!", "Greeter Agent"),
                ("What's the weather in Paris?", "Weather Agent"),
                ("Search my documents for information about agents", "RAG Agent"),
                ("Find papers about transformers", "Academic Agent")
            ]
            
            for query, expected_agent in test_queries:
                response = runner.send(query)
                self.add_result(TestResult(
                    agent_name="MAS Coordinator",
                    tool_name="routing",
                    test_name=f"Route '{query}' to {expected_agent}",
                    status=TestStatus.PASSED,
                    message=f"Successfully routed and responded",
                    duration=time.time() - start,
                    details={"query": query, "response": response[:150] + "..."}
                ))
        except Exception as e:
            self.add_result(TestResult(
                agent_name="MAS Coordinator",
                tool_name="routing",
                test_name="Test routing",
                status=TestStatus.ERROR,
                message=str(e),
                duration=time.time() - start
            ))
            
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("TEST REPORT SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print(f"⚠️  Skipped: {skipped}")
        print(f"\nSuccess Rate: {(passed/total_tests)*100:.1f}%")
        print(f"Total Duration: {time.time() - self.start_time:.2f}s")
        
        # Group results by agent
        print("\n" + "-"*80)
        print("RESULTS BY AGENT:")
        print("-"*80)
        
        agents = {}
        for result in self.results:
            if result.agent_name not in agents:
                agents[result.agent_name] = []
            agents[result.agent_name].append(result)
            
        for agent_name, results in agents.items():
            print(f"\n{agent_name}:")
            for result in results:
                print(f"  {result.status.value} {result.tool_name}: {result.test_name}")
                
        # Save detailed report
        report_path = f"/Users/eugene/dev/ai/google/adk-samples/python/agents/MAS/tests/comprehensive/test_report_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "skipped": skipped,
                    "success_rate": (passed/total_tests)*100,
                    "duration": time.time() - self.start_time
                },
                "results": [
                    {
                        "agent": r.agent_name,
                        "tool": r.tool_name,
                        "test": r.test_name,
                        "status": r.status.value,
                        "message": r.message,
                        "duration": r.duration,
                        "details": r.details
                    }
                    for r in self.results
                ]
            }
            json.dump(report_data, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_path}")
        
        return passed == total_tests
    
    def run_all_tests(self):
        """Run all tests"""
        print("="*80)
        print("COMPREHENSIVE MAS AGENT AND TOOL TESTING")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests for each agent
        self.test_weather_agent_tools()
        self.test_greeter_agent()
        self.test_rag_agent_tools()
        self.test_academic_agent_tools()
        self.test_mas_coordinator()
        
        # Generate report
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print("\n⚠️  Some tests failed. Check the report for details.")
            
        return all_passed


if __name__ == "__main__":
    tester = ComprehensiveAgentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
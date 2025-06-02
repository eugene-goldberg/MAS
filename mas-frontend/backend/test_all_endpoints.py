#!/usr/bin/env python3
"""
Comprehensive test script for MAS Testing Frontend API
Tests all endpoints and validates end-to-end functionality
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
import websockets
from colorama import init, Fore, Style

init(autoreset=True)

API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

class EndpointTester:
    def __init__(self):
        self.results = []
        self.session_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
    async def run_all_tests(self):
        """Run all endpoint tests"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}MAS Testing Frontend - Comprehensive API Test")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        async with aiohttp.ClientSession() as session:
            # Basic connectivity tests
            await self.test_root_endpoint(session)
            await self.test_health_endpoint(session)
            await self.test_test_endpoint(session)
            
            # Agent information tests
            await self.test_agent_info(session)
            await self.test_agent_metrics(session)
            await self.test_tool_usage(session)
            
            # Session management tests
            await self.test_session_create(session)
            await self.test_session_get(session)
            await self.test_session_list(session)
            
            # Chat functionality tests
            await self.test_chat_send(session)
            await self.test_chat_history(session)
            
            # Testing endpoints
            await self.test_get_scenarios(session)
            await self.test_validate_tools(session)
            await self.test_run_agent_tests(session)
            await self.test_performance(session)
            await self.test_comprehensive_health(session)
            
            # WebSocket test
            await self.test_websocket_connection()
        
        # Print summary
        self.print_summary()
    
    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, 
                          endpoint: str, test_name: str, **kwargs) -> Dict[str, Any]:
        """Generic endpoint test helper"""
        url = f"{API_BASE_URL}{endpoint}"
        print(f"\n{Fore.YELLOW}Testing: {test_name}")
        print(f"  {method} {endpoint}")
        
        try:
            async with session.request(method, url, **kwargs) as response:
                status = response.status
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                success = 200 <= status < 300
                self.results.append({
                    "test": test_name,
                    "endpoint": endpoint,
                    "status": status,
                    "success": success
                })
                
                if success:
                    print(f"  {Fore.GREEN}✓ Status: {status}")
                    if isinstance(data, dict) and len(str(data)) < 200:
                        print(f"  {Fore.GREEN}✓ Response: {json.dumps(data, indent=2)}")
                    else:
                        print(f"  {Fore.GREEN}✓ Response received (truncated)")
                else:
                    print(f"  {Fore.RED}✗ Status: {status}")
                    print(f"  {Fore.RED}✗ Error: {data}")
                
                return {"status": status, "data": data, "success": success}
                
        except Exception as e:
            print(f"  {Fore.RED}✗ Error: {str(e)}")
            self.results.append({
                "test": test_name,
                "endpoint": endpoint,
                "status": 0,
                "success": False,
                "error": str(e)
            })
            return {"status": 0, "data": None, "success": False, "error": str(e)}
    
    # Individual test methods
    async def test_root_endpoint(self, session):
        await self.test_endpoint(session, "GET", "/", "Root Endpoint")
    
    async def test_health_endpoint(self, session):
        await self.test_endpoint(session, "GET", "/health", "Health Check")
    
    async def test_test_endpoint(self, session):
        await self.test_endpoint(session, "GET", "/test", "Test Endpoint")
    
    async def test_agent_info(self, session):
        result = await self.test_endpoint(session, "GET", "/api/agents/info", "Agent Information")
        if result["success"] and result["data"]:
            agents = result["data"].get("agents", [])
            print(f"  {Fore.CYAN}ℹ Found {len(agents)} agents")
    
    async def test_agent_metrics(self, session):
        await self.test_endpoint(session, "GET", "/api/agents/metrics", "Agent Metrics")
    
    async def test_tool_usage(self, session):
        await self.test_endpoint(session, "GET", "/api/agents/tools", "Tool Usage Stats")
    
    async def test_session_create(self, session):
        result = await self.test_endpoint(session, "POST", "/api/sessions/create", "Create Session")
        if result["success"] and result["data"]:
            self.session_id = result["data"].get("session_id", self.session_id)
    
    async def test_session_get(self, session):
        await self.test_endpoint(session, "GET", f"/api/sessions/{self.session_id}", "Get Session")
    
    async def test_session_list(self, session):
        await self.test_endpoint(session, "GET", "/api/sessions/active", "List Active Sessions")
    
    async def test_chat_send(self, session):
        data = {
            "message": "Hello, this is a test message!",
            "session_id": self.session_id
        }
        result = await self.test_endpoint(
            session, "POST", "/api/chat/send", "Send Chat Message",
            json=data
        )
        if result["success"]:
            print(f"  {Fore.CYAN}ℹ Response length: {len(result['data'].get('response', ''))}")
            if result['data'].get('execution_trace'):
                trace = result['data']['execution_trace']
                print(f"  {Fore.CYAN}ℹ Execution time: {trace.get('total_time_ms', 0)}ms")
                print(f"  {Fore.CYAN}ℹ Agents used: {', '.join(trace.get('agent_sequence', []))}")
    
    async def test_chat_history(self, session):
        await self.test_endpoint(
            session, "GET", f"/api/chat/history/{self.session_id}?limit=10", 
            "Get Chat History"
        )
    
    async def test_get_scenarios(self, session):
        result = await self.test_endpoint(session, "GET", "/api/test/scenarios", "Get Test Scenarios")
        if result["success"] and result["data"]:
            total = sum(len(scenarios) for scenarios in result["data"].values())
            print(f"  {Fore.CYAN}ℹ Total test scenarios: {total}")
    
    async def test_validate_tools(self, session):
        result = await self.test_endpoint(session, "POST", "/api/test/validate-tools", "Validate Tools")
        if result["success"] and result["data"]:
            all_valid = result["data"].get("all_tools_valid", False)
            print(f"  {Fore.CYAN}ℹ All tools valid: {'Yes' if all_valid else 'No'}")
    
    async def test_run_agent_tests(self, session):
        # Test individual agent types
        for agent_type in ["greeter", "weather"]:
            result = await self.test_endpoint(
                session, "POST", f"/api/test/run/{agent_type}", 
                f"Run {agent_type.title()} Agent Tests"
            )
            if result["success"] and result["data"]:
                data = result["data"]
                print(f"  {Fore.CYAN}ℹ Passed: {data['passed']}/{data['total_tests']}")
                print(f"  {Fore.CYAN}ℹ Success rate: {data['success_rate']:.1f}%")
    
    async def test_performance(self, session):
        result = await self.test_endpoint(
            session, "POST", "/api/test/performance-test?iterations=3", 
            "Performance Test"
        )
        if result["success"] and result["data"]:
            avg_time = result["data"].get("overall_avg_ms", 0)
            print(f"  {Fore.CYAN}ℹ Overall average response time: {avg_time:.1f}ms")
    
    async def test_comprehensive_health(self, session):
        result = await self.test_endpoint(
            session, "GET", "/api/test/health-check", 
            "Comprehensive Health Check"
        )
        if result["success"] and result["data"]:
            health = result["data"].get("overall_health", "unknown")
            print(f"  {Fore.CYAN}ℹ Overall health: {health}")
            components = result["data"].get("components", {})
            for comp, status in components.items():
                emoji = "✓" if status else "✗"
                color = Fore.GREEN if status else Fore.RED
                print(f"  {color}{emoji} {comp}: {status}")
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print(f"\n{Fore.YELLOW}Testing: WebSocket Connection")
        print(f"  WS {WS_BASE_URL}/ws/chat/{self.session_id}")
        
        try:
            uri = f"{WS_BASE_URL}/ws/chat/{self.session_id}"
            async with websockets.connect(uri) as websocket:
                # Wait for connection established message
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                
                if data.get("type") == "connection_established":
                    print(f"  {Fore.GREEN}✓ WebSocket connected")
                    print(f"  {Fore.GREEN}✓ Session ID: {data.get('session_id')}")
                    
                    # Test sending a message
                    test_message = {
                        "type": "chat_message",
                        "content": "WebSocket test message"
                    }
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for acknowledgment
                    ack = await asyncio.wait_for(websocket.recv(), timeout=5)
                    ack_data = json.loads(ack)
                    if ack_data.get("type") == "message_received":
                        print(f"  {Fore.GREEN}✓ Message acknowledged")
                    
                    self.results.append({
                        "test": "WebSocket Connection",
                        "endpoint": f"/ws/chat/{self.session_id}",
                        "status": 200,
                        "success": True
                    })
                else:
                    print(f"  {Fore.RED}✗ Unexpected message type: {data.get('type')}")
                    self.results.append({
                        "test": "WebSocket Connection",
                        "endpoint": f"/ws/chat/{self.session_id}",
                        "status": 0,
                        "success": False
                    })
                    
        except Exception as e:
            print(f"  {Fore.RED}✗ WebSocket error: {str(e)}")
            self.results.append({
                "test": "WebSocket Connection",
                "endpoint": f"/ws/chat/{self.session_id}",
                "status": 0,
                "success": False,
                "error": str(e)
            })
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Test Summary")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"{Fore.GREEN}Passed: {passed_tests}")
        print(f"{Fore.RED}Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")
        
        if failed_tests > 0:
            print(f"{Fore.RED}Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']} ({result['endpoint']})")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        
        # Return exit code based on results
        return 0 if failed_tests == 0 else 1

async def main():
    tester = EndpointTester()
    await tester.run_all_tests()
    return tester.print_summary()

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}")
        sys.exit(1)
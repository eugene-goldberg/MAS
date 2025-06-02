from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
import asyncio

from app.api.dependencies import get_mas_service, get_session_service, get_tracking_service
from app.services.mas_service import MASService
from app.services.session_service import SessionService
from app.services.tracking_service import TrackingService
from app.models.chat import ChatRequest

router = APIRouter()

# Test scenarios for each agent
TEST_SCENARIOS = {
    "greeter": [
        {"message": "Hello!", "expected_agent": "Greeter Agent"},
        {"message": "Good morning", "expected_agent": "Greeter Agent"},
        {"message": "Goodbye", "expected_agent": "Greeter Agent"}
    ],
    "weather": [
        {"message": "What's the weather in London?", "expected_agent": "Weather Agent"},
        {"message": "Give me a 5-day forecast for New York", "expected_agent": "Weather Agent"},
        {"message": "What's the temperature in Tokyo?", "expected_agent": "Weather Agent"}
    ],
    "rag": [
        {"message": "List my document collections", "expected_agent": "RAG Agent"},
        {"message": "Create a new corpus called test-corpus", "expected_agent": "RAG Agent"},
        {"message": "Search for information about machine learning", "expected_agent": "RAG Agent"}
    ],
    "academic": [
        {"message": "Find papers on transformers", "expected_agent": "Academic"},
        {"message": "Search for recent AI research", "expected_agent": "Academic"},
        {"message": "What are the latest developments in NLP?", "expected_agent": "Academic"}
    ]
}

@router.get("/scenarios")
async def get_test_scenarios() -> Dict[str, List[Dict[str, str]]]:
    """Get all available test scenarios"""
    return TEST_SCENARIOS

@router.post("/run/{agent_type}")
async def run_agent_test(
    agent_type: str,
    mas_service: MASService = Depends(get_mas_service),
    session_service: SessionService = Depends(get_session_service)
) -> Dict[str, Any]:
    """Run all test scenarios for a specific agent type"""
    if agent_type not in TEST_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Unknown agent type: {agent_type}")
    
    scenarios = TEST_SCENARIOS[agent_type]
    results = []
    session_id = "test-session"
    
    for scenario in scenarios:
        try:
            response, execution_trace = await mas_service.process_message(
                scenario["message"],
                session_id
            )
            
            # Check if expected agent was used
            agents_used = execution_trace.agent_sequence
            success = any(scenario["expected_agent"] in agent for agent in agents_used)
            
            results.append({
                "message": scenario["message"],
                "success": success,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "agents_used": agents_used,
                "execution_time_ms": execution_trace.total_time_ms,
                "expected_agent": scenario["expected_agent"]
            })
            
        except Exception as e:
            results.append({
                "message": scenario["message"],
                "success": False,
                "error": str(e),
                "expected_agent": scenario["expected_agent"]
            })
    
    # Calculate summary
    success_count = sum(1 for r in results if r.get("success", False))
    
    return {
        "agent_type": agent_type,
        "total_tests": len(scenarios),
        "passed": success_count,
        "failed": len(scenarios) - success_count,
        "success_rate": (success_count / len(scenarios)) * 100 if scenarios else 0,
        "results": results
    }

@router.post("/run-all")
async def run_all_tests(
    mas_service: MASService = Depends(get_mas_service),
    session_service: SessionService = Depends(get_session_service)
) -> Dict[str, Any]:
    """Run all test scenarios for all agents"""
    all_results = {}
    
    for agent_type in TEST_SCENARIOS:
        result = await run_agent_test(agent_type, mas_service, session_service)
        all_results[agent_type] = result
    
    # Calculate overall summary
    total_tests = sum(r["total_tests"] for r in all_results.values())
    total_passed = sum(r["passed"] for r in all_results.values())
    
    return {
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "overall_success_rate": (total_passed / total_tests) * 100 if total_tests > 0 else 0
        },
        "agent_results": all_results
    }

@router.post("/validate-tools")
async def validate_tools(
    mas_service: MASService = Depends(get_mas_service)
) -> Dict[str, Any]:
    """Validate that all expected tools are available"""
    agent_info = await mas_service.get_agent_info()
    
    expected_tools = {
        "Weather Agent": ["get_current_weather", "get_weather_forecast", "get_random_lucky_number", "get_random_temperature_adjustment"],
        "RAG Agent": ["create_corpus", "list_corpora", "add_data", "rag_query", "get_corpus_info", "delete_document", "delete_corpus"],
        "Academic WebSearch": ["google_search"],
        "Academic NewResearch": [],
        "Greeter Agent": []
    }
    
    validation_results = []
    
    for agent in agent_info["agents"]:
        agent_name = agent["name"]
        actual_tools = set(agent["tools"])
        expected = set(expected_tools.get(agent_name, []))
        
        validation_results.append({
            "agent": agent_name,
            "valid": actual_tools == expected,
            "expected_tools": list(expected),
            "actual_tools": list(actual_tools),
            "missing_tools": list(expected - actual_tools),
            "extra_tools": list(actual_tools - expected)
        })
    
    all_valid = all(r["valid"] for r in validation_results)
    
    return {
        "all_tools_valid": all_valid,
        "validation_results": validation_results
    }

@router.post("/performance-test")
async def run_performance_test(
    iterations: int = 5,
    mas_service: MASService = Depends(get_mas_service)
) -> Dict[str, Any]:
    """Run performance tests to measure response times"""
    test_messages = [
        "Hello!",
        "What's the weather in Paris?",
        "List my document collections"
    ]
    
    results = []
    
    for message in test_messages:
        times = []
        
        for i in range(iterations):
            try:
                import time
                start = time.time()
                response, execution_trace = await mas_service.process_message(
                    message,
                    f"perf-test-{i}"
                )
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"Error in performance test: {e}")
        
        if times:
            results.append({
                "message": message,
                "iterations": len(times),
                "avg_time_ms": sum(times) / len(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "times": times
            })
    
    return {
        "performance_results": results,
        "overall_avg_ms": sum(r["avg_time_ms"] for r in results) / len(results) if results else 0
    }

@router.get("/health-check")
async def comprehensive_health_check(
    mas_service: MASService = Depends(get_mas_service),
    session_service: SessionService = Depends(get_session_service),
    tracking_service: TrackingService = Depends(get_tracking_service)
) -> Dict[str, Any]:
    """Comprehensive health check of all systems"""
    
    # Check MAS connection
    mas_connected = await mas_service.check_connection()
    
    # Check agent availability
    try:
        agent_info = await mas_service.get_agent_info()
        agents_available = len(agent_info.get("agents", [])) > 0
    except:
        agents_available = False
    
    # Check session service
    try:
        sessions = await session_service.list_active_sessions()
        session_service_ok = True
    except:
        session_service_ok = False
    
    # Test simple message
    test_message_ok = False
    try:
        response, _ = await mas_service.process_message("test", "health-check")
        test_message_ok = True
    except:
        pass
    
    all_healthy = all([
        mas_connected,
        agents_available,
        session_service_ok,
        test_message_ok
    ])
    
    return {
        "overall_health": "healthy" if all_healthy else "unhealthy",
        "components": {
            "mas_connection": mas_connected,
            "agents_available": agents_available,
            "session_service": session_service_ok,
            "message_processing": test_message_ok
        },
        "agent_count": len(agent_info.get("agents", [])) if agents_available else 0
    }
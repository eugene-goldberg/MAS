from typing import Dict, List, Callable, Optional, Any
import functools
import time
import asyncio
from datetime import datetime
import inspect

from app.models.agent import AgentResponse, ToolCall

class TrackingInterceptor:
    """Intercepts and tracks agent and tool execution"""
    
    def __init__(self):
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        
    def start_request(self, request_id: str, session_id: str):
        """Initialize tracking for a new request"""
        self.active_requests[request_id] = {
            "session_id": session_id,
            "agent_responses": [],
            "agent_sequence": [],
            "current_agent": None,
            "tool_calls": []
        }
        
    def end_request(self, request_id: str):
        """Cleanup tracking for completed request"""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
            
    def get_responses(self, request_id: str) -> List[AgentResponse]:
        """Get all agent responses for a request"""
        if request_id in self.active_requests:
            return self.active_requests[request_id]["agent_responses"]
        return []
        
    def get_agent_sequence(self, request_id: str) -> List[str]:
        """Get the sequence of agents called"""
        if request_id in self.active_requests:
            return self.active_requests[request_id]["agent_sequence"]
        return []
        
    def wrap_coordinator(self, coordinator, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap the MAS coordinator to track agent calls"""
        
        class TrackedCoordinator:
            def __init__(self, original_coordinator, interceptor, req_id, ws_callback):
                self.coordinator = original_coordinator
                self.interceptor = interceptor
                self.request_id = req_id
                self.websocket_callback = ws_callback
                
            async def run_async(self, context):
                # Track the coordinator processing
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "coordinator_start",
                        "message": context.input if hasattr(context, 'input') else str(context),
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Intercept sub-agent calls
                # This would require patching the coordinator's tool calls
                # For now, we'll simulate tracking
                async for event in self.coordinator.run_async(context):
                    yield event
                
        return TrackedCoordinator(coordinator, self, request_id, websocket_callback)
        
    def wrap_agent(self, agent, agent_name: str, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap an agent to track its execution"""
        
        class TrackedAgent:
            def __init__(self, original_agent, interceptor, name, req_id, ws_callback):
                self.agent = original_agent
                self.interceptor = interceptor
                self.agent_name = name
                self.request_id = req_id
                self.websocket_callback = ws_callback
                
            async def process(self, message: str) -> str:
                # Record agent start
                start_time = time.time()
                
                if self.request_id in self.interceptor.active_requests:
                    self.interceptor.active_requests[self.request_id]["current_agent"] = self.agent_name
                    self.interceptor.active_requests[self.request_id]["agent_sequence"].append(self.agent_name)
                
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "agent_start",
                        "agent": self.agent_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Wrap agent tools
                wrapped_tools = self._wrap_agent_tools()
                
                # Execute agent
                response = await self.agent.process(message)
                
                # Record agent completion
                duration = (time.time() - start_time) * 1000
                
                # Get tool calls for this agent
                agent_tool_calls = []
                if self.request_id in self.interceptor.active_requests:
                    all_tool_calls = self.interceptor.active_requests[self.request_id]["tool_calls"]
                    agent_tool_calls = [tc for tc in all_tool_calls if tc.get("agent") == self.agent_name]
                
                # Create agent response
                agent_response = AgentResponse(
                    agent_name=self.agent_name,
                    agent_type=self.agent.__class__.__name__,
                    response=response,
                    tools_used=[self._convert_tool_call(tc) for tc in agent_tool_calls],
                    processing_time_ms=duration,
                    timestamp=datetime.now()
                )
                
                if self.request_id in self.interceptor.active_requests:
                    self.interceptor.active_requests[self.request_id]["agent_responses"].append(agent_response)
                
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "agent_complete",
                        "agent": self.agent_name,
                        "duration_ms": duration,
                        "response_preview": response[:100] + "..." if len(response) > 100 else response,
                        "timestamp": datetime.now().isoformat()
                    })
                
                return response
                
            def _wrap_agent_tools(self):
                """Wrap all tools of the agent"""
                # This would wrap each tool function
                # Implementation depends on how tools are attached to agents
                pass
                
            def _convert_tool_call(self, tool_call_data: Dict) -> ToolCall:
                """Convert tracked tool call data to ToolCall model"""
                return ToolCall(
                    tool_name=tool_call_data["tool_name"],
                    tool_type=tool_call_data["tool_type"],
                    parameters=tool_call_data["parameters"],
                    result=tool_call_data["result"],
                    duration_ms=tool_call_data["duration_ms"],
                    timestamp=tool_call_data["timestamp"]
                )
                
        return TrackedAgent(agent, self, agent_name, request_id, websocket_callback)
        
    def wrap_tool(self, tool_func: Callable, tool_name: str, agent_name: str, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap a tool function to track its execution"""
        
        @functools.wraps(tool_func)
        async def wrapped_tool(*args, **kwargs):
            start_time = time.time()
            
            # Notify tool start
            if websocket_callback:
                await websocket_callback({
                    "type": "tool_start",
                    "agent": agent_name,
                    "tool": tool_name,
                    "parameters": self._serialize_parameters(kwargs),
                    "timestamp": datetime.now().isoformat()
                })
            
            try:
                # Execute tool
                if inspect.iscoroutinefunction(tool_func):
                    result = await tool_func(*args, **kwargs)
                else:
                    result = tool_func(*args, **kwargs)
                
                duration = (time.time() - start_time) * 1000
                
                # Record tool call
                tool_call_data = {
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "tool_type": "function",
                    "parameters": kwargs,
                    "result": result,
                    "duration_ms": duration,
                    "timestamp": datetime.now(),
                    "success": True
                }
                
                if request_id in self.active_requests:
                    self.active_requests[request_id]["tool_calls"].append(tool_call_data)
                
                # Notify tool completion
                if websocket_callback:
                    await websocket_callback({
                        "type": "tool_complete",
                        "agent": agent_name,
                        "tool": tool_name,
                        "duration_ms": duration,
                        "success": True,
                        "result_preview": self._preview_result(result),
                        "timestamp": datetime.now().isoformat()
                    })
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Record failed tool call
                tool_call_data = {
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "tool_type": "function",
                    "parameters": kwargs,
                    "result": {"error": str(e)},
                    "duration_ms": duration,
                    "timestamp": datetime.now(),
                    "success": False
                }
                
                if request_id in self.active_requests:
                    self.active_requests[request_id]["tool_calls"].append(tool_call_data)
                
                # Notify tool error
                if websocket_callback:
                    await websocket_callback({
                        "type": "tool_error",
                        "agent": agent_name,
                        "tool": tool_name,
                        "duration_ms": duration,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                
                raise
                
        return wrapped_tool
        
    def _serialize_parameters(self, params: Dict) -> Dict:
        """Serialize parameters for transmission"""
        # Convert complex objects to strings
        serialized = {}
        for key, value in params.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                serialized[key] = value
            else:
                serialized[key] = str(value)
        return serialized
        
    def _preview_result(self, result: Any) -> str:
        """Create a preview of the result"""
        if isinstance(result, dict):
            return f"Dict with {len(result)} keys"
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        elif isinstance(result, str):
            return result[:100] + "..." if len(result) > 100 else result
        else:
            return str(result)[:100]
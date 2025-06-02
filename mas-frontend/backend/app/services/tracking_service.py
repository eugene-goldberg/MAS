from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.agent import AgentResponse
from app.models.tracking import ExecutionTrace

class TrackingService:
    """Service for tracking and analyzing agent execution metrics"""
    
    def __init__(self):
        self.execution_history: List[ExecutionTrace] = []
        self.agent_metrics: Dict[str, Dict] = defaultdict(lambda: {
            "total_calls": 0,
            "total_time_ms": 0,
            "tool_usage": defaultdict(int),
            "error_count": 0
        })
        
    async def add_execution(self, trace: ExecutionTrace):
        """Add execution trace and update metrics"""
        self.execution_history.append(trace)
        
        # Update metrics for each agent
        for agent_response in trace.agent_responses:
            agent_name = agent_response.agent_name
            metrics = self.agent_metrics[agent_name]
            
            metrics["total_calls"] += 1
            metrics["total_time_ms"] += agent_response.processing_time_ms
            
            # Track tool usage
            for tool in agent_response.tools_used:
                metrics["tool_usage"][tool.tool_name] += 1
                if not tool.success:
                    metrics["error_count"] += 1
                    
    async def get_agent_metrics(self) -> Dict[str, Dict]:
        """Get metrics for all agents"""
        result = {}
        
        for agent_name, metrics in self.agent_metrics.items():
            avg_time = (
                metrics["total_time_ms"] / metrics["total_calls"] 
                if metrics["total_calls"] > 0 else 0
            )
            
            result[agent_name] = {
                "total_calls": metrics["total_calls"],
                "avg_response_time_ms": avg_time,
                "total_time_ms": metrics["total_time_ms"],
                "tool_usage": dict(metrics["tool_usage"]),
                "error_count": metrics["error_count"],
                "error_rate": (
                    metrics["error_count"] / metrics["total_calls"] 
                    if metrics["total_calls"] > 0 else 0
                )
            }
            
        return result
        
    async def get_recent_executions(
        self, 
        limit: int = 10,
        agent_filter: Optional[str] = None
    ) -> List[ExecutionTrace]:
        """Get recent execution traces"""
        executions = self.execution_history[-limit:]
        
        if agent_filter:
            executions = [
                exec for exec in executions
                if any(agent_filter in resp.agent_name for resp in exec.agent_responses)
            ]
            
        return executions
        
    async def get_execution_by_id(self, request_id: str) -> Optional[ExecutionTrace]:
        """Get specific execution trace by request ID"""
        for execution in self.execution_history:
            if execution.request_id == request_id:
                return execution
        return None
        
    async def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get overall tool usage statistics"""
        tool_stats = defaultdict(int)
        
        for agent_metrics in self.agent_metrics.values():
            for tool_name, count in agent_metrics["tool_usage"].items():
                tool_stats[tool_name] += count
                
        return dict(tool_stats)
        
    async def clear_old_data(self, days: int = 7):
        """Clear execution history older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        self.execution_history = [
            exec for exec in self.execution_history
            if exec.timestamp > cutoff_time
        ]
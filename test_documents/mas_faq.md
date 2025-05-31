# Multi-Agent System (MAS) Frequently Asked Questions

## General Questions

### Q: What is a Multi-Agent System (MAS)?

A: A Multi-Agent System is an architectural pattern where multiple specialized AI agents work together to handle complex tasks. In the context of Google ADK, MAS uses a coordinator agent to route requests to appropriate sub-agents based on the nature of the query.

### Q: Why use MAS instead of a single agent?

A: MAS offers several advantages:
- **Specialization**: Each agent can be optimized for specific tasks
- **Modularity**: Agents can be developed, tested, and deployed independently  
- **Scalability**: New agents can be added without modifying existing ones
- **Maintainability**: Easier to debug and update individual components

### Q: How do agents communicate in MAS?

A: Agents communicate through the coordinator using structured messages. The coordinator receives user requests, determines which sub-agent should handle it, forwards the request, and returns the response to the user.

## Technical Questions

### Q: What's the difference between Agent and LlmAgent?

A: 
- **Agent**: Base class for agents with tools and custom logic
- **LlmAgent**: Specialized for agents that primarily use language models for reasoning and don't need custom tools

Example:
```python
# Use Agent when you have custom tools
weather_agent = Agent(
    name="weather_agent",
    tools=[FunctionTool(func=get_weather)]
)

# Use LlmAgent for the coordinator
coordinator = LlmAgent(
    name="coordinator",
    tools=[AgentTool(agent=weather_agent)]
)
```

### Q: Why must tools return dictionaries?

A: When using `AgentTool` to wrap sub-agents, the framework expects structured data (dictionaries) to properly serialize and pass information between agents. String returns don't provide enough structure for the framework to handle the response correctly.

### Q: How do I handle state in MAS?

A: Use ToolContext for session-level state:
```python
def stateful_tool(data: str, tool_context: ToolContext = None) -> dict:
    if tool_context:
        # Store state
        tool_context.state["last_query"] = data
        # Retrieve state
        history = tool_context.state.get("history", [])
```

## Common Issues

### Q: My sub-agent responses aren't showing up. What's wrong?

A: Check these common causes:
1. **Tool returns strings instead of dictionaries** - All tools must return dicts
2. **Missing AgentTool wrapper** - Sub-agents must be wrapped with AgentTool
3. **Incorrect prompt** - Coordinator prompt must clearly specify when to use each agent

### Q: How do I debug routing issues?

A: 
1. Add logging to your coordinator prompt
2. Test each sub-agent independently first
3. Use explicit routing rules in the coordinator prompt
4. Check that agent names match between prompt and implementation

### Q: Can I use async operations in MAS?

A: Yes! ADK supports async operations:
```python
async def async_tool(query: str) -> dict:
    result = await async_operation(query)
    return {"status": "success", "data": result}
```

## Best Practices

### Q: How should I structure my MAS project?

A: Recommended structure:
```
mas_system/
├── __init__.py
├── agent.py          # Coordinator definition
├── prompt.py         # Coordinator prompt
└── sub_agents/
    ├── weather_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   ├── prompt.py
    │   └── tools.py
    └── rag_agent/
        ├── __init__.py
        ├── agent.py
        ├── prompt.py
        └── tools/
```

### Q: How do I test MAS effectively?

A: Test at three levels:
1. **Unit tests**: Test individual tool functions
2. **Integration tests**: Test sub-agents in isolation
3. **End-to-end tests**: Test full MAS workflow

### Q: What's the best way to handle errors?

A: Implement error handling at each level:
```python
# Tool level
def safe_tool(param: str) -> dict:
    try:
        result = risky_operation(param)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Agent level - handled by coordinator
# Coordinator level - graceful fallbacks
```

## Performance and Scaling

### Q: How many sub-agents can I have?

A: There's no hard limit, but consider:
- Each agent adds initialization overhead
- Too many agents can make routing complex
- Group related functionality into single agents
- Typically 5-10 sub-agents work well

### Q: How do I optimize MAS performance?

A: Key optimization strategies:
1. **Lazy loading**: Initialize agents only when needed
2. **Caching**: Cache frequently used agent responses
3. **Parallel execution**: Run independent agent calls in parallel
4. **Model selection**: Use lighter models for simple agents

### Q: Can I deploy agents separately?

A: Yes! Agents can be deployed as separate services:
- Deploy high-traffic agents independently
- Use different resources for different agents
- Update agents without full system redeploy

## RAG Integration

### Q: How do I add document search to MAS?

A: Create a RAG agent as a sub-agent:
1. Create a Vertex AI RAG corpus
2. Implement RAG tools (create_corpus, add_documents, search)
3. Add the RAG agent to your coordinator
4. Update coordinator prompt to route document queries

### Q: What file formats does RAG support?

A: Vertex AI RAG supports:
- PDF files
- Text files
- Google Cloud Storage files
- Local files (must be uploaded)

Note: Direct Google Drive uploads are not supported through the API.

### Q: How do I handle large document collections?

A: Best practices for large collections:
1. Use meaningful corpus names and organization
2. Implement document metadata for better search
3. Set appropriate chunk sizes for your content
4. Monitor corpus size and query performance

## Deployment

### Q: How do I deploy MAS to production?

A: Steps for deployment:
1. Build the agent package
2. Deploy to Vertex AI Agent Builder
3. Test with the deployment test script
4. Monitor performance and errors

```bash
cd deployment
python3 deploy.py --build --deploy
```

### Q: How do I update a deployed MAS?

A: To update:
1. Make changes to your agents
2. Test locally
3. Rebuild and redeploy
4. Verify with deployment tests

### Q: What monitoring should I implement?

A: Essential monitoring:
- Request routing accuracy
- Sub-agent response times  
- Error rates by agent
- Token usage per agent
- User satisfaction metrics

## Future Enhancements

### Q: Can I add new agents dynamically?

A: While not built-in, you can implement dynamic agent loading:
```python
def add_agent_dynamically(coordinator, new_agent):
    coordinator.tools.append(AgentTool(agent=new_agent))
    # Update coordinator prompt
```

### Q: Will MAS support other LLM providers?

A: Currently, MAS works with Google's models through ADK. The architecture is flexible enough to support other providers with appropriate adapters.

### Q: Can agents communicate directly without the coordinator?

A: The current architecture routes all communication through the coordinator. Direct agent-to-agent communication could be implemented but would require careful design to maintain system coherence.

## Getting Help

### Q: Where can I find more examples?

A: Resources for learning:
- Google ADK documentation
- Example agents in the ADK samples repository
- MAS implementation guide
- Community forums and discussions

### Q: How do I report issues or contribute?

A: 
- Report issues on the GitHub repository
- Submit pull requests for improvements
- Share your agent implementations with the community
- Participate in discussions and forums

### Q: What's the roadmap for MAS?

A: Future directions include:
- Enhanced state management
- Better debugging tools
- Performance optimizations
- Extended agent marketplace
- Improved deployment options
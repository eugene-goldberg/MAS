# Multi-Agent System (MAS) Documentation

## Overview

The Multi-Agent System (MAS) is a coordinator-based architecture that routes user requests to specialized sub-agents. It demonstrates the hub-and-spoke pattern for multi-agent systems using Google's Agent Development Kit (ADK).

## Architecture

### Coordinator Agent
- **Name**: `mas_coordinator`
- **Model**: `gemini-2.0-flash-001`
- **Role**: Routes requests to appropriate sub-agents based on query type
- **Implementation**: Uses `LlmAgent` with `AgentTool` wrappers for sub-agents

### Sub-Agents

1. **Weather Agent**
   - Handles weather-related queries
   - Returns weather information as dictionaries
   - Has custom tools for weather data

2. **Greeter Agent**
   - Handles greetings, welcomes, and farewells
   - No custom tools (pure LLM responses)

3. **Academic WebSearch Agent**
   - Searches for academic papers citing a seminal work
   - Requires specific seminal paper context
   - Part of academic research workflow

4. **Academic NewResearch Agent**
   - Suggests future research directions
   - Requires seminal paper and recent citations as input
   - Part of academic research workflow

5. **RAG Agent**
   - Manages document collections using Vertex AI RAG
   - Supports semantic search across uploaded documents
   - Tools: create_corpus, list_corpora, add_data, rag_query, get_corpus_info, delete_document, delete_corpus

## Key Implementation Details

### Agent Tool Pattern
All sub-agents are wrapped with `AgentTool` to make them available to the coordinator:
```python
tools=[
    AgentTool(agent=weather_agent),
    AgentTool(agent=greeter_agent),
    AgentTool(agent=academic_newresearch_agent),
    AgentTool(agent=academic_websearch_agent),
    AgentTool(agent=rag_agent),
]
```

### Important Discovery
- Sub-agent tools must return dictionaries, not strings, when used with `AgentTool`
- String-returning tools don't properly surface results through the coordinator
- This was discovered when the calculator agent (now removed) failed to return results

## Academic Research Agents

The academic agents were copied from the `academic-research` project and are designed for a specific workflow:

1. A seminal paper is analyzed first
2. Recent citing papers are found using `academic_websearch_agent`
3. Future research directions are suggested using `academic_newresearch_agent`

### Coordinator Prompting
The coordinator includes specific instructions for academic queries:
- For general academic searches: Directs users to dedicated academic search tools
- For seminal paper analysis: Recommends using the standalone Academic Research Agent
- Prevents misuse of these specialized agents for general queries

## Deployment

### Build and Deploy
```bash
cd /Users/eugene/dev/ai/google/adk-samples/python/agents/MAS
source venv/bin/activate
cd deployment
python3 deploy.py --build --deploy
```

### Test Deployment
```bash
python3 test_deployment.py --resource_id <RESOURCE_ID> --user_id test_user
```

### List Deployed Agents
```bash
python3 deploy.py --list
```

### Delete Agent
```bash
python3 delete_agent.py --resource_id <RESOURCE_ID>
```

## Current Deployment

As of the last deployment:
- **Resource ID**: 4901227012439408640
- **Status**: Successfully deployed and tested
- **Includes**: Weather, Greeter, Academic WebSearch, Academic NewResearch, and RAG agents

## Testing Results

All agents tested successfully:
1. Greeter: "Hello! How are you today?" → Warm welcome response
2. Weather: "What's the weather in San Francisco?" → Detailed weather data
3. Academic: "Find papers on transformers" → Correctly explains need for seminal paper context
4. Greeter: "goodbye" → Farewell message

## Project Structure

```
MAS/
├── mas_system/
│   ├── __init__.py
│   ├── agent.py (coordinator configuration)
│   ├── prompt.py (coordinator instructions)
│   └── sub_agents/
│       ├── weather_agent/
│       ├── greeter_agent/
│       ├── academic_websearch/
│       ├── academic_newresearch/
│       └── rag_agent/
│           ├── agent.py
│           ├── config.py
│           ├── prompt.py
│           ├── utils.py
│           └── tools/
│               ├── create_corpus.py
│               ├── list_corpora.py
│               ├── add_data.py
│               ├── rag_query.py
│               ├── get_corpus_info.py
│               ├── delete_document.py
│               └── delete_corpus.py
├── deployment/
│   ├── deploy.py
│   ├── delete_agent.py
│   └── test_deployment.py
├── pyproject.toml
├── RAG_AGENT_INTEGRATION_PLAN.md
└── CLAUDE.md (this file)
```

## Removed Components

### Calculator Agent
- **Reason for Removal**: Tools returned strings instead of dictionaries
- **Issue**: String results weren't properly surfaced through AgentTool wrapper
- **Attempts Made**:
  - Created dictionary-returning wrapper tools
  - Modified prompts
  - Changed from Agent to LlmAgent
  - None resolved the core issue

## Best Practices Learned

1. **Tool Return Types**: When using `AgentTool`, ensure sub-agent tools return dictionaries
2. **Prompting**: Be explicit about when to use each sub-agent in coordinator instructions
3. **Academic Agents**: Specialized agents may require specific workflows and contexts
4. **Testing**: Always test through the coordinator, not just individual agents

## Environment Variables Required

```
GOOGLE_CLOUD_PROJECT=<your-project-id>
GOOGLE_CLOUD_LOCATION=<your-location>
GOOGLE_CLOUD_STORAGE_BUCKET=<your-bucket>
```

## Future Considerations

1. The academic agents could be enhanced to work more independently
2. Additional sub-agents can be added following the same pattern
3. Consider implementing a more sophisticated routing mechanism
4. Tool return type validation could prevent issues like the calculator agent problem
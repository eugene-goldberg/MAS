# MAS (Multi-Agent System) Architecture Visualization

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MAS COORDINATOR                                 │
│                          (gemini-2.0-flash-001)                             │
│                                                                             │
│  Routes user requests to specialized sub-agents based on query type        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Routes to
                                      ▼
    ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
    │              │              │              │              │              │
    ▼              ▼              ▼              ▼              ▼              │
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐           │
│ Weather │  │ Greeter │  │   RAG   │  │Academic  │  │Academic  │           │
│  Agent  │  │  Agent  │  │  Agent  │  │WebSearch │  │NewResearch│           │
└─────────┘  └─────────┘  └─────────┘  └──────────┘  └──────────┘           │
     │            │            │             │              │                  │
     │            │            │             │              │                  │
     ▼            ▼            ▼             ▼              ▼                  │
  [Tools]    [No Tools]    [7 Tools]    [No Tools]    [No Tools]              │
                                                                               │
                                                                               │
                            External Systems & Resources                       │
                                      ▼                                        │
    ┌──────────────┬──────────────┬──────────────┬──────────────┐            │
    │              │              │              │              │            │
    │  Weather API │  Vertex AI   │  Cloud       │     PDF      │            │
    │  (Open-Meteo)│     RAG      │  Storage     │   Parser     │            │
    └──────────────┴──────────────┴──────────────┴──────────────┘            │
```

## Detailed Agent Breakdown

### 1. MAS Coordinator (Hub)
```
┌─────────────────────────────────────────────────────────────┐
│                      MAS COORDINATOR                        │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Role: Central routing hub                                   │
│ Tools: 5 AgentTools (wrapping sub-agents)                  │
├─────────────────────────────────────────────────────────────┤
│ Routing Logic:                                              │
│ • Weather queries → Weather Agent                           │
│ • Greetings/farewells → Greeter Agent                      │
│ • Document/search queries → RAG Agent                       │
│ • Academic paper queries → Academic Agents                  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Weather Agent
```
┌─────────────────────────────────────────────────────────────┐
│                      WEATHER AGENT                          │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Purpose: Weather information and forecasts                  │
├─────────────────────────────────────────────────────────────┤
│ Tools (4):                                                  │
│ 1. get_current_weather(location)                           │
│    └─> Returns: temperature, conditions, humidity, wind    │
│ 2. get_weather_forecast(location, days)                    │
│    └─> Returns: multi-day forecast data                    │
│ 3. get_random_lucky_number()                               │
│    └─> Returns: random number 1-100                        │
│ 4. get_random_temperature_adjustment()                     │
│    └─> Returns: temperature variation                      │
├─────────────────────────────────────────────────────────────┤
│ External API: Open-Meteo (free weather API)                │
└─────────────────────────────────────────────────────────────┘
```

### 3. RAG Agent
```
┌─────────────────────────────────────────────────────────────┐
│                        RAG AGENT                            │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Purpose: Document management and semantic search            │
├─────────────────────────────────────────────────────────────┤
│ Tools (7):                                                  │
│ 1. create_corpus(name, description)                        │
│    └─> Creates new document collection                     │
│ 2. list_corpora()                                          │
│    └─> Lists all available corpora                         │
│ 3. add_data(corpus_name, paths)                           │
│    └─> Adds documents from GCS/local paths                 │
│ 4. rag_query(corpus_name, query)                          │
│    └─> Semantic search across documents                    │
│ 5. get_corpus_info(corpus_name)                            │
│    └─> Detailed corpus information                         │
│ 6. delete_document(corpus_name, file_id)                   │
│    └─> Remove specific document                            │
│ 7. delete_corpus(corpus_name, confirm)                     │
│    └─> Delete entire corpus                                │
├─────────────────────────────────────────────────────────────┤
│ Backend: Vertex AI RAG with Vector Search                  │
│ Embedding Model: text-embedding-005                         │
└─────────────────────────────────────────────────────────────┘
```

### 4. Academic Agents
```
┌─────────────────────────────────────────────────────────────┐
│                   ACADEMIC WEBSEARCH AGENT                  │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Purpose: Find papers citing a seminal work                  │
│ Tools: Uses Google Search (configured in prompt)            │
│ Requires: Seminal paper context in prompt                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Feeds results to
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  ACADEMIC NEWRESEARCH AGENT                 │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Purpose: Suggest future research directions                 │
│ Tools: None (pure LLM reasoning)                           │
│ Requires: Seminal paper + recent citations                  │
└─────────────────────────────────────────────────────────────┘
```

### 5. Greeter Agent
```
┌─────────────────────────────────────────────────────────────┐
│                      GREETER AGENT                          │
├─────────────────────────────────────────────────────────────┤
│ Model: gemini-2.0-flash-001                                 │
│ Purpose: Handle greetings, welcomes, and farewells         │
│ Tools: None (pure conversational responses)                │
└─────────────────────────────────────────────────────────────┘
```

## Supporting Infrastructure

### Cloud Function for RAG Ingestion
```
┌─────────────────────────────────────────────────────────────┐
│              RAG INGESTION CLOUD FUNCTION                   │
├─────────────────────────────────────────────────────────────┤
│ Trigger: File upload to GCS bucket                         │
│ Bucket: gs://mas-rag-documents-dev/                        │
│ Process:                                                    │
│   1. Detect file upload                                     │
│   2. Validate file type                                     │
│   3. Ingest to RAG corpus                                  │
│   4. Move to processed/ or failed/                         │
├─────────────────────────────────────────────────────────────┤
│ Supported Formats:                                          │
│ PDF, TXT, MD, HTML, DOCX, JSON, CSV                       │
└─────────────────────────────────────────────────────────────┘
```

### Academic Tools Library
```
┌─────────────────────────────────────────────────────────────┐
│                    ACADEMIC TOOLS                           │
├─────────────────────────────────────────────────────────────┤
│ PDF Parser:                                                 │
│ • extract_paper_info_from_pdf()                            │
│ • Extract: title, authors, abstract, year, keywords         │
│                                                             │
│ Agent Tools:                                                │
│ • analyze_seminal_paper(pdf_path)                          │
│ • prepare_paper_for_citation_search(pdf_path)              │
│ • format_citations_for_research(paper_info, citations)     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### 1. Weather Query Flow
```
User: "What's the weather in Tokyo?"
    │
    ▼
MAS Coordinator
    │ (Routes to Weather Agent)
    ▼
Weather Agent
    │ (Calls get_current_weather)
    ▼
Open-Meteo API
    │
    ▼
Response: "Tokyo: 22°C, Clear sky, Humidity: 45%..."
```

### 2. RAG Query Flow
```
User: "Search my documents for information about transformers"
    │
    ▼
MAS Coordinator
    │ (Routes to RAG Agent)
    ▼
RAG Agent
    │ (Calls rag_query)
    ▼
Vertex AI RAG
    │ (Vector search)
    ▼
Response: "Found 3 relevant chunks about transformers..."
```

### 3. Academic Research Flow
```
User: "Analyze this paper and find recent research"
    │
    ▼
Academic Tools
    │ (PDF parsing)
    ▼
Academic WebSearch Agent
    │ (Find citations)
    ▼
Academic NewResearch Agent
    │ (Analyze trends)
    ▼
Response: "Future research directions..."
```

## Key Features

### 1. Modular Architecture
- Each agent is independent
- Easy to add/remove agents
- Clear separation of concerns

### 2. Tool Integration
- 17 total tools across all agents
- Real external API integration
- State management for complex operations

### 3. Scalability
- Cloud Function for automatic processing
- Vertex AI for enterprise-scale RAG
- Concurrent agent execution

### 4. Testing
- 100% tool coverage
- Comprehensive test suite
- Mock interfaces for testing

## Deployment Status

### Currently Deployed:
- MAS Coordinator: Resource ID 4901227012439408640
- Cloud Function: rag-ingestion-function-dev
- RAG Corpus: mas-rag-corpus
- All agents active and tested

### GCP Resources:
- Project: pickuptruckapp
- Location: us-central1
- Storage: mas-rag-documents-dev
- Service Account: rag-function-sa-dev
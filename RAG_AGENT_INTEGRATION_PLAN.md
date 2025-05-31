# RAG Agent Integration Plan for MAS

## Executive Summary

This document outlines a comprehensive plan to integrate a Retrieval Augmented Generation (RAG) agent into the existing Multi-Agent System (MAS). The RAG agent will enable the MAS to answer questions based on documents stored in Google Cloud Storage or Google Drive, with capabilities for dynamic corpus management.

## 1. Architecture Overview

### 1.1 Integration Pattern
- The RAG agent will be implemented as a sub-agent following the existing MAS pattern
- It will be wrapped with `AgentTool` and made available to the MAS coordinator
- The coordinator will route document-related and knowledge queries to the RAG agent
- Vertex AI Vector Search will provide the underlying vector database infrastructure

### 1.2 Vertex AI RAG Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    MAS Coordinator                        │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                    RAG Agent                              │
├───────────────────────────────────────────────────────────┤
│  Tools: create_corpus, add_data, rag_query, etc.         │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│              Vertex AI RAG API                            │
├───────────────────────────────────────────────────────────┤
│  • Document Processing (chunking, parsing)                │
│  • Embedding Generation (text-embedding-005)              │
│  • Vector Storage & Retrieval                             │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│           Vertex AI Vector Search                         │
├───────────────────────────────────────────────────────────┤
│  • Managed vector database                                │
│  • Optimized similarity search                            │
│  • Automatic scaling & indexing                           │
└───────────────────────────────────────────────────────────┘
```

### 1.3 Component Structure
```
MAS/
├── mas_system/
│   ├── sub_agents/
│   │   ├── rag_agent/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── prompt.py
│   │   │   ├── config.py
│   │   │   ├── utils.py
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── create_corpus.py
│   │   │       ├── list_corpora.py
│   │   │       ├── add_data.py
│   │   │       ├── get_corpus_info.py
│   │   │       ├── rag_query.py
│   │   │       ├── delete_document.py
│   │   │       └── delete_corpus.py
```

## 2. Vertex AI Vector Search Provisioning

### 2.1 Prerequisites
1. **Enable Required APIs**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

2. **Create Service Account**
   ```bash
   gcloud iam service-accounts create mas-rag-agent \
     --display-name="MAS RAG Agent Service Account"
   
   # Grant necessary roles
   gcloud projects add-iam-policy-binding ${PROJECT_ID} \
     --member="serviceAccount:mas-rag-agent@${PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   
   gcloud projects add-iam-policy-binding ${PROJECT_ID} \
     --member="serviceAccount:mas-rag-agent@${PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/storage.objectUser"
   ```

### 2.2 Vector Search Configuration
Vertex AI RAG automatically provisions and manages Vector Search infrastructure when you create a RAG corpus. The system handles:
- Index creation and optimization
- Automatic scaling based on corpus size
- Query optimization and caching
- Backup and recovery

**Note**: Unlike standalone Vector Search deployments, RAG-managed Vector Search doesn't require manual index creation or endpoint deployment.

### 2.3 Corpus Configuration Options
```python
# Backend configuration for vector database
backend_config = rag.RagVectorDbConfig(
    # Optional: Specify vector database type
    # rag_managed_db uses optimized Vertex AI Vector Search
    rag_managed_db=rag.RagManagedDb()
)

# Embedding model configuration
embedding_model_config = rag.RagEmbeddingModelConfig(
    publisher_model="text-embedding-005",  # Latest embedding model
    # Optional: Fine-tuned model endpoint can be specified here
)
```

## 3. Implementation Requirements

### 3.1 Environment Configuration
- Add Vertex AI RAG-specific environment variables to `.env`:
  ```
  VERTEX_AI_RAG_ENABLED=True
  DEFAULT_EMBEDDING_MODEL=text-embedding-005
  DEFAULT_CHUNK_SIZE=1024
  DEFAULT_CHUNK_OVERLAP=100
  DEFAULT_TOP_K=5
  DEFAULT_DISTANCE_THRESHOLD=0.5
  DEFAULT_EMBEDDING_REQUESTS_PER_MIN=600
  VECTOR_SEARCH_INDEX_UPDATE_METHOD=streaming  # or batch
  VECTOR_SEARCH_DISTANCE_MEASURE=DOT_PRODUCT_DISTANCE  # or COSINE_DISTANCE
  ```

### 3.2 Dependencies
- Add to `pyproject.toml`:
  ```toml
  vertexai = "^1.46.0"
  google-cloud-storage = "^2.10.0"
  google-cloud-aiplatform = "^1.38.0"
  ```

### 3.3 GCP Permissions
Required APIs and permissions:
- Vertex AI API enabled
- Vertex AI Vector Search API enabled
- Storage Admin role for GCS bucket access
- Service account with appropriate permissions:
  - `aiplatform.ragCorpora.create`
  - `aiplatform.ragCorpora.delete`
  - `aiplatform.ragCorpora.get`
  - `aiplatform.ragCorpora.list`
  - `aiplatform.ragCorpora.query`
  - `aiplatform.ragFiles.create`
  - `aiplatform.ragFiles.delete`
  - `aiplatform.ragFiles.get`
  - `aiplatform.ragFiles.list`
  - `storage.buckets.get`
  - `storage.objects.get`
  - `storage.objects.list`

## 4. RAG Agent Capabilities

### 4.1 Core Functions
1. **Corpus Management**
   - Create new document corpora
   - List available corpora
   - Delete corpora with confirmation

2. **Document Operations**
   - Add documents from Google Drive or GCS
   - List documents in a corpus
   - Delete specific documents
   - Support for various formats (PDF, DOCX, TXT, etc.)

3. **Query Operations**
   - Semantic search across documents
   - Return relevant chunks with source attribution
   - Configurable similarity thresholds

### 4.2 Tool Return Types
Following MAS best practices, all tools will return dictionaries with standardized structure:
```python
{
    "status": "success|error|info",
    "message": "Human-readable message",
    "data": {...}  # Tool-specific data
}
```

### 4.3 Vector Search Integration Details
Each corpus created will automatically:
- Use Vertex AI's managed Vector Search infrastructure
- Create optimized indexes for similarity search
- Support up to 10M documents per corpus
- Provide sub-100ms query latency for most use cases
- Handle automatic index updates when documents are added/removed

## 5. Test Data Generation Plan

### 5.1 Test Document Categories
1. **Technical Documentation**
   - MAS architecture guide
   - ADK best practices
   - Agent development tutorials

2. **FAQ Documents**
   - Common MAS questions
   - Troubleshooting guide
   - Feature explanations

3. **Sample Business Documents**
   - Product specifications
   - Meeting notes
   - Project plans

### 5.2 Document Generation Strategy
1. Create 5-10 test documents in various formats:
   - 3 technical PDFs (auto-generated from markdown)
   - 2 Google Docs (FAQs and guides)
   - 2 text files (configuration examples)
   - 3 business documents (mixed formats)

2. Document content will include:
   - Varied vocabulary for testing semantic search
   - Cross-references between documents
   - Different document lengths (1-20 pages)
   - Tables, lists, and structured data

### 5.3 GCS Bucket Structure
```
gs://mas-rag-test-data/
├── technical/
│   ├── mas_architecture.pdf
│   ├── adk_best_practices.pdf
│   └── agent_development_guide.pdf
├── faqs/
│   ├── mas_faq.txt
│   └── troubleshooting.docx
└── business/
    ├── product_spec_v1.pdf
    ├── q4_meeting_notes.txt
    └── 2025_project_plan.docx
```

## 6. Integration with MAS Coordinator

### 6.1 Coordinator Prompt Updates
Add to the coordinator's instruction:
```
- rag_agent: Handles document-based queries, corpus management, and knowledge retrieval
  - Can search through uploaded documents
  - Manages document collections (corpora)
  - Answers questions based on document content
```

### 6.2 Request Routing Logic
The coordinator will route to RAG agent for:
- "What documents do we have?"
- "Search for information about [topic]"
- "Create a knowledge base for [subject]"
- "Add this document to [corpus]"
- "What does the document say about [topic]?"

## 7. Testing Strategy

### 7.1 Unit Tests
- Test each RAG tool individually
- Mock Vertex AI RAG API calls
- Validate return type compliance

### 7.2 Integration Tests
- Test RAG agent through MAS coordinator
- Verify proper request routing
- Test error handling and edge cases

### 7.3 End-to-End Tests
1. Create test corpus
2. Upload test documents
3. Query for specific information
4. Verify accurate retrieval
5. Test document deletion
6. Clean up test corpus

## 8. Implementation Phases

### Phase 0: Infrastructure Setup (Week 0.5)
- [ ] Enable Vertex AI and Vector Search APIs
- [ ] Create service account with proper permissions
- [ ] Configure GCS bucket for test data
- [ ] Verify Vector Search provisioning through RAG corpus creation test
- [ ] Set up monitoring for Vector Search metrics

### Phase 1: Foundation (Week 1)
- [ ] Set up RAG agent structure
- [ ] Implement basic tools (create_corpus, list_corpora)
- [ ] Create config and utils modules
- [ ] Generate initial test documents
- [ ] Test Vector Search integration with simple corpus

### Phase 2: Core Features (Week 2)
- [ ] Implement document operations (add_data, get_corpus_info)
- [ ] Implement query functionality (rag_query)
- [ ] Upload test documents to GCS
- [ ] Initial integration with MAS coordinator
- [ ] Verify Vector Search performance metrics

### Phase 3: Advanced Features (Week 3)
- [ ] Implement deletion operations (delete_document, delete_corpus)
- [ ] Add confirmation workflows
- [ ] Enhance error handling
- [ ] Implement Vector Search optimization (query caching, index tuning)
- [ ] Comprehensive testing

### Phase 4: Polish & Deploy (Week 4)
- [ ] Performance optimization for Vector Search queries
- [ ] Documentation updates including Vector Search details
- [ ] Deployment preparation with production Vector Search settings
- [ ] Final testing and validation
- [ ] Cost analysis and optimization

## 9. Monitoring and Maintenance

### 9.1 Logging
- Log all RAG operations
- Track query performance and latency
- Monitor embedding costs
- Track Vector Search metrics:
  - Query latency (p50, p90, p99)
  - Index size and growth
  - Query throughput
  - Recall accuracy

### 9.2 Cost Management
- Implement corpus size limits
- Add usage tracking for:
  - Embedding API calls
  - Vector Search queries
  - Storage costs
  - Index maintenance costs
- Provide cost estimates for operations
- Set up billing alerts for Vector Search usage

### 9.3 Security Considerations
- Validate document access permissions
- Implement user-level corpus isolation (future enhancement)
- Audit trail for document operations
- Ensure Vector Search data encryption at rest
- Configure VPC-SC for Vector Search endpoints (if required)

## 10. Future Enhancements

1. **Multi-corpus Queries**
   - Search across multiple corpora simultaneously
   - Corpus federation capabilities

2. **Document Processing**
   - Custom chunking strategies
   - Metadata extraction
   - Document summarization

3. **Advanced Search**
   - Filters by date, author, type
   - Boolean search operators
   - Relevance tuning

4. **Integration Features**
   - Direct Google Workspace integration
   - Scheduled document sync
   - Webhook notifications

## 11. Success Criteria

The RAG agent integration will be considered successful when:
1. All seven RAG tools are implemented and return proper dictionary responses
2. The agent successfully integrates with MAS coordinator
3. Test documents are searchable with >90% relevance accuracy
4. Vector Search query latency is <100ms for p90
5. All operations complete within reasonable time limits (<5s for end-to-end queries)
6. Error handling is robust and user-friendly
7. Documentation is complete and accurate
8. Vector Search infrastructure auto-scales appropriately
9. Total monthly cost is within budget (<$100 for test environment)
10. Zero data loss during corpus operations

## Appendix A: Test Document Templates

### A.1 Technical Document Template
```markdown
# [Component Name] Architecture Guide

## Overview
[Brief description of the component]

## Key Concepts
- Concept 1: [Description]
- Concept 2: [Description]

## Implementation Details
[Technical details with code examples]

## Best Practices
[List of recommendations]

## Troubleshooting
[Common issues and solutions]
```

### A.2 FAQ Document Template
```markdown
# Frequently Asked Questions

## General Questions

### Q: What is [feature]?
A: [Detailed answer]

### Q: How do I [task]?
A: [Step-by-step guide]

## Technical Questions
[Similar Q&A format]
```

### A.3 Business Document Template
```markdown
# [Document Type]: [Title]

**Date**: [Date]
**Author**: [Name]
**Version**: [Version]

## Executive Summary
[Brief overview]

## Details
[Main content]

## Action Items
- [ ] Item 1
- [ ] Item 2

## References
[Related documents]
```

## Appendix B: Vector Search Configuration Examples

### B.1 Create Corpus with Custom Vector Search Settings
```python
def create_corpus_with_vector_config(corpus_name: str):
    # Advanced vector database configuration
    backend_config = rag.RagVectorDbConfig(
        rag_managed_db=rag.RagManagedDb(
            # Optional: Specify index update method
            # "streaming" for real-time updates
            # "batch" for periodic batch updates
        )
    )
    
    # Create corpus with custom configuration
    rag_corpus = rag.create_corpus(
        display_name=corpus_name,
        rag_embedding_model_config=rag.RagEmbeddingModelConfig(
            publisher_model="text-embedding-005"
        ),
        backend_config=backend_config
    )
    return rag_corpus
```

### B.2 Query with Vector Search Optimization
```python
def optimized_rag_query(corpus_name: str, query: str, top_k: int = 5):
    # Configure retrieval with Vector Search optimization
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=top_k,
        filter=rag.Filter(
            vector_distance_threshold=0.5,  # Similarity threshold
            # Optional: Add metadata filters here
        ),
        # Optional: Enable hybrid search (keyword + vector)
        ranking=rag.Ranking(
            rank_service="vertex_ai_hybrid_ranking"
        )
    )
    
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
                # Optional: Specify specific files to search
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return response
```

## Appendix C: Sample Queries for Testing

1. "What documents are available?"
2. "Create a knowledge base for project documentation"
3. "Add this document to the project corpus: [URL]"
4. "What does the architecture guide say about sub-agents?"
5. "Search for information about error handling"
6. "Show me all documents in the technical corpus"
7. "Delete the old meeting notes from January"
8. "What are the best practices for agent development?"
9. "Find all mentions of 'coordinator' in the documentation"
10. "Remove the entire test corpus"

## Appendix D: Vector Search Monitoring Queries

### D.1 Cloud Monitoring Metrics
```yaml
# Key metrics to monitor for Vector Search
metrics:
  - name: "aiplatform.googleapis.com/prediction/online/prediction_latencies"
    display_name: "Vector Search Query Latency"
    filter: 'resource.type="aiplatform.googleapis.com/Endpoint"'
    
  - name: "aiplatform.googleapis.com/prediction/online/prediction_count"
    display_name: "Vector Search Query Count"
    filter: 'resource.type="aiplatform.googleapis.com/Endpoint"'
    
  - name: "aiplatform.googleapis.com/prediction/online/error_count"
    display_name: "Vector Search Error Rate"
    filter: 'resource.type="aiplatform.googleapis.com/Endpoint"'
```

### D.2 Cost Estimation Formula
```
Monthly Cost = (Embedding Costs) + (Vector Search Costs) + (Storage Costs)

Where:
- Embedding Costs = (Number of chunks) × (Cost per 1K embeddings)
- Vector Search Costs = (Number of queries) × (Cost per 1K queries) + (Index storage GB) × (Monthly storage rate)
- Storage Costs = (Document storage GB) × (GCS monthly rate)

Example for 1000 documents, 10K chunks, 1000 queries/day:
- Embeddings: 10K × $0.025/1K = $0.25 (one-time)
- Vector Search: 30K queries × $0.30/1K + 1GB × $0.35/GB = $9.35/month
- Storage: 1GB × $0.02/GB = $0.02/month
- Total: ~$9.62/month
```

---

This plan provides a comprehensive roadmap for integrating a RAG agent into the MAS with full Vertex AI Vector Search support, ensuring consistency with existing patterns while adding powerful document-based knowledge retrieval capabilities with enterprise-grade performance and scalability.
# GCP Resources Inventory for MAS Project

## Summary
**No duplicates found.** All resources are properly named and serve distinct purposes.

## Cloud Functions (2)
| Name | Purpose | State | Last Updated |
|------|---------|-------|--------------|
| `generate-random-number` | Random number generation function | ACTIVE | 2025-05-30 |
| `rag-ingestion-function-dev` | RAG document ingestion from GCS | ACTIVE | 2025-06-01 |

## Cloud Storage Buckets (5)
| Bucket | Purpose |
|--------|---------|
| `gcf-v2-sources-*` | Cloud Functions source storage (system) |
| `gcf-v2-uploads-*` | Cloud Functions uploads (system) |
| `mas-rag-documents-dev` | RAG document uploads for ingestion |
| `pickuptruckapp-bucket` | General project storage |
| `run-sources-*` | Cloud Run source storage (system) |

## Vertex AI RAG Corpora (1)
| Display Name | Resource Name | Purpose |
|--------------|---------------|---------|
| `mas-rag-corpus` | projects/.../ragCorpora/7991637538768945152 | Document storage for MAS agents |

## Cloud Run Services (2)
| Name | URL | Created |
|------|-----|---------|
| `generate-random-number` | https://generate-random-number-*.run.app | 2025-05-30 |
| `rag-ingestion-function-dev` | https://rag-ingestion-function-dev-*.run.app | 2025-06-01 |

*Note: Cloud Functions Gen2 automatically create Cloud Run services*

## Service Accounts (1 project-specific)
| Email | Display Name |
|-------|--------------|
| `rag-function-sa-dev@` | RAG Ingestion Function Service Account (dev) |

## Eventarc Triggers (1)
| Name | Bucket | Created |
|------|--------|---------|
| `rag-ingestion-function-dev-731067` | mas-rag-documents-dev | 2025-06-01 |

## MAS Agents
Unable to list via gcloud CLI, but based on deployment logs:
- **Resource ID**: 4901227012439408640
- **Includes**: Weather, Greeter, Academic WebSearch, Academic NewResearch, and RAG agents

## Analysis
✅ **No duplicate resources detected**

Each resource serves a specific purpose:
- Cloud Functions are uniquely named
- Only one RAG corpus exists (as intended)
- Service accounts follow naming conventions
- Buckets have distinct purposes
- No redundant triggers or services
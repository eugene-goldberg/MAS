Here's a detailed step-by-step guide to building the RAG Agent with ADK as demonstrated.
# Building Your First RAG Agent with Google's Agent Development Kit (ADK)

This guide walks you through building a Retrieval Augmented Generation (RAG) agent using Google's Agent Development Kit (ADK) and Vertex AI. This agent can answer questions about documents stored in Google Drive and allows for dynamic addition and deletion of documents and corpora.

**Video Reference:** [Original YouTube Video Link (if you have it, or just mention the source)]

## Table of Contents
1.  [Prerequisites](#prerequisites)
2.  [Conceptual Overview of the RAG Agent](#conceptual-overview-of-the-rag-agent)
3.  [Step 1: Setup Google Cloud Project (GCP)](#step-1-setup-google-cloud-project-gcp)
4.  [Step 2: Setup Local Computer (Install Google Cloud CLI)](#step-2-setup-local-computer-install-google-cloud-cli)
5.  [Step 3: Setup RAG Agent Project](#step-3-setup-rag-agent-project)
    *   [3.1. Project Structure Overview](#31-project-structure-overview)
    *   [3.2. Installation and Environment Setup](#32-installation-and-environment-setup)
    *   [3.3. Agent Definition (`agent.py`)](#33-agent-definition-agentpy)
    *   [3.4. Tool Deep Dive](#34-tool-deep-dive)
        *   [Create Corpus Tool (`create_corpus.py`)](#create-corpus-tool-create_corpuspy)
        *   [List Corpora Tool (`list_corpora.py`)](#list-corpora-tool-list_corpoapy)
        *   [Add Data Tool (`add_data.py`)](#add-data-tool-add_datapy)
        *   [Get Corpus Info Tool (`get_corpus_info.py`)](#get-corpus-info-tool-get_corpus_infopy)
        *   [RAG Query Tool (`rag_query.py`)](#rag-query-tool-rag_querypy)
        *   [Delete Document Tool (`delete_document.py`)](#delete-document-tool-delete_documentpy)
        *   [Delete Corpus Tool (`delete_corpus.py`)](#delete-corpus-tool-delete_corpuspy)
6.  [Running and Interacting with the Agent](#running-and-interacting-with-the-agent)
7.  [Conclusion](#conclusion)

---

## Prerequisites

*   A Google Cloud Platform (GCP) account with billing enabled.
*   Python 3.9+ installed on your local machine.
*   Familiarity with basic Python and command-line operations.
*   Git installed (for cloning the source code).
*   Source code for this project (available via the presenter's GitHub link, typically in the video description).

## Conceptual Overview of the RAG Agent

The RAG agent works by:
1.  **Ingesting Documents:** Taking documents (e.g., from Google Drive, Google Cloud Storage) and processing them.
2.  **Chunking:** Breaking down large documents into smaller, manageable pieces (chunks).
3.  **Embedding:** Converting these text chunks into numerical representations (vectors) using an embedding model (e.g., `text-embedding-005` from Vertex AI).
4.  **Storing in Vector Database:** Storing these embeddings in a RAG Corpus (a vector database) within Vertex AI.
5.  **Retrieval:** When a user asks a question (query):
    *   The query is also embedded into a vector.
    *   The vector database is searched for the most similar/relevant document chunks based on vector similarity (e.g., cosine similarity).
6.  **Augmentation & Generation:** The retrieved relevant chunks are provided as context to a Large Language Model (LLM, e.g., Gemini 2.5 Flash) along with the original query. The LLM then generates an answer based on this augmented context.

The ADK provides the framework for defining the agent, its tools, and the web interface for interaction.

![RAG Pipeline Diagram](https://i.imgur.com/gL5e09k.png)
*(Image recreated based on the video's whiteboard explanation around 22:00)*

---

## Step 1: Setup Google Cloud Project (GCP)

(Video Timestamp: ~4:41 - 6:10)

1.  **Navigate to Google Cloud Console:**
    *   Search for "Google Cloud" on Google.
    *   Click the link for `cloud.google.com`.
    *   Sign in or sign up for a GCP account. Make sure billing is enabled.
    *   Click "Console" in the top right corner.

2.  **Create a New Project:**
    *   In the Google Cloud Console, click the project selector dropdown (usually at the top, next to the Google Cloud logo).
    *   Click "NEW PROJECT".
    *   Enter a **Project name**, e.g., `adk-rag-yt`. The Project ID will be auto-generated (you can edit it if needed).
    *   Select your **Billing account**.
    *   Select an **Organization** and **Location** if applicable (or "No organization").
    *   Click "CREATE".

3.  **Select Your Project:**
    *   Once created, ensure your new project (e.g., `adk-rag-yt`) is selected in the project selector dropdown.

4.  **Enable Vertex AI APIs:**
    *   In the search bar at the top of the console, type "Vertex AI" and select it from the results.
    *   If it's your first time using Vertex AI in this project, you'll be prompted to enable APIs. Click "Enable all recommended APIs". This might take a few minutes.

---

## Step 2: Setup Local Computer (Install Google Cloud CLI)

(Video Timestamp: ~6:10 - 11:08)

The Google Cloud CLI (gcloud CLI) allows your local machine to interact with your GCP project.

1.  **Find Installation Instructions:**
    *   Search "install gcloud cli" on Google or use the link `https://cloud.google.com/sdk/docs/install` (often provided in the project's README).
    *   Choose the installation instructions for your operating system (e.g., Linux, macOS, Windows). The video demonstrates macOS (Apple Silicon).

2.  **Download and Extract:**
    *   Download the appropriate archive file for your OS (e.g., `google-cloud-cli-darwin-arm.tar.gz` for macOS ARM).
    *   Extract the archive. The presenter extracts it into the `Downloads` folder, resulting in a `google-cloud-sdk` directory.

3.  **Run Installation Script:**
    *   Open your terminal.
    *   Navigate into the extracted `google-cloud-sdk` directory:
        ```bash
        cd Downloads/google-cloud-sdk
        ```
    *   Run the installation script:
 древний код        ```bash
        ./install.sh
        ```

4.  **Follow Installation Prompts:**
    *   **Help improve the Google Cloud CLI?**: The presenter types `N` (No).
    *   **Modify profile to update your $PATH and enable shell command completion?**: Type `Y` (Yes).
    *   **Enter a path to an rc file to update**: Press Enter to accept the default (e.g., `~/.zshrc` for Zsh or `~/.bash_profile` for Bash).
    *   **Python 3.12 installation detected, install recommended modules?**: Type `Y` (Yes).
    *   The installer will download and install components. This may take a few minutes.
    *   **Important:** After installation, you might need to restart your terminal or source your profile file (e.g., `source ~/.zshrc`) for the changes to take effect.

5.  **Verify Installation:**
    *   In a new terminal window (or after sourcing your profile), check the gcloud version:
 древний код        ```bash
        gcloud --version
        ```
    *   This should display the installed Google Cloud SDK version.

6.  **Initialize gcloud CLI:**
    *   Run the initialization command:
 древний код        ```bash
        gcloud init
        ```
    *   **Pick configuration to use**: If prompted, type `1` to re-initialize the default configuration.
    *   **You must log in to continue. Would you like to log in (Y/n)?**: Type `Y`.
    *   A browser window will open. Choose your Google account associated with GCP and grant permissions.
    *   Back in the terminal, you'll be asked to **Pick cloud project to use**. Select the project you created in Step 1 (e.g., `adk-rag-yt`) by typing its corresponding number.
    *   **Do you want to configure a default Compute Region and Zone (Y/n)?**: Type `Y`.
    *   Select a region. The presenter chooses `us-central1` (option 9 in his list) as it's common for RAG services and supports the necessary features. You can press Enter for `Do not set default zone`.

---

## Step 3: Setup RAG Agent Project

(Video Timestamp: ~11:09 onwards)

### 3.1. Project Structure Overview

The provided source code typically has the following structure:
Use code with caution.
Markdown
adk-vertexai-rag/
├── rag_agent/
│ ├── init.py
│ ├── agent.py # Main agent definition
│ ├── config.py # Configuration settings
│ └── tools/ # Folder for individual tool logic
│ ├── init.py
│ ├── add_data.py
│ ├── create_corpus.py
│ ├── delete_corpus.py
│ ├── delete_document.py
│ ├── get_corpus_info.py
│ ├── list_corpora.py
│ └── rag_query.py
├── .env.example # Example environment file
├── .gitignore
├── README.md
└── requirements.txt # Python dependencies
### 3.2. Installation and Environment Setup

(Video Timestamp: ~13:32)

1.  **Clone the Repository (if you haven't already):**
 древний код    ```bash
    git clone [repository_url]
    cd adk-vertexai-rag
    ```

2.  **Create and Activate Virtual Environment:**
 древний код    ```bash
    python -m venv .venv
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
 древний код    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables (`.env` file):**
    (Video Timestamp: ~14:35)
    *   Create a copy of `.env.example` and name it `.env`.
    *   Edit the `.env` file with your specific GCP project details:
        ```text
        GOOGLE_CLOUD_PROJECT="your-gcp-project-id"  # e.g., "adk-rag-yt"
        GOOGLE_CLOUD_LOCATION="us-central1"         # Or your chosen region
        GOOGLE_GENAI_USE_VERTEXAI="True"
        ```
    *   The `config.py` file will load these variables. It also contains defaults for chunk size, overlap, top_k results, distance threshold, and the embedding model.

### 3.3. Agent Definition (`agent.py`)

(Video Timestamp: ~16:07)

The `agent.py` file defines the core RAG agent.

```python
from google.adk.agents import Agent
# Import all your tools
from .tools.add_data import add_data
from .tools.create_corpus import create_corpus
from .tools.delete_corpus import delete_corpus
# ... (other tool imports)

root_agent = Agent(
    name="RagAgent",
    # Using Gemini 2.5 Flash for best performance with RAG operations
    model="gemini-2.5-flash-preview-04-17", # Check for the latest stable version
    description="Vertex AI RAG Agent",
    tools=[
        rag_query,
        list_corpora,
 카메라        create_corpus,
        add_data,
        get_corpus_info,
        delete_corpus,
        delete_document,
    ],
    instruction="""
    # Vertex AI RAG Agent

    You are a helpful RAG (Retrieval Augmented Generation) agent that can interact with Vertex AI's document corpora.
    You can retrieve information from corpora, list available corpora, create new corpora, add new documents to corpora,
    get detailed information about specific corpora, delete specific documents from corpora,
    and delete entire corpora when they're no longer needed.

    ## Your Capabilities
    1.  **Query Documents**: You can answer questions by retrieving relevant information from document corpora.
    2.  **List Corpora**: You can list all available document corpora to help users understand what data is available.
    3.  **Create Corpus**: You can create new document corpora for organizing information.
    4.  **Add New Data**: You can add new documents (Google Drive URLs, etc.) to existing corpora.
    5.  **Get Corpus Info**: You can provide detailed information about a specific corpus, including file metadata and statistics.
    6.  **Delete Document**: You can delete a specific document from a corpus when it's no longer needed.
    7.  **Delete Corpus**: You can delete an entire corpus and all its associated files when it's no longer needed.

    ## How to Approach User Requests
    When a user asks a question:
    1.  First, determine if they want to manage corpora (list/create/add data/get info/delete) or query existing information.
    2.  If they're asking a knowledge question, use the `rag_query` tool to search the corpus.
    3.  If they're asking about available corpora, use the `list_corpora` tool.
    4.  If they want to create a new corpus, use the `create_corpus` tool.
    5.  If they want to add data, ensure you know which corpus to add to, then use the `add_data` tool.
    6.  If they want information about a specific corpus, use the `get_corpus_info` tool.
    7.  If they want to delete a specific document, use the `delete_document` tool with confirmation.
    8.  If they want to delete an entire corpus, use the `delete_corpus` tool with confirmation.

    ## INTERNAL: Technical Implementation Details
    This section is NOT user-facing information – don't repeat these details to users:
    - The system tracks a "current corpus" in the state. When a corpus is created or used, it becomes the current corpus.
    - For rag_query and add_data, you can provide an empty string for corpus_name to use the current corpus.
    - If no current corpus is set and an empty corpus_name is provided, the tools will prompt the user to specify one.
    - Whenever possible, use the full resource name returned by the list_corpora tool when calling other tools.
    - Using the full resource name instead of just the display name will ensure more reliable operation.
    - Do not tell users to use full resource names in your responses – just use them internally in your tool calls.

    ## Communication Guidelines
    - Be clear and concise in your responses.
    - If querying a corpus, explain which corpus you're using to answer the question.
    - If managing corpora, explain what actions you've taken.
    - When new data is added, confirm what was added and to which corpus.
    - When corpus information is displayed, organize it clearly for the user.
    - When deleting a document or corpus, always ask for confirmation before proceeding.
    - If an error occurs, explain what went wrong and suggest next steps.
    - When listing corpora, just provide the display names and basic information – don't tell users the full resource names unless they are developers debugging.

    Remember, your primary goal is to help users access and manage information through RAG capabilities efficiently and clearly.
    """
)
Use code with caution.
Key points in agent.py:
Model: gemini-2.5-flash-preview-04-17 is chosen for its balance of performance and cost-efficiency for RAG.
Tools: A list of functions (defined in the tools/ directory) that the agent can call.
Instruction: This is the system prompt that guides the agent's behavior, capabilities, and how it should interact with users and use its tools. It's crucial for effective tool use.
3.4. Tool Deep Dive
Each tool is a Python function decorated with @tool (from google.adk. súčasť). They typically take tool_context as an argument, which allows them to access and modify the agent's state.
Create Corpus Tool (create_corpus.py)
(Video Timestamp: ~20:43)
Purpose: Creates a new RAG corpus in Vertex AI.
from google.adk.tools.tool_context import ToolContext
from google.adk. súčasť import tool
from vertexai.preview import rag
import re
from ..config import DEFAULT_EMBEDDING_MODEL # Assuming config.py is one level up

@tool
def create_corpus(corpus_name: str, tool_context: ToolContext) -> dict:
    """Create a new Vertex AI RAG corpus with the specified name."""
    # ... (docstring with Args and Returns) ...

    # Clean corpus name for use as display name (Vertex AI has naming restrictions)
    display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)

    # Check if corpus already exists (using a helper from utils.py, not shown in detail in video)
    # if check_corpus_exists(display_name, tool_context):
    #     return {"status": "info", "message": f"Corpus '{display_name}' already exists." ...}

    try:
        # Configure embedding model
        embedding_model_config = rag.RagEmbeddingModelConfig(
            publisher_model=DEFAULT_EMBEDDING_MODEL
        )
        # Create the corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            rag_embedding_model_config=embedding_model_config,
            # backend_config can be used for more advanced vector DB settings
            backend_config=rag.RagVectorDbConfig()
        )

        # Update state to track corpus existence and set as current
        tool_context.state[f"corpus_exists_{display_name}"] = True
        tool_context.state["current_corpus"] = display_name # Or rag_corpus.name for full resource name

        return {
            "status": "success",
            "message": f"Successfully created corpus '{display_name}'",
            "corpus_name": rag_corpus.name, # Full resource name
            "display_name": display_name,
            "corpus_created": True,
        }
    except Exception as e:
        return {"status": "error", "message": f"Error creating corpus: {str(e)}", ...}
Use code with caution.
Python
Key rag.create_corpus() is the core Vertex AI SDK call.
List Corpora Tool (list_corpora.py)
(Video Timestamp: ~27:17)
Purpose: Lists all available RAG corpora in the current GCP project and location.
from google.adk.tools.tool_context import ToolContext
from google.adk. súčasť import tool
from vertexai.preview import rag
from typing import List, Dict, Union

@tool
def list_corpora(tool_context: ToolContext) -> dict: # Presenter initially had no args, tool_context is good practice
    """List all available Vertex AI RAG corpora."""
    # ... (docstring with Returns) ...
    try:
        corpora = rag.list_corpora() # This is the main call
        corpus_info = []
        for corpus in corpora:
            corpus_data = {
                "resource_name": corpus.name, # Full resource name
                "display_name": corpus.display_name,
                "create_time": str(corpus.create_time) if hasattr(corpus, 'create_time') else "",
                "update_time": str(corpus.update_time) if hasattr(corpus, 'update_time') else "",
            }
            corpus_info.append(corpus_data)
        return {
            "status": "success",
            "message": f"Found {len(corpus_info)} available corpora",
            "corpora": corpus_info,
        }
    except Exception as e:
        return {"status": "error", "message": f"Error listing corpora: {str(e)}", "corpora": []}
Use code with caution.
Python
Key rag.list_corpora() fetches the list.
Add Data Tool (add_data.py)
(Video Timestamp: ~29:14)
Purpose: Adds new documents (from Google Drive URLs or GCS paths) to an existing RAG corpus.
from google.adk.tools.tool_context import ToolContext
from google.adk. súčasť import tool
from vertexai.preview import rag
import re
from typing import List, Dict
from ..config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_EMBEDDING_REQUESTS_PER_MIN
# from ..utils import check_corpus_exists, get_corpus_resource_name # Assuming these helpers

@tool
def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext) -> dict:
    """Add new data sources to a Vertex AI RAG corpus."""
    # ... (docstring with Args: corpus_name, paths, supported formats, and Returns) ...

    # Check if the corpus exists
    # if not check_corpus_exists(corpus_name, tool_context):
    #     return {"status": "error", "message": f"Corpus '{corpus_name}' does not exist."}

    # Validate inputs (paths should be a list of strings)
    # ...

    validated_paths = []
    invalid_paths = []
    conversions = [] # To track URL conversions

    # Pre-process paths to validate and convert Google Docs/Slides URLs if needed
    for path in paths:
        # ... (logic to check if path is string) ...
        # Check for Google Docs/Sheets/Slides URLs and convert them to Drive format
        # Example: https://docs.google.com/document/d/{FILE_ID}/... -> https://drive.google.com/file/d/{FILE_ID}/view
        docs_match = re.match(r"https://docs\.google\.com/(?:document|spreadsheets|presentation)/d/([^/]+)/.*", path)
        drive_match = re.match(r"https://drive\.google\.com/file/d/([^/]+)/.*", path)

        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path: conversions.append({"original": path, "converted": drive_url})
        elif drive_match or path.startswith("gs://"):
            validated_paths.append(path)
        else:
            invalid_paths.append({"path": path, "reason": "Invalid format"})
            continue
    # ... (check if any valid paths remain) ...

    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name) # Helper to get full name

        # Set up chunking configuration
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP
            )
        )

        # Import files to the corpus
        import_result = rag.import_files(
            corpus_resource_name=corpus_resource_name,
            paths=validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN
        )

        # Set this as the current corpus if not already set
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        conversion_msg = ""
        if conversions:
            conversion_msg = " (Converted Google Docs URLs to Drive format)"

        return {
            "status": "success",
            "message": f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus '{corpus_name}'{conversion_msg}",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions
        }
    except Exception as e:
        return {"status": "error", "message": f"Error adding data to corpus: {str(e)}", ...}
Use code with caution.
Python
Key rag.import_files() is used. It handles chunking and embedding internally based on the transformation_config. The paths argument requires URLs in specific formats (Google Drive, Google Docs/Slides, GCS).
Get Corpus Info Tool (get_corpus_info.py)
(Video Timestamp: ~36:55)
Purpose: Retrieves detailed information about a specific RAG corpus, including its files.
# ... (imports similar to other tools) ...
@tool
def get_corpus_info(corpus_name: str, tool_context: ToolContext) -> dict:
    """Get detailed information about a specific RAG corpus, including its files."""
    # ... (docstring) ...
    # if not check_corpus_exists(corpus_name, tool_context):
    #     return {"status": "error", ...}
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        corpus_display_name = corpus_name # Default if we can't get actual display name
        # Try to get corpus details first (to get the actual display_name if different)
        # actual_corpus = rag.get_corpus(name=corpus_resource_name)
        # corpus_display_name = actual_corpus.display_name

        files = rag.list_files(corpus_resource_name) # Main call to list files
        file_details = []
        for rag_file in files:
            file_id = rag_file.name.split("/")[-1] # Extract file ID from full resource name
            file_info = {
                "file_id": file_id,
                "display_name": rag_file.display_name if hasattr(rag_file, 'display_name') else "",
                "source_uri": rag_file.gcs_uri.uris[0] if hasattr(rag_file, 'gcs_uri') and rag_file.gcs_uri.uris else (rag_file.drive_uri.resource_id if hasattr(rag_file, 'drive_uri') else ""), # Simplified
                "create_time": str(rag_file.create_time) if hasattr(rag_file, 'create_time') else "",
                "update_time": str(rag_file.update_time) if hasattr(rag_file, 'update_time') else ""
            }
            file_details.append(file_info)

        return {
            "status": "success",
            "message": f"Successfully retrieved information for corpus '{corpus_display_name}'",
            "corpus_name": corpus_resource_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details
        }
    except Exception as e:
        return {"status": "error", ...}
Use code with caution.
Python
Key rag.list_files() is used to get documents within a corpus.
RAG Query Tool (rag_query.py)
(Video Timestamp: ~39:12)
Purpose: Queries a Vertex AI RAG corpus with a user question and returns relevant information.
# ... (imports similar to other tools) ...
from ..config import DEFAULT_TOP_K, DEFAULT_DISTANCE_THRESHOLD

@tool
def rag_query(corpus_name: str, query: str, tool_context: ToolContext) -> dict:
    """Query a Vertex AI RAG corpus with a user question and return relevant information."""
    # ... (docstring) ...
    # if not check_corpus_exists(corpus_name, tool_context):
    #     return {"status": "error", ...}
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(
                vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD
            )
        )

        # Perform the query
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                    # You can also specify rag_file_ids here to query specific files
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": ctx_group.source_uri if hasattr(ctx_group, "source_uri") else "",
                    "source_name": ctx_group.source_display_name if hasattr(ctx_group, "source_display_name") else "",
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)
        # ... (handle if no results found) ...
        return {
            "status": "success",
            "message": f"Successfully queried corpus '{corpus_name}'",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results)
        }
    except Exception as e:
        return {"status": "error", ...}
Use code with caution.
Python
Key rag.retrieval_query() is the main call. top_k controls how many of the most relevant chunks are returned. vector_distance_threshold filters results based on similarity score (e.g., 0.5 means chunks must be at least 50% similar).
Delete Document Tool (delete_document.py)
(Video Timestamp: ~45:32)
Purpose: Deletes a specific document from a RAG corpus.
# ... (imports similar to other tools) ...
@tool
def delete_document(corpus_name: str, document_id: str, tool_context: ToolContext) -> dict:
    """Delete a specific document from a Vertex AI RAG corpus."""
    # ... (docstring with Args: document_id is the specific ID of the file) ...
    # if not check_corpus_exists(corpus_name, tool_context):
    #     return {"status": "error", ...}
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        # The RAG file path needs to be constructed with the corpus resource name and the document ID
        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        
        rag.delete_file(name=rag_file_path) # Main call

        return {
            "status": "success",
            "message": f"Successfully deleted document '{document_id}' from corpus '{corpus_name}'",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    except Exception as e:
        return {"status": "error", ...}
Use code with caution.
Python
Key rag.delete_file() is used. It requires the full path to the RAG file, including the corpus resource name and the document ID.
Delete Corpus Tool (delete_corpus.py)
(Video Timestamp: ~49:33)
Purpose: Deletes an entire RAG corpus.
# ... (imports similar to other tools) ...
@tool
def delete_corpus(corpus_name: str, confirm: bool, tool_context: ToolContext) -> dict:
    """Delete a Vertex AI RAG corpus when it's no longer needed. Requires confirmation."""
    # ... (docstring with Args: confirm must be True for deletion) ...
    # if not check_corpus_exists(corpus_name, tool_context):
    #     return {"status": "error", ...}
    if not confirm:
        return {"status": "error", "message": "Deletion requires explicit confirmation. Set confirm=True to delete this corpus."}
    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        rag.delete_corpus(name=corpus_resource_name) # Main call

        # Update state
        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False
        if tool_context.state.get("current_corpus") == corpus_name:
            tool_context.state["current_corpus"] = "" # Clear current corpus if it was deleted

        return {
            "status": "success",
            "message": f"Successfully deleted corpus '{corpus_name}'",
            "corpus_name": corpus_name,
        }
    except Exception as e:
        return {"status": "error", ...}
Use code with caution.
Python
Key rag.delete_corpus() is used. It requires the full resource name of the corpus.
Running and Interacting with the Agent
Ensure your virtual environment is activated and you are in the project's root directory.
Start the ADK Web Server:
древний код ```bash
adk web
Use code with caution.
Open the Web UI:
Navigate to http://localhost:8000 (or the port shown in your terminal) in your web browser.
Interact with the Agent:
You can now type messages in the chat interface.
Example interactions (as shown in the video):
"What data sources are you connected to?" (Initially, none or test_corpus).
(If test_corpus exists) "What documents do I have in that corpus?"
"I would like to create a new knowledge store called business"
"What corpora do I have?" (Should now include "business").
"I would like to add the following doc to my business corpus: [paste_google_slides_or_drive_link]"
"What docs are in the business [corpus]?"
"What do we talk about in phase 1?" (Assuming "phase 1" content is in the added doc).
"Delete the week 1 presentation" (Agent might ask for clarification on which corpus or the document ID).
"Delete the corpus business" (Agent should ask for confirmation: "Yes, delete the business corpus").
Conclusion
You have now successfully built a RAG agent using Google's Agent Development Kit and Vertex AI! This agent can manage knowledge corpora, ingest documents from Google Drive, and answer questions based on the content of those documents. This is a powerful foundation for building more sophisticated AI applications.
Remember to:
Manage Costs: Delete corpora and documents you no longer need from Vertex AI, as they incur storage costs.
Experiment: Modify the agent's instructions, add new tools, or integrate different data sources.
Security: Be mindful of document permissions if you are using Google Drive links, ensuring the service account or your user (during local dev) has access.
For further learning, explore the ADK documentation, Vertex AI RAG service details, and the presenter's Skool community or other resources.

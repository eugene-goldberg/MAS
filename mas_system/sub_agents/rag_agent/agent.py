# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""RAG Agent: Document-based knowledge retrieval using Vertex AI RAG."""

from google.adk import Agent
from google.adk.tools import FunctionTool
from . import prompt
from .tools.create_corpus import create_corpus
from .tools.list_corpora import list_corpora
from .tools.add_data import add_data
from .tools.get_corpus_info import get_corpus_info
from .tools.rag_query import rag_query
from .tools.delete_document import delete_document
from .tools.delete_corpus import delete_corpus

# Model configuration
MODEL = "gemini-2.0-flash-001"

# Create the RAG agent
rag_agent = Agent(
    model=MODEL,
    name="rag_agent",
    description=(
        "I help you manage and query document collections using Vertex AI RAG. "
        "I can create knowledge bases, add documents, search for information, "
        "and manage your document corpora."
    ),
    instruction=prompt.RAG_AGENT_PROMPT,
    tools=[
        FunctionTool(func=rag_query),
        FunctionTool(func=list_corpora),
        FunctionTool(func=create_corpus),
        FunctionTool(func=add_data),
        FunctionTool(func=get_corpus_info),
        FunctionTool(func=delete_document),
        FunctionTool(func=delete_corpus),
    ],
)
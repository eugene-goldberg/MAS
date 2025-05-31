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

"""Configuration settings for the RAG agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Vertex AI RAG settings
VERTEX_AI_RAG_ENABLED = os.getenv("VERTEX_AI_RAG_ENABLED", "True").lower() == "true"
DEFAULT_EMBEDDING_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-005")
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1024"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "100"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
DEFAULT_DISTANCE_THRESHOLD = float(os.getenv("DEFAULT_DISTANCE_THRESHOLD", "0.5"))
DEFAULT_EMBEDDING_REQUESTS_PER_MIN = int(os.getenv("DEFAULT_EMBEDDING_REQUESTS_PER_MIN", "600"))

# Vector Search settings
VECTOR_SEARCH_INDEX_UPDATE_METHOD = os.getenv("VECTOR_SEARCH_INDEX_UPDATE_METHOD", "streaming")
VECTOR_SEARCH_DISTANCE_MEASURE = os.getenv("VECTOR_SEARCH_DISTANCE_MEASURE", "DOT_PRODUCT_DISTANCE")

# GCP settings
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

# Corpus limits
MAX_CORPUS_SIZE_GB = 100
MAX_DOCUMENTS_PER_CORPUS = 10000
MAX_CHUNK_SIZE = 2048
MIN_CHUNK_SIZE = 256
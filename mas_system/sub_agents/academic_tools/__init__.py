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

"""Academic tools for paper analysis and formatting."""

from .pdf_parser import (
    extract_paper_info_from_pdf,
    format_for_websearch_agent,
    format_for_newresearch_agent,
    extract_text_from_pdf
)

from .helpers import (
    format_paper_for_websearch,
    format_research_context,
    get_example_paper,
    extract_paper_info_simple,
    EXAMPLE_PAPERS
)

from .agent_tools import (
    analyze_seminal_paper,
    prepare_paper_for_citation_search,
    format_citations_for_research,
    get_example_pdf_url,
    get_example_citations
)

__all__ = [
    # PDF parsing
    'extract_paper_info_from_pdf',
    'format_for_websearch_agent', 
    'format_for_newresearch_agent',
    'extract_text_from_pdf',
    # Helpers
    'format_paper_for_websearch',
    'format_research_context',
    'get_example_paper',
    'extract_paper_info_simple',
    'EXAMPLE_PAPERS',
    # Agent tools
    'analyze_seminal_paper',
    'prepare_paper_for_citation_search',
    'format_citations_for_research',
    'get_example_pdf_url',
    'get_example_citations'
]
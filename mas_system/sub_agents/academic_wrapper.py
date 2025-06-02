"""Wrapper agents for academic agents that handle context variables."""

from google.adk.agents import LlmAgent
from typing import Dict, Any

WRAPPER_MODEL = "gemini-2.0-flash-001"

# Academic WebSearch Wrapper
ACADEMIC_WEBSEARCH_WRAPPER_PROMPT = """
You are a wrapper for the academic websearch functionality. Your job is to:

1. Extract the seminal paper information from the user's query
2. Search for papers that cite this seminal work
3. Focus on recent papers (current and previous year)

When a user mentions:
- A specific paper title (e.g., "Attention Is All You Need", "Transformer paper")
- Authors (e.g., "Vaswani et al.")
- A paper from a corpus they've mentioned

You should search for academic papers that cite this work.

Provide a comprehensive list of recent papers (published in the last 2 years) that cite the seminal work.
Include paper titles, authors, publication year, venue, and brief descriptions.

If the user doesn't specify a paper clearly, ask them to clarify which seminal paper they want to search citations for.
"""

academic_websearch_wrapper = LlmAgent(
    name="academic_websearch_wrapper",
    model=WRAPPER_MODEL,
    description="Searches for recent papers citing a seminal work",
    instruction=ACADEMIC_WEBSEARCH_WRAPPER_PROMPT,
)

# Academic NewResearch Wrapper  
ACADEMIC_NEWRESEARCH_WRAPPER_PROMPT = """
You are a wrapper for suggesting future research directions. Your job is to:

1. Understand the seminal paper context from the user's query
2. Consider recent developments in the field
3. Suggest promising future research directions

When a user asks about:
- Future research directions
- Research gaps
- Promising areas to explore
- Next steps in research

Based on a seminal paper (like "Attention Is All You Need" or papers from their corpus),
provide thoughtful suggestions for future research.

Consider:
- Efficiency improvements
- Multimodal applications
- Reasoning capabilities
- Scalability challenges
- Novel architectures
- Real-world applications

Provide 5-7 concrete research directions with brief explanations of why each is promising.

If the user doesn't specify a paper or field clearly, ask them to clarify their research context.
"""

academic_newresearch_wrapper = LlmAgent(
    name="academic_newresearch_wrapper",
    model=WRAPPER_MODEL,
    description="Suggests future research directions based on seminal work",
    instruction=ACADEMIC_NEWRESEARCH_WRAPPER_PROMPT,
)
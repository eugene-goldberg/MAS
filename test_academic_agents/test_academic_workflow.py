#!/usr/bin/env python3
"""Test academic research agents with properly formatted seminal paper data."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_seminal_paper():
    """Format the seminal paper information for the academic agents."""
    return """
Title: Attention Is All You Need
Primary Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
Publication Year: 2017
DOI: 10.48550/arXiv.1706.03762

Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.

Key Contributions:
1. Introduced the Transformer architecture based solely on attention mechanisms
2. Developed multi-head self-attention mechanism
3. Eliminated need for recurrence and convolutions in sequence models
4. Achieved state-of-the-art results on machine translation benchmarks
5. Demonstrated significant training time reduction through parallelization
"""

def test_websearch_agent():
    """Test the academic websearch agent to find citing papers."""
    print("Testing Academic WebSearch Agent")
    print("=" * 60)
    
    from mas_system.sub_agents.academic_websearch import academic_websearch_agent
    from mas_system.sub_agents.academic_websearch.prompt import ACADEMIC_WEBSEARCH_PROMPT
    
    # Format the prompt with the seminal paper
    seminal_paper_info = format_seminal_paper()
    formatted_prompt = ACADEMIC_WEBSEARCH_PROMPT.replace("{seminal_paper}", seminal_paper_info)
    
    # Update agent's instruction
    academic_websearch_agent.instruction = formatted_prompt
    
    print("Agent configured with seminal paper: 'Attention Is All You Need'")
    print("\nNote: This agent uses Google Search to find citing papers.")
    print("In a real workflow, it would be invoked through the coordinator.")
    
    # The agent would typically be called through the MAS coordinator
    # For testing, we'll just show the configuration
    print("\nAgent details:")
    print(f"- Name: {academic_websearch_agent.name}")
    print(f"- Model: {academic_websearch_agent.model}")
    print(f"- Output key: {academic_websearch_agent.output_key}")
    print(f"- Tools: {[tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in academic_websearch_agent.tools]}")
    
    return seminal_paper_info

def test_newresearch_agent(seminal_paper_info, mock_citing_papers):
    """Test the academic newresearch agent with mock data."""
    print("\n\nTesting Academic NewResearch Agent")
    print("=" * 60)
    
    from mas_system.sub_agents.academic_newresearch import academic_newresearch_agent
    from mas_system.sub_agents.academic_newresearch.prompt import ACADEMIC_NEWRESEARCH_PROMPT
    
    # Format the prompt with both inputs
    formatted_prompt = ACADEMIC_NEWRESEARCH_PROMPT.replace(
        "{seminal_paper}", seminal_paper_info
    ).replace(
        "{recent_citing_papers}", mock_citing_papers
    )
    
    # Update agent's instruction
    academic_newresearch_agent.instruction = formatted_prompt
    
    print("Agent configured with:")
    print("- Seminal paper: 'Attention Is All You Need'")
    print("- Recent citing papers (mock data)")
    
    print("\nAgent details:")
    print(f"- Name: {academic_newresearch_agent.name}")
    print(f"- Model: {academic_newresearch_agent.model}")
    print(f"- No external tools (pure LLM reasoning)")

def create_mock_citing_papers():
    """Create mock citing papers for testing."""
    return """
Recent Papers (2024-2025):

1. Title: Efficient Transformers: A Survey
   Authors: Yi Tay, Mostafa Dehghani, Dara Bahri, Donald Metzler
   Year: 2024
   Source: ACM Computing Surveys
   Key Finding: Reviews efficiency improvements in Transformer architectures

2. Title: FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning
   Authors: Tri Dao
   Year: 2024
   Source: arXiv
   Key Finding: Introduces optimized attention computation reducing memory usage

3. Title: Mamba: Linear-Time Sequence Modeling with Selective State Spaces
   Authors: Albert Gu, Tri Dao
   Year: 2024
   Source: arXiv
   Key Finding: Challenges Transformer dominance with state-space models

4. Title: LongNet: Scaling Transformers to 1,000,000,000 Tokens
   Authors: Jiayu Ding, Shuming Ma, Li Dong, Xingxing Zhang, Shaohan Huang, Wenhui Wang, Furu Wei
   Year: 2024
   Source: arXiv
   Key Finding: Extends Transformer context length dramatically

5. Title: Retentive Network: A Successor to Transformer for Large Language Models
   Authors: Yutao Sun, Li Dong, Shaohan Huang, Shuming Ma, Yuqing Xia, Jilong Xue, Jianyong Wang, Furu Wei
   Year: 2024
   Source: arXiv
   Key Finding: Proposes retention mechanism as alternative to attention
"""

def main():
    """Run the academic agent tests."""
    print("Academic Research Agents Test")
    print("=" * 80)
    print("\nThese agents are designed to work in a specific workflow:")
    print("1. Analyze a seminal paper")
    print("2. Find recent papers citing it (websearch)")
    print("3. Suggest future research directions (newresearch)")
    print("\nNote: RAG is NOT suitable here - agents need structured data, not search.")
    
    # Test websearch agent
    seminal_paper_info = test_websearch_agent()
    
    # Create mock citing papers (in real use, websearch agent would provide these)
    mock_citing_papers = create_mock_citing_papers()
    
    # Test newresearch agent
    test_newresearch_agent(seminal_paper_info, mock_citing_papers)
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("\nKey findings:")
    print("1. Agents expect formatted string inputs, not raw documents")
    print("2. They work through prompt template substitution")
    print("3. The workflow requires external paper analysis (not included)")
    print("4. Full functionality requires deployment with proper coordinator")
    
    print("\nTo make these agents fully functional in MAS:")
    print("1. Add a PDF parsing tool to extract paper information")
    print("2. Update the coordinator to handle the multi-step workflow")
    print("3. Consider caching parsed paper data for efficiency")

if __name__ == "__main__":
    main()
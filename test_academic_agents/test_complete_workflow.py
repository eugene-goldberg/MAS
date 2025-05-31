#!/usr/bin/env python3
"""Test complete academic workflow with proper agent configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_academic_workflow_complete():
    """Test the complete academic workflow with proper formatting."""
    print("Complete Academic Workflow Test")
    print("=" * 80)
    
    # Import the tools
    from mas_system.sub_agents.academic_tools import (
        format_paper_for_websearch,
        format_research_context,
        get_example_paper,
        EXAMPLE_PAPERS
    )
    
    # Step 1: Get a seminal paper
    print("\nStep 1: Retrieving seminal paper information")
    print("-" * 40)
    
    paper_result = get_example_paper("transformers")
    print(f"Status: {paper_result['status']}")
    print(f"Message: {paper_result['message']}")
    print(f"\nPaper Info:\n{paper_result['data']['paper_info']}")
    
    # Step 2: Format for websearch agent
    print("\n\nStep 2: Formatting paper for citation search")
    print("-" * 40)
    
    paper_data = paper_result['data']
    websearch_result = format_paper_for_websearch(
        paper_title=paper_data['title'],
        paper_authors=paper_data['authors'],
        paper_year=paper_data['year']
    )
    print(f"Status: {websearch_result['status']}")
    print(f"Formatted paper:\n{websearch_result['data']['formatted_paper']}")
    
    # Step 3: Simulate citing papers (in real use, websearch agent would find these)
    print("\n\nStep 3: Simulating citation search results")
    print("-" * 40)
    
    mock_citations = """
Found 12 papers citing "Attention Is All You Need" from 2024-2025:

2025 Papers:
1. "Attention Mechanisms in Edge Computing" - Liu et al. (IEEE Trans. 2025)
2. "Transformer Optimization for Mobile Devices" - Park et al. (MLSys 2025)
3. "Cross-Modal Transformers for Video Understanding" - Singh et al. (CVPR 2025)

2024 Papers:
1. "Efficient Transformers: A Survey" - Tay et al. (ACM Computing Surveys 2024)
2. "FlashAttention-2: Faster Attention with Better Parallelism" - Dao (arXiv 2024)
3. "Mamba: Linear-Time Sequence Modeling" - Gu & Dao (ICLR 2024)
4. "LongNet: Scaling Transformers to 1B Tokens" - Ding et al. (arXiv 2024)
5. "Retentive Network: A Successor to Transformer" - Sun et al. (ICML 2024)
"""
    print(mock_citations)
    
    # Step 4: Format context for research suggestions
    print("\n\nStep 4: Preparing context for research direction analysis")
    print("-" * 40)
    
    research_context = format_research_context(
        seminal_paper_info=paper_result['data']['paper_info'],
        citing_papers=mock_citations
    )
    print(f"Status: {research_context['status']}")
    print(f"Message: {research_context['message']}")
    print(f"Ready for analysis: {research_context['data']['ready_for_analysis']}")
    
    # Step 5: Show how agents would be configured
    print("\n\nStep 5: Agent Configuration (for MAS coordinator)")
    print("-" * 40)
    
    print("\nTo use these agents in MAS:")
    print("1. The coordinator receives: 'Analyze the Transformers paper'")
    print("2. Coordinator recognizes academic request")
    print("3. Coordinator responds with guidance about the workflow")
    print("4. If user provides paper details, format with academic_tools")
    print("5. Configure agents with formatted data")
    print("6. Execute workflow: websearch → newresearch")
    
    # Show all available example papers
    print("\n\nAvailable Example Papers:")
    print("-" * 40)
    for key, paper in EXAMPLE_PAPERS.items():
        print(f"\n{key}:")
        print(f"  Title: {paper['title']}")
        print(f"  Year: {paper['year']}")
        print(f"  Description: {paper['description']}")
    
    print("\n" + "=" * 80)
    print("Workflow Test Complete!")
    print("\nKey Insights:")
    print("1. Academic agents need structured text input, not PDFs")
    print("2. The workflow is sequential: paper → citations → suggestions")
    print("3. Tools help format data properly for each agent")
    print("4. Real implementation would need PDF parsing capabilities")

def test_direct_agent_invocation():
    """Test direct invocation of academic agents with proper data."""
    print("\n\nDirect Agent Invocation Test")
    print("=" * 80)
    
    from mas_system.sub_agents.academic_websearch import academic_websearch_agent
    from mas_system.sub_agents.academic_newresearch import academic_newresearch_agent
    
    # Configure websearch agent
    seminal_paper = "Attention Is All You Need"
    
    print(f"\nConfiguring academic_websearch_agent for: {seminal_paper}")
    print(f"Model: {academic_websearch_agent.model}")
    print(f"Tools: Google Search")
    print(f"Output key: {academic_websearch_agent.output_key}")
    
    # Configure newresearch agent  
    print(f"\nConfiguring academic_newresearch_agent")
    print(f"Model: {academic_newresearch_agent.model}")
    print(f"Tools: None (pure reasoning)")
    
    print("\nNote: Direct invocation requires deployment or InMemoryRunner")
    print("These agents are designed to work through the MAS coordinator")

if __name__ == "__main__":
    test_academic_workflow_complete()
    test_direct_agent_invocation()
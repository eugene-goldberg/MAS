"""Tools to make academic agents functional within MAS."""

from typing import Optional

def format_paper_for_websearch(paper_title: str, paper_authors: Optional[str] = None, paper_year: Optional[str] = None) -> dict:
    """
    Format paper information for the academic websearch agent.
    
    Args:
        paper_title: Title of the seminal paper
        paper_authors: Optional authors of the paper
        paper_year: Optional publication year
        
    Returns:
        Dictionary with formatted paper info for the agent
    """
    paper_info = f"Title: {paper_title}"
    if paper_authors:
        paper_info += f"\nAuthors: {paper_authors}"
    if paper_year:
        paper_info += f"\nYear: {paper_year}"
    
    return {
        "status": "success",
        "message": f"Paper formatted for citation search: {paper_title}",
        "data": {
            "formatted_paper": paper_info,
            "paper_title": paper_title
        }
    }


def format_research_context(seminal_paper_info: str, citing_papers: str) -> dict:
    """
    Format the context for the academic newresearch agent.
    
    Args:
        seminal_paper_info: Information about the seminal paper
        citing_papers: List of recent papers citing the seminal work
        
    Returns:
        Dictionary with formatted context for research suggestions
    """
    return {
        "status": "success",
        "message": "Research context prepared for future directions analysis",
        "data": {
            "seminal_paper": seminal_paper_info,
            "citing_papers": citing_papers,
            "ready_for_analysis": True
        }
    }


def extract_paper_info_simple(paper_description: str) -> dict:
    """
    Extract basic paper information from a text description.
    
    This is a simple version that could be enhanced with PDF parsing
    or more sophisticated extraction.
    
    Args:
        paper_description: Text description of the paper
        
    Returns:
        Dictionary with extracted paper information
    """
    # Simple extraction based on common patterns
    lines = paper_description.strip().split('\n')
    
    title = None
    authors = None
    year = None
    abstract = None
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith('title:'):
            title = line.split(':', 1)[1].strip()
        elif line.lower().startswith('authors:'):
            authors = line.split(':', 1)[1].strip()
        elif line.lower().startswith('year:'):
            year = line.split(':', 1)[1].strip()
        elif line.lower().startswith('abstract:'):
            abstract = line.split(':', 1)[1].strip()
    
    if not title:
        # Try to use the first non-empty line as title
        for line in lines:
            if line.strip():
                title = line.strip()
                break
    
    return {
        "status": "success",
        "message": f"Extracted paper information{': ' + title if title else ''}",
        "data": {
            "title": title or "Unknown",
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "full_text": paper_description
        }
    }


# Example seminal papers for testing
EXAMPLE_PAPERS = {
    "transformers": {
        "title": "Attention Is All You Need",
        "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin",
        "year": "2017",
        "description": "Introduced the Transformer architecture based solely on attention mechanisms"
    },
    "bert": {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": "Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova",
        "year": "2018",
        "description": "Introduced bidirectional pre-training for language representations"
    },
    "gpt": {
        "title": "Language Models are Few-Shot Learners",
        "authors": "Tom Brown, Benjamin Mann, Nick Ryder, et al.",
        "year": "2020",
        "description": "Demonstrated that large language models can perform few-shot learning"
    }
}


def get_example_paper(paper_key: str = "transformers") -> dict:
    """
    Get an example seminal paper for testing.
    
    Args:
        paper_key: Key for the paper (transformers, bert, or gpt)
        
    Returns:
        Dictionary with paper information
    """
    if paper_key not in EXAMPLE_PAPERS:
        return {
            "status": "error",
            "message": f"Unknown paper key: {paper_key}. Available: {list(EXAMPLE_PAPERS.keys())}",
            "data": {}
        }
    
    paper = EXAMPLE_PAPERS[paper_key]
    formatted = f"Title: {paper['title']}\nAuthors: {paper['authors']}\nYear: {paper['year']}\nDescription: {paper['description']}"
    
    return {
        "status": "success",
        "message": f"Retrieved example paper: {paper['title']}",
        "data": {
            "paper_info": formatted,
            **paper
        }
    }
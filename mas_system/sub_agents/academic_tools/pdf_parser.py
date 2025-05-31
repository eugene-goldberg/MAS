"""PDF parsing tools for academic papers."""

import re
from typing import Dict, List, Optional, Tuple
import PyPDF2
from io import BytesIO
import requests


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to PDF file (local path or URL)
        
    Returns:
        Extracted text as a string
    """
    try:
        # Handle URLs
        if pdf_path.startswith(('http://', 'https://')):
            response = requests.get(pdf_path)
            response.raise_for_status()
            pdf_file = BytesIO(response.content)
        else:
            # Local file
            pdf_file = open(pdf_path, 'rb')
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        if isinstance(pdf_file, BytesIO):
            pdf_file.close()
        elif hasattr(pdf_file, 'close'):
            pdf_file.close()
            
        return text
        
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_title(text: str) -> Optional[str]:
    """Extract paper title from text."""
    lines = text.split('\n')
    
    # Common patterns for titles
    # Usually the title is in the first few lines, in a larger font
    for i, line in enumerate(lines[:20]):
        line = line.strip()
        # Skip empty lines and very short lines
        if len(line) < 10:
            continue
        # Skip lines that look like headers/footers
        if any(word in line.lower() for word in ['page', 'arxiv', 'conference', 'journal']):
            continue
        # Title is usually the first substantial line
        if len(line) > 20 and line[0].isupper():
            return line
    
    return None


def extract_authors(text: str) -> Optional[str]:
    """Extract authors from paper text."""
    lines = text.split('\n')
    
    # Look for author patterns after title
    title_found = False
    author_lines = []
    
    for i, line in enumerate(lines[:50]):
        line = line.strip()
        
        # Skip until we find something that looks like a title
        if not title_found and len(line) > 20 and line[0].isupper():
            title_found = True
            continue
            
        if title_found:
            # Author names often have specific patterns
            # Look for lines with names (capitals, commas)
            if re.search(r'[A-Z][a-z]+\s+[A-Z]', line):
                # Check if it's not abstract or introduction
                if not any(word in line.lower() for word in ['abstract', 'introduction', 'keywords']):
                    author_lines.append(line)
                else:
                    break
            # Stop if we hit abstract
            elif 'abstract' in line.lower():
                break
    
    if author_lines:
        # Join author lines and clean up
        authors = ' '.join(author_lines)
        # Remove superscripts and extra spaces
        authors = re.sub(r'\d+', '', authors)
        authors = re.sub(r'\s+', ' ', authors).strip()
        return authors
    
    return None


def extract_abstract(text: str) -> Optional[str]:
    """Extract abstract from paper text."""
    text_lower = text.lower()
    
    # Find abstract section
    abstract_start = text_lower.find('abstract')
    if abstract_start == -1:
        return None
    
    # Look for the end of abstract (usually Introduction or Keywords)
    abstract_text = text[abstract_start:]
    
    # Common section headers that follow abstract
    end_markers = ['introduction', 'keywords', '1.', '1 ', 'i. introduction']
    
    end_pos = len(abstract_text)
    for marker in end_markers:
        pos = abstract_text.lower().find(marker)
        if pos > 0 and pos < end_pos:
            end_pos = pos
    
    abstract_text = abstract_text[:end_pos]
    
    # Clean up
    abstract_text = abstract_text.replace('Abstract', '', 1)
    abstract_text = abstract_text.replace('ABSTRACT', '', 1)
    abstract_text = abstract_text.strip()
    
    # Remove very short abstracts (likely errors)
    if len(abstract_text) < 100:
        return None
        
    return abstract_text


def extract_year(text: str) -> Optional[str]:
    """Extract publication year from paper text."""
    # Look for year patterns (4 digits between 1990-2029)
    year_pattern = r'\b(199\d|20[0-2]\d)\b'
    
    # Check first few pages
    matches = re.findall(year_pattern, text[:5000])
    
    if matches:
        # Return the most recent year found
        years = [int(year) for year in matches]
        return str(max(years))
    
    return None


def extract_references(text: str) -> List[str]:
    """Extract references section from paper."""
    text_lower = text.lower()
    
    # Find references section
    ref_markers = ['references', 'bibliography', 'works cited']
    ref_start = -1
    
    for marker in ref_markers:
        pos = text_lower.rfind(marker)  # Look from the end
        if pos > len(text_lower) * 0.7:  # References usually in last 30%
            ref_start = pos
            break
    
    if ref_start == -1:
        return []
    
    references_text = text[ref_start:]
    
    # Split into individual references
    # Look for patterns like [1], 1., or similar
    ref_pattern = r'\n\s*\[?\d+\]?\.?\s+'
    refs = re.split(ref_pattern, references_text)
    
    # Clean up references
    cleaned_refs = []
    for ref in refs[1:]:  # Skip the header
        ref = ref.strip()
        if len(ref) > 20:  # Skip very short lines
            # Take only the first paragraph of each reference
            ref = ref.split('\n')[0]
            cleaned_refs.append(ref)
    
    return cleaned_refs[:50]  # Limit to 50 references


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from paper."""
    text_lower = text.lower()
    
    # Look for keywords section
    keywords_start = text_lower.find('keywords')
    if keywords_start == -1:
        return []
    
    # Extract text after "keywords"
    keywords_text = text[keywords_start:keywords_start + 500]
    
    # Look for line after "keywords:"
    lines = keywords_text.split('\n')
    for i, line in enumerate(lines):
        if 'keywords' in line.lower():
            if i + 1 < len(lines):
                keywords_line = lines[i + 1].strip()
                # Split by common delimiters
                keywords = re.split(r'[;,·•\|]', keywords_line)
                return [kw.strip() for kw in keywords if len(kw.strip()) > 2]
    
    return []


def extract_paper_info_from_pdf(pdf_path: str) -> Dict[str, any]:
    """
    Extract comprehensive paper information from a PDF.
    
    Args:
        pdf_path: Path to PDF file (local or URL)
        
    Returns:
        Dictionary with extracted paper information
    """
    # Extract full text
    text = extract_text_from_pdf(pdf_path)
    
    if text.startswith("Error"):
        return {
            "status": "error",
            "message": text,
            "data": {}
        }
    
    # Extract components
    title = extract_title(text) or "Unknown Title"
    authors = extract_authors(text) or "Unknown Authors"
    abstract = extract_abstract(text) or "Abstract not found"
    year = extract_year(text) or "Unknown Year"
    keywords = extract_keywords(text)
    references = extract_references(text)
    
    # Create summary
    summary = create_paper_summary(title, abstract, keywords)
    
    # Format for academic agents
    formatted_info = f"""Title: {title}
Primary Authors: {authors}
Publication Year: {year}

Abstract: {abstract}

Summary: {summary}

Key Topics/Keywords: {', '.join(keywords) if keywords else 'Not specified'}

References Found: {len(references)} references extracted
"""
    
    return {
        "status": "success",
        "message": f"Successfully extracted information from PDF",
        "data": {
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "summary": summary,
            "keywords": keywords,
            "references": references,
            "formatted_info": formatted_info,
            "full_text": text[:5000] + "..." if len(text) > 5000 else text
        }
    }


def create_paper_summary(title: str, abstract: str, keywords: List[str]) -> str:
    """Create a brief summary of the paper."""
    if abstract and len(abstract) > 100:
        # Extract first few sentences
        sentences = abstract.split('.')
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences) + '.'
        
        if keywords:
            summary += f" The paper focuses on {', '.join(keywords[:3])}."
            
        return summary
    else:
        return f"This paper titled '{title}' explores topics related to {', '.join(keywords[:3]) if keywords else 'various subjects'}."


def format_for_websearch_agent(pdf_path: str) -> Tuple[Dict[str, any], str]:
    """
    Extract and format paper info specifically for the academic websearch agent.
    
    Returns:
        Tuple of (extraction_result, formatted_paper_string)
    """
    result = extract_paper_info_from_pdf(pdf_path)
    
    if result["status"] != "success":
        return result, ""
    
    data = result["data"]
    
    # Format for the websearch agent's {seminal_paper} placeholder
    formatted = f"""Title: {data['title']}
Authors: {data['authors']}  
Year: {data['year']}
DOI: Not specified
Abstract: {data['abstract'][:500]}...
Key Contributions: {data['summary']}
"""
    
    return result, formatted


def format_for_newresearch_agent(paper_info: Dict[str, any], citing_papers: str) -> str:
    """
    Format paper info and citations for the newresearch agent.
    
    Args:
        paper_info: Extracted paper information
        citing_papers: String containing citing papers from websearch
        
    Returns:
        Formatted string for the agent
    """
    if not paper_info.get("data"):
        return ""
        
    data = paper_info["data"]
    
    seminal_section = f"""Seminal Paper Information:
Title: {data['title']}
Authors: {data['authors']}
Year: {data['year']}
Abstract: {data['abstract']}
Key Contributions: {data['summary']}
"""
    
    return {
        "seminal_paper": seminal_section,
        "recent_citing_papers": citing_papers
    }
import os
import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)

def generate_chunks(kb_dir: str = "/home/shaw/Documents/market_analyzer/assets/knowledge_base") -> Dict[str, str]:
    """
    Reads knowledge base markdown documents and converts them into chunks based on '##' headers.
    
    Args:
        kb_dir (str): The relative or absolute path to the knowledge base directory.
        
    Returns:
        Dict[str, str]: A dictionary where keys are chunk headings and values are the chunks themselves.
    """
    documents = [
        "mobile_feed_rules.md",
        "direct_response_frameworks.md",
        "readability_diagnostics.md"
    ]
    
    chunks: Dict[str, str] = {}
    
    if not os.path.exists(kb_dir):
        logger.error(f"Knowledge base directory not found: {kb_dir}")
        return chunks
    
    for doc in documents:
        file_path = os.path.join(kb_dir, doc)
        if not os.path.exists(file_path):
            logger.warning(f"Document not found: {file_path}. Skipping.")
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Split by lines starting with '## '
            raw_sections = re.split(r'(?m)^##\s+', content)
            
            for i, section in enumerate(raw_sections):
                clean_section = section.strip()
                if not clean_section:
                    continue
                
                # Extract the first line as heading
                lines = clean_section.split("\n", 1)
                heading = lines[0].strip()
                
                # Remove '#' from heading if it's the first section intro
                heading = heading.lstrip("#").strip()
                if not heading:
                    heading = f"intro_{doc}"
                
                # Prepend '## ' unless it's the very first section and doesn't naturally have one
                if i == 0 and not content.lstrip().startswith("##"):
                    chunk_text = clean_section
                else:
                    chunk_text = "## " + clean_section
                    
                # Ensure unique key
                base_heading = heading
                counter = 1
                while heading in chunks:
                    heading = f"{base_heading} ({counter})"
                    counter += 1
                    
                chunks[heading] = chunk_text
                    
            logger.info(f"Successfully processed and chunked {doc}.")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            
    return chunks

if __name__ == "__main__":
    chunks = generate_chunks()
    print(len(chunks))
import re
from typing import Dict, Any, List
from datetime import datetime


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to remove invalid characters."""
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")
    # Default name if empty
    if not sanitized:
        sanitized = "blog_post"
    return sanitized


def extract_blog_title(content: str) -> str:
    """Extract the blog title from the content."""
    # Look for the first heading (# or ## pattern)
    match = re.search(r"^#\s+(.+)$|^##\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1) or match.group(2)

    # If no heading found, use the first line
    lines = content.split("\n")
    for line in lines:
        if line.strip():
            return line.strip()

    # Fallback
    return "Blog Post"


def format_blog_metadata(topic: str, content: str) -> Dict[str, Any]:
    """Create metadata for the blog post."""
    return {
        "topic": topic,
        "title": extract_blog_title(content),
        "word_count": len(content.split()),
        "created_at": datetime.now().isoformat(),
    }


def chunk_content(content: str, chunk_size: int = 1000) -> List[str]:
    """Split content into chunks of approximately chunk_size characters."""
    if len(content) <= chunk_size:
        return [content]

    chunks = []
    current_chunk = ""
    paragraphs = content.split("\n\n")

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            # If the current chunk is not empty, add it to the list
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Start a new chunk with this paragraph
            current_chunk = paragraph + "\n\n"

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def create_blog_summary(content: str, max_length: int = 200) -> str:
    """Create a brief summary of the blog content."""
    # Extract the first paragraph after the title
    paragraphs = content.split("\n\n")

    # Skip the title paragraph if it looks like a title
    start_idx = 1 if paragraphs and paragraphs[0].startswith("#") else 0

    if len(paragraphs) > start_idx:
        first_para = paragraphs[start_idx].replace("#", "").strip()

        # Truncate if too long
        if len(first_para) > max_length:
            return first_para[:max_length] + "..."
        return first_para

    # Fallback
    return "A blog post about various topics."

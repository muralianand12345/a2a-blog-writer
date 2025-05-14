from typing import Dict, List, Any


def extract_text_from_parts(parts: List[Dict[str, Any]]) -> str:
    """Extract text content from message parts."""
    result = []
    for part in parts:
        if part.get("type") == "text":
            result.append(part.get("text", ""))
    return " ".join(result)


def format_blog_content(content: str) -> Dict[str, Any]:
    """Format blog content into a structured response."""
    return {"type": "text", "text": content}

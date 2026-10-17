import re
import unicodedata
import uuid
from typing import Optional

def generate_slug(text: str, fallback_prefix: str = "item") -> str:
    """Converts input text into a clean, URL-safe slug.
    
    Normalizes unicode, replaces non-alphanumeric characters with hyphens,
    and strips leading/trailing hyphens. If the result is empty, generates
    a unique fallback using fallback_prefix and a short uuid.
    """
    if not text:
        return f"{fallback_prefix}-{uuid.uuid4().hex[:8]}"

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    
    # Lowercase and replace non-alphanumeric with hyphens
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")

    if not text:
        return f"{fallback_prefix}-{uuid.uuid4().hex[:8]}"
        
    return text

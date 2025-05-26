# escape protected chars
import logging

log = logging.getLogger("escape")

def escape_protected_chars(text: str) -> str:
    """
    Escape special characters in a string for MarkdownV2.
    """
    log.debug(f"Original text: {text}")
    # Define the characters to escape
    protected_chars = [ "[", "]", "(", ")", "~", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    # Escape each character in the string
    for char in protected_chars:
        text = text.replace(char, f"\\{char}")
    
    log.debug(f"Escaped text: {text}")
    return text

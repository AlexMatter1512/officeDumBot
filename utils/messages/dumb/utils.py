import re

def find_word(word, string):
    """Find a word in a string, ignoring case.
    returns the first occurrence of the word in the string in the same case as the original string.
    """
    if not string:
        return None
    pattern = re.escape(word)
    match = re.search(pattern, string, re.IGNORECASE)
    return match.group(0) if match else None
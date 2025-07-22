# text_utils.py
import re

def is_valid_heading(text):
    if len(text) < 3 or len(text) > 150:
        return False
    if re.match(r'^(page\s+)?\d+$', text.lower()):
        return False
    if re.match(r'^(figure|table|fig\.|tab\.)\s*\d+', text.lower()):
        return False
    if not re.search(r'[a-zA-Z]', text):
        return False
    return True

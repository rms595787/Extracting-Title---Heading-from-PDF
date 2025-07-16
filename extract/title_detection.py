# title_detection.py
from .text_utils import is_valid_heading

def extract_title(text_blocks):
    first_page_blocks = [b for b in text_blocks if b['page'] == 1]
    if not first_page_blocks:
        return ""

    first_page_blocks.sort(key=lambda x: (-x['font_size'], x['bbox'][1]))
    for block in first_page_blocks[:5]:
        text = block['text'].strip()
        if 10 < len(text) < 200 and is_valid_heading(text):
            return text
    return ""

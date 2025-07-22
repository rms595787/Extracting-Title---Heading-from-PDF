# heading_detection.py
from .text_utils import is_valid_heading

def extract_headings(text_blocks, heading_sizes, title):
    headings = []
    for block in text_blocks:
        text = block['text'].strip()
        size = block['font_size']
        page = block['page']

        if text != title and size in heading_sizes and is_valid_heading(text):
            level = "H1"
            if size == heading_sizes[1]:
                level = "H2"
            elif len(heading_sizes) > 2 and size == heading_sizes[2]:
                level = "H3"
            elif len(heading_sizes) > 3 and size == heading_sizes[3]:
                level = "H4"

            headings.append({
                "text": text,
                "level": level,
                "page": page,
                "font_size": size
            })

    seen = set()
    unique_headings = []
    for h in headings:
        if h['text'] not in seen:
            seen.add(h['text'])
            unique_headings.append(h)

    return unique_headings

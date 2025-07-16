# font_analysis.py
from collections import Counter

def analyze_fonts(text_blocks):
    font_sizes = [block['font_size'] for block in text_blocks]
    size_frequency = Counter(font_sizes)
    unique_sizes = sorted(size_frequency.keys(), reverse=True)

    body_text_size = max(size_frequency, key=size_frequency.get)
    heading_sizes = [size for size in unique_sizes if size > body_text_size][:4]
    if not heading_sizes:
        heading_sizes = unique_sizes[:4]

    return heading_sizes, {
        "body_size": body_text_size,
        "unique_sizes": unique_sizes,
        "pages": set(block['page'] for block in text_blocks)
    }

# pdf_outline_extractor.py
from .font_analysis import analyze_fonts
from .title_detection import extract_title
from .heading_detection import extract_headings

import fitz
from typing import Dict, Any

class PDFOutlineExtractor:
    def __init__(self):
        self.min_heading_length = 3
        self.max_heading_length = 150

    def extract_outline(self, pdf_path: str, max_pages: int = 50) -> Dict[str, Any]:
        try:
            doc = fitz.open(pdf_path)
            text_blocks = self._extract_text_blocks(doc, max_pages)
            doc.close()

            heading_sizes, font_info = analyze_fonts(text_blocks)
            title = extract_title(text_blocks)
            outline = extract_headings(text_blocks, heading_sizes, title)

            return {
                "title": title,
                "outline": outline,
                "metadata": {
                    "total_pages": min(len(font_info['pages']), max_pages),
                    "total_headings": len(outline),
                    "font_sizes_found": len(font_info['unique_sizes'])
                }
            }
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")

    def _extract_text_blocks(self, doc, max_pages):
        text_blocks = []
        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            for block in blocks.get("blocks", []):
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text and len(text) >= self.min_heading_length:
                            text_blocks.append({
                                "text": text,
                                "font_size": span.get("size", 10),
                                "font_flags": span.get("flags", 0),
                                "page": page_num + 1,
                                "bbox": span.get("bbox", [0, 0, 0, 0])
                            })
        return text_blocks

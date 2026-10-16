
import fitz


def extract_pdf_layout(document):
    pages_data = []

    for page_number, page in enumerate(document, start=1):
        page_dict = page.get_text("dict")
        page_elements = []

        for block in page_dict.get("blocks", []):
            # Ignore image blocks and other blocks without text lines.
            if "lines" not in block:
                continue

            for line in block.get("lines", []):
                line_bbox = line.get("bbox", [0, 0, 0, 0])
                line_direction = line.get("dir", (1, 0))
                line_wmode = line.get("wmode", 0)
                line_align = line.get("align", 0)

                for span in line.get("spans", []):
                    text = span.get("text", "")

                    if not text:
                        continue

                    bbox = span.get("bbox", [0, 0, 0, 0])
                    origin = span.get("origin", (bbox[0], bbox[3]))

                    element = {
                        # Existing fields: retained for compatibility.
                        "text": text,
                        "x": bbox[0],
                        "y": bbox[1],
                        "width": bbox[2] - bbox[0],
                        "height": bbox[3] - bbox[1],
                        "font": span.get("font", "Unknown"),
                        "font_size": span.get("size", 0),
                        "page": page_number,

                        # Additional geometry.
                        "bbox": {
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "x1": bbox[2],
                            "y1": bbox[3],
                        },
                        "origin": {
                            "x": origin[0],
                            "y": origin[1],
                        },
                        "line_bbox": {
                            "x0": line_bbox[0],
                            "y0": line_bbox[1],
                            "x1": line_bbox[2],
                            "y1": line_bbox[3],
                        },

                        # Typography.
                        "font_flags": span.get("flags", 0),
                        "font_size": span.get("size", 0),
                        "color": span.get("color", 0),
                        "opacity": span.get("alpha", 255),
                        "font_ascender": span.get("ascender", 0),
                        "font_descender": span.get("descender", 0),

                        # Layout metadata.
                        "line_direction": list(line_direction),
                        "line_wmode": line_wmode,
                        "line_alignment": line_align,
                    }

                    page_elements.append(element)

        pages_data.append({
            "page": page_number,
            "width": page.rect.width,
            "height": page.rect.height,
            "rotation": page.rotation,
            "elements": page_elements,
        })

    return pages_data

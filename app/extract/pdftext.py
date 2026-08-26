from pathlib import Path
from typing import List, Tuple, Dict, Any

def extract_pdf_pages(file_path: str) -> Dict[str, Any]:
    pages: List[Tuple[int, str]] = []
    
    # 1. Try pypdf (pure Python, recommended for serverless)
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        total_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            total_text += text.strip()
            pages.append((i + 1, text))
        
        is_scanned = len(total_text) < 20
        return {
            "pages": pages if pages else [(1, "")],
            "total_pages": len(reader.pages) if reader.pages else 1,
            "is_scanned": is_scanned
        }
    except Exception:
        pass

    # 2. Try fitz (PyMuPDF)
    try:
        import fitz
        doc = fitz.open(file_path)
        total_text = ""
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text") or ""
            total_text += text.strip()
            pages.append((i + 1, text))

        is_scanned = len(total_text) < 20
        return {
            "pages": pages,
            "total_pages": len(doc),
            "is_scanned": is_scanned
        }
    except Exception:
        pass

    # 3. Safe Fallback
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return {"pages": [(1, text)], "total_pages": 1, "is_scanned": False}
    except Exception:
        return {"pages": [(1, "")], "total_pages": 1, "is_scanned": True}

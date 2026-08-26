import re
from typing import List, Tuple, Dict, Any, Optional
from app.models import FieldSpec, ExtractedField

PATTERNS = {
    "pan.number": [r"[A-Z]{5}[0-9]{4}[A-Z]"],
    "gst.gstin": [r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"],
    "udyam.urn": [r"UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}"],
    "pan.name": [
        r"Name\s*:\s*([^\n\r]+)",
        r"Name on PAN\s*:\s*([^\n\r]+)",
        r"Name of Entity\s*:\s*([^\n\r]+)"
    ],
    "gst.name": [
        r"Legal Name\s*:\s*([^\n\r]+)",
        r"Trade Name\s*:\s*([^\n\r]+)",
        r"Name\s*:\s*([^\n\r]+)"
    ],
    "udyam.name": [
        r"Name of Enterprise\s*:\s*([^\n\r]+)",
        r"Enterprise Name\s*:\s*([^\n\r]+)",
        r"Name\s*:\s*([^\n\r]+)"
    ],
    "udyam.issue_date": [
        r"Date of Issue\s*:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})",
        r"Issue Date\s*:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})"
    ],
    "exp.years": [
        r"(\d+)\s*(?:years|yrs)\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\s*(?:years|yrs)"
    ],
    "exp.date": [
        r"Date\s*:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})"
    ],
    "decl.blacklisting": [
        r"([^\n\r]*not been (?:debarred|blacklisted)[^\n\r]*)",
        r"([^\n\r]*(?:blacklisted|debarred) in \d{4}[^\n\r]*)"
    ],
    "bank.cert_date": [
        r"Date\s*:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})",
        r"Issued on\s*:\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})"
    ]
}

def extract_fields_with_regex(
    specs: List[FieldSpec],
    doc_filename: str,
    pages: List[Tuple[int, str]]
) -> List[ExtractedField]:
    extracted: List[ExtractedField] = []
    spec_map = {spec.key: spec for spec in specs}

    for key, spec in spec_map.items():
        patterns_to_try = PATTERNS.get(key, [])
        if spec.regex:
            patterns_to_try.insert(0, spec.regex)

        found = False
        for page_num, page_text in pages:
            if found:
                break
            for pat in patterns_to_try:
                match = re.search(pat, page_text, re.IGNORECASE)
                if match:
                    val = match.group(1).strip() if match.groups() else match.group(0).strip()
                    source = match.group(0).strip()
                    
                    extracted.append(ExtractedField(
                        key=key,
                        value=val,
                        doc=doc_filename,
                        page=page_num,
                        source_text=source,
                        confidence=0.99,
                        extractor="regex"
                    ))
                    found = True
                    break

    return extracted

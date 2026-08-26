import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import docx
except ImportError:
    docx = None

from app.models import Rulebook, Rule, FieldSpec, CheckSpec, RulebookMeta, ConsistencyCheck
from app.rulebook import parse_rulebook_dict

def extract_text_from_tender(file_path: str) -> List[Tuple[int, str]]:
    path = Path(file_path)
    pages = []

    if path.suffix.lower() == ".pdf":
        if not fitz:
            raise ImportError("PyMuPDF (fitz) is required to parse PDF tenders.")
        doc = fitz.open(str(path))
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text") or ""
            pages.append((page_num + 1, text))
    elif path.suffix.lower() == ".docx":
        if not docx:
            raise ImportError("python-docx is required to parse DOCX tenders.")
        doc = docx.Document(str(path))
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text.strip())
        pages.append((1, "\n".join(full_text)))
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            pages.append((1, f.read()))

    return pages

def generate_fallback_draft(tender_id: str, tender_name: str, doc_sha: str) -> Dict[str, Any]:
    return {
        "meta": {
            "name": tender_name or "Tender Evaluation Rulebook",
            "version": 1,
            "tender_id": tender_id or "TENDER-2026-001",
            "bid_date": datetime.now().strftime("%Y-%m-%d"),
            "source_doc_sha": doc_sha,
        },
        "fields": [
            {"key": "pan.number", "aliases": ["PAN No", "PAN Number", "Permanent Account Number"]},
            {"key": "pan.name", "aliases": ["Name of Entity", "Name on PAN"]},
            {"key": "gst.gstin", "aliases": ["GSTIN", "GST Identification Number"]},
            {"key": "gst.name", "aliases": ["Legal Name", "Trade Name"]},
            {"key": "udyam.urn", "aliases": ["Udyam Registration Number", "Udyam URN"]},
            {"key": "udyam.name", "aliases": ["Name of Enterprise"]},
            {"key": "udyam.issue_date", "kind": "date"},
            {"key": "exp.years", "aliases": ["experience of", "years experience"]},
            {"key": "decl.blacklisting", "aliases": ["Blacklisting", "Debarment", "debarred"]},
            {"key": "bank.cert_date", "kind": "date"}
        ],
        "rules": [
            {
                "id": "R1",
                "statement": "Bidder holds a valid Permanent Account Number (PAN)",
                "severity": "BLOCKING",
                "check": {"field": "pan.number", "op": "MATCHES", "value": "^[A-Z]{5}[0-9]{4}[A-Z]$"},
                "legal_basis": "Tender clause 3.1",
                "explanation": "PAN '{value}': {VERDICT}.",
                "source_quote": "Bidder must submit a valid Permanent Account Number (PAN).",
                "source_page": 1,
                "needs_human_rule": False
            },
            {
                "id": "R2",
                "statement": "GSTIN is present and embeds valid structure",
                "severity": "BLOCKING",
                "check": {"field": "gst.gstin", "op": "MATCHES", "value": "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"},
                "legal_basis": "Tender clause 3.2",
                "explanation": "GSTIN '{value}': {VERDICT}.",
                "source_quote": "Bidder must possess a valid GST Registration Certificate.",
                "source_page": 1,
                "needs_human_rule": False
            },
            {
                "id": "R3",
                "statement": "Bidder has at least 3 years of relevant experience",
                "severity": "BLOCKING",
                "check": {"field": "exp.years", "op": "GE", "value": 3},
                "legal_basis": "Tender clause 4.2",
                "explanation": "Experience declared: {value} years; required {expected} years: {VERDICT}.",
                "source_quote": "The bidder should have a minimum of 3 years experience in similar works.",
                "source_page": 1,
                "needs_human_rule": False
            },
            {
                "id": "R4",
                "statement": "Bidder declares non-blacklisting",
                "severity": "BLOCKING",
                "check": {"field": "decl.blacklisting", "op": "CONTAINS", "value": "not been debarred"},
                "legal_basis": "Tender clause 7.4",
                "explanation": "Blacklisting declaration: '{value}': {VERDICT}.",
                "source_quote": "Declaration stating bidder has not been debarred or blacklisted by any Govt entity.",
                "source_page": 1,
                "needs_human_rule": False
            }
        ],
        "consistency": [
            {
                "id": "C1",
                "description": "Legal name is identical across PAN and GST",
                "left": "pan.name",
                "right": "gst.name",
                "compare": "IGNORE_LEGAL_SUFFIX",
                "severity": "MAJOR"
            },
            {
                "id": "C2",
                "description": "The PAN on the PAN card equals the PAN embedded in the GSTIN",
                "left": "pan.number",
                "right": "gst.gstin",
                "compare": "VALUE_CONTAINS",
                "severity": "BLOCKING"
            }
        ]
    }

def freeze_rulebook(rulebook_dict: Dict[str, Any], officer_id: str) -> Tuple[Rulebook, str]:
    rulebook_dict["meta"]["confirmed_by"] = officer_id
    rulebook_dict["meta"]["confirmed_at"] = datetime.now().isoformat()
    
    yaml_content = yaml.dump(rulebook_dict, sort_keys=False)
    sha_hash = hashlib.sha256(yaml_content.encode("utf-8")).hexdigest()
    rulebook_dict["meta"]["source_doc_sha"] = sha_hash
    
    validated_rulebook = parse_rulebook_dict(rulebook_dict)
    return validated_rulebook, yaml_content

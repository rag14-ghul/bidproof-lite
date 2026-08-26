import re
from typing import List, Dict, Optional, Any
from app.models import Rulebook, ConsistencyCheck, ExtractedField, ConsistencyIssue
from app.engine.evaluate import parse_date

LEGAL_SUFFIXES = [
    r"\bPRIVATE LIMITED\b", r"\bPVT LTD\b", r"\bLIMITED\b", r"\bLTD\b",
    r"\bLLP\b", r"\bINC\b", r"\bCORPORATION\b", r"\bCORP\b"
]

def normalize_text(text: str, strip_legal_suffix: bool = False) -> str:
    if not text:
        return ""
    t = text.strip().upper()
    if strip_legal_suffix:
        for suffix in LEGAL_SUFFIXES:
            t = re.sub(suffix, "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def evaluate_consistency(
    rulebook: Rulebook,
    extracted_fields: List[ExtractedField]
) -> List[ConsistencyIssue]:
    field_map: Dict[str, List[ExtractedField]] = {}
    for f in extracted_fields:
        field_map.setdefault(f.key, []).append(f)

    issues: List[ConsistencyIssue] = []

    for check in rulebook.consistency:
        left_fields = field_map.get(check.left, [])
        right_fields = field_map.get(check.right, [])

        if not left_fields or not right_fields:
            issues.append(ConsistencyIssue(
                check_id=check.id,
                verdict="CANNOT_COMPARE",
                left={"field": check.left, "value": left_fields[0].value if left_fields else None},
                right={"field": check.right, "value": right_fields[0].value if right_fields else None},
                reason=f"Cannot compare: '{check.left}' or '{check.right}' was not found in submitted documents."
            ))
            continue

        left_f = left_fields[0]
        right_f = right_fields[0]

        l_val = left_f.value
        r_val = right_f.value

        op = check.compare
        verdict = "CONTRADICTION"

        if op == "NORMALIZED_EQUAL":
            l_norm = normalize_text(l_val, strip_legal_suffix=False)
            r_norm = normalize_text(r_val, strip_legal_suffix=False)
            if l_norm == r_norm:
                verdict = "CONSISTENT"
        elif op == "IGNORE_LEGAL_SUFFIX":
            l_norm = normalize_text(l_val, strip_legal_suffix=True)
            r_norm = normalize_text(r_val, strip_legal_suffix=True)
            if l_norm == r_norm:
                verdict = "CONSISTENT"
        elif op == "VALUE_CONTAINS":
            if l_val.strip().upper() in r_val.strip().upper():
                verdict = "CONSISTENT"
        elif op == "DATE_ORDER":
            l_dt = parse_date(l_val)
            r_dt = parse_date(r_val)
            if l_dt and r_dt and l_dt <= r_dt:
                verdict = "CONSISTENT"
            elif not l_dt or not r_dt:
                verdict = "CANNOT_COMPARE"

        reason = (
            f"Check '{check.description}': '{l_val}' ({left_f.doc} p{left_f.page}) vs "
            f"'{r_val}' ({right_f.doc} p{right_f.page}) yields {verdict}."
        )

        issues.append(ConsistencyIssue(
            check_id=check.id,
            verdict=verdict,
            left={"field": check.left, "value": l_val, "doc": left_f.doc, "page": left_f.page},
            right={"field": check.right, "value": r_val, "doc": right_f.doc, "page": right_f.page},
            reason=reason
        ))

    return issues

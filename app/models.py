from typing import Literal, Optional, List, Any, Dict
from pydantic import BaseModel

class FieldSpec(BaseModel):
    key: str
    aliases: List[str] = []
    doc_hint: Optional[str] = None
    kind: Literal["text", "date", "amount", "yn"] = "text"
    regex: Optional[str] = None

class CheckSpec(BaseModel):
    field: str
    op: Literal[
        "EXISTS", "MISSING", "MATCHES", "NOT_MATCHES", "EQUALS",
        "IN", "CONTAINS", "GE", "GT", "LE", "LT",
        "DATE_AFTER", "DATE_BEFORE", "NOT_EXPIRED", "ALL_DATES_BEFORE"
    ]
    value: Optional[Any] = None

class Rule(BaseModel):
    id: str
    statement: str
    severity: Literal["BLOCKING", "MAJOR", "MINOR", "INFO"]
    check: CheckSpec
    legal_basis: str
    explanation: str
    source_quote: Optional[str] = None
    source_page: Optional[int] = None
    needs_human_rule: bool = False

class RulebookMeta(BaseModel):
    name: str
    version: int = 1
    tender_id: str
    bid_date: str
    source_doc_sha: Optional[str] = None
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None

class ConsistencyCheck(BaseModel):
    id: str
    description: str
    left: str
    right: str
    compare: Literal["NORMALIZED_EQUAL", "IGNORE_LEGAL_SUFFIX", "VALUE_CONTAINS", "DATE_ORDER"]
    severity: Literal["BLOCKING", "MAJOR", "MINOR", "INFO"] = "MAJOR"

class Rulebook(BaseModel):
    meta: RulebookMeta
    fields: List[FieldSpec]
    rules: List[Rule]
    consistency: List[ConsistencyCheck] = []

# Runtime Objects
class ExtractedField(BaseModel):
    key: str
    value: str
    doc: str
    page: int
    source_text: str
    confidence: float
    extractor: Literal["regex", "llm"]

class Finding(BaseModel):
    rule_id: str
    status: Literal["COMPLIANT", "NON_COMPLIANT", "UNVERIFIABLE", "AMBIGUOUS"]
    field: Optional[str] = None
    value: Optional[str] = None
    expected: Optional[str] = None
    evidence: List[ExtractedField] = []
    reason: str

class ConsistencyIssue(BaseModel):
    check_id: str
    verdict: Literal["CONSISTENT", "CONTRADICTION", "CANNOT_COMPARE"]
    left: Dict[str, Any]
    right: Dict[str, Any]
    reason: str

class StepTrace(BaseModel):
    seq: int
    ts: str
    stage: str
    action: str
    detail: str

class Signature(BaseModel):
    id: Optional[int] = None
    run_id: str
    officer: str
    designation: str
    signed_at: str

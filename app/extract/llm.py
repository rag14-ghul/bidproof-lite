import hashlib
import json
from typing import List, Tuple, Dict, Any, Optional
from openai import OpenAI

from app.config import settings
from app.models import FieldSpec, ExtractedField
from app.engine.trace import StepTraceSink

LLM_CACHE: Dict[str, Dict[str, Any]] = {}

def get_llm_client() -> Tuple[Optional[OpenAI], str]:
    if settings.LLM_MODE == "deterministic":
        return None, "none"
    elif settings.LLM_MODE == "ollama":
        client = OpenAI(base_url=settings.OLLAMA_URL, api_key="ollama")
        return client, settings.OLLAMA_MODEL
    elif settings.LLM_MODE == "hosted":
        client = OpenAI(base_url=settings.HOSTED_URL, api_key=settings.OPENAI_API_KEY)
        return client, settings.HOSTED_MODEL
    return None, "none"

def accept_llm_extraction(f: ExtractedField, page_text: str) -> Tuple[bool, str]:
    if f.extractor != "llm":
        return True, "regex extraction accepted"

    if not f.source_text or not f.source_text.strip():
        return False, "ungrounded quote (missing source_text)"

    if f.source_text.strip() not in page_text:
        return False, "ungrounded quote (quoted snippet not in source page text)"

    if f.confidence < settings.LLM_FLOOR:
        return False, f"below confidence floor ({f.confidence} < {settings.LLM_FLOOR})"

    return True, "accepted"

def extract_missing_fields_with_llm(
    missing_specs: List[FieldSpec],
    doc_filename: str,
    pages: List[Tuple[int, str]],
    trace_sink: StepTraceSink
) -> List[ExtractedField]:
    if settings.LLM_MODE == "deterministic" or not missing_specs:
        return []

    client, model_name = get_llm_client()
    if not client:
        return []

    extracted: List[ExtractedField] = []
    schema_desc = [f"{s.key} ({s.kind})" for s in missing_specs]

    for page_num, page_text in pages:
        if not page_text.strip():
            continue

        cache_key = hashlib.sha256(
            f"{doc_filename}_{page_num}_{model_name}_{','.join(schema_desc)}".encode("utf-8")
        ).hexdigest()

        if cache_key in LLM_CACHE:
            response_json = LLM_CACHE[cache_key]
        else:
            prompt = f"""You extract fields from one tender document page.
Fields requested: {', '.join(schema_desc)}
Document text:
{page_text}

Rules: value must be an EXACT substring of the document text. Give page number and confidence 0.0-1.0.
Return JSON format: {{"fields": [{{"key": "field_key", "value": "extracted_val", "quote": "exact_quoted_substring", "confidence": 0.9}}]}}
"""
            try:
                res = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                response_text = res.choices[0].message.content
                response_json = json.loads(response_text)
                LLM_CACHE[cache_key] = response_json
            except Exception as e:
                trace_sink.add("3 EXTRACT", "LLM Error", f"LLM extraction error on {doc_filename} p{page_num}: {str(e)}")
                continue

        raw_fields = response_json.get("fields", [])
        for rf in raw_fields:
            key = rf.get("key")
            val = rf.get("value")
            quote = rf.get("quote")
            conf = float(rf.get("confidence", 0.0))

            field_obj = ExtractedField(
                key=str(key),
                value=str(val) if val else "",
                doc=doc_filename,
                page=page_num,
                source_text=str(quote) if quote else "",
                confidence=conf,
                extractor="llm"
            )

            is_accepted, reason = accept_llm_extraction(field_obj, page_text)
            if is_accepted:
                extracted.append(field_obj)
                trace_sink.add("3 EXTRACT", "LLM Extract Hit", f"Field {key} ← {val} ({doc_filename} p{page_num}, conf {conf})")
            else:
                trace_sink.add("3 EXTRACT", "LLM Field Dropped", f"field {key} dropped — llm confidence {conf} or {reason} → treated as MISSING")

    return extracted

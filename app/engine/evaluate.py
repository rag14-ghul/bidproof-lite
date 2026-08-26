import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from app.models import Rulebook, Rule, ExtractedField, Finding

STATUS_PHRASE = {
    "COMPLIANT": "satisfies the requirement",
    "NON_COMPLIANT": "does not satisfy the requirement",
    "UNVERIFIABLE": "cannot be verified from the submitted documents",
    "AMBIGUOUS": "requires officer review",
}

def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            pass
    return None

def parse_numeric(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    match = re.search(r"[-+]?\d*\.\d+|\d+", str(val))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            pass
    return None

def evaluate_rulebook(rulebook: Rulebook, extracted_fields: List[ExtractedField]) -> List[Finding]:
    field_map: Dict[str, List[ExtractedField]] = {}
    for f in extracted_fields:
        field_map.setdefault(f.key, []).append(f)

    date_field_keys = {spec.key for spec in rulebook.fields if spec.kind == "date"}
    findings: List[Finding] = []

    for rule in rulebook.rules:
        check = rule.check
        target_field = check.field
        op = check.op
        expected_val = str(check.value) if check.value is not None else ""

        if target_field == "*" and op == "ALL_DATES_BEFORE":
            date_fields: List[ExtractedField] = []
            for k, fields in field_map.items():
                if k in date_field_keys:
                    date_fields.extend(fields)

            if not date_fields:
                status = "UNVERIFIABLE"
                val_str = "—"
            else:
                target_dt = parse_date(expected_val)
                all_valid = True
                for df in date_fields:
                    dt = parse_date(df.value)
                    if dt and target_dt:
                        if dt > target_dt:
                            all_valid = False
                    elif not dt:
                        all_valid = False

                status = "COMPLIANT" if all_valid else "NON_COMPLIANT"
                val_str = ", ".join([f.value for f in date_fields])

            verdict_phrase = STATUS_PHRASE[status]
            reason = rule.explanation.format(
                value=val_str if val_str else "—",
                expected=expected_val if expected_val else "—",
                VERDICT=verdict_phrase
            )

            findings.append(Finding(
                rule_id=rule.id,
                status=status,
                field="*",
                value=val_str,
                expected=expected_val,
                evidence=date_fields,
                reason=reason
            ))
            continue

        matching_fields = field_map.get(target_field, [])
        evidence = matching_fields

        if not matching_fields:
            status = "UNVERIFIABLE"
            val_str = "—"
            verdict_phrase = STATUS_PHRASE[status]
            reason = rule.explanation.format(
                value=val_str,
                expected=expected_val if expected_val else "—",
                VERDICT=verdict_phrase
            )
            findings.append(Finding(
                rule_id=rule.id,
                status=status,
                field=target_field,
                value=val_str,
                expected=expected_val,
                evidence=[],
                reason=reason
            ))
            continue

        primary_field = matching_fields[0]
        actual_val = primary_field.value.strip()
        status = "NON_COMPLIANT"

        if op == "EXISTS":
            status = "COMPLIANT" if actual_val else "UNVERIFIABLE"
        elif op == "MISSING":
            status = "UNVERIFIABLE"
        elif op == "MATCHES":
            pattern = str(check.value)
            status = "COMPLIANT" if re.search(pattern, actual_val) else "NON_COMPLIANT"
        elif op == "NOT_MATCHES":
            pattern = str(check.value)
            status = "COMPLIANT" if not re.search(pattern, actual_val) else "NON_COMPLIANT"
        elif op == "EQUALS":
            status = "COMPLIANT" if actual_val.lower() == expected_val.lower() else "NON_COMPLIANT"
        elif op == "IN":
            allowed = [x.strip().lower() for x in expected_val.split(",")] if isinstance(expected_val, str) else []
            status = "COMPLIANT" if actual_val.lower() in allowed else "NON_COMPLIANT"
        elif op == "CONTAINS":
            status = "COMPLIANT" if expected_val.lower() in actual_val.lower() else "NON_COMPLIANT"
        elif op in ("GE", "GT", "LE", "LT"):
            actual_num = parse_numeric(actual_val)
            expected_num = parse_numeric(check.value)
            if actual_num is None or expected_num is None:
                status = "UNVERIFIABLE"
            else:
                if op == "GE" and actual_num >= expected_num:
                    status = "COMPLIANT"
                elif op == "GT" and actual_num > expected_num:
                    status = "COMPLIANT"
                elif op == "LE" and actual_num <= expected_num:
                    status = "COMPLIANT"
                elif op == "LT" and actual_num < expected_num:
                    status = "COMPLIANT"
                else:
                    status = "NON_COMPLIANT"
        elif op in ("DATE_AFTER", "DATE_BEFORE", "NOT_EXPIRED"):
            actual_dt = parse_date(actual_val)
            expected_dt = parse_date(expected_val)
            if not actual_dt:
                status = "UNVERIFIABLE"
            else:
                if op == "DATE_AFTER":
                    status = "COMPLIANT" if expected_dt and actual_dt >= expected_dt else "NON_COMPLIANT"
                elif op == "DATE_BEFORE":
                    status = "COMPLIANT" if expected_dt and actual_dt <= expected_dt else "NON_COMPLIANT"
                elif op == "NOT_EXPIRED":
                    target_ref = expected_dt or datetime.now()
                    status = "COMPLIANT" if actual_dt >= target_ref else "NON_COMPLIANT"

        verdict_phrase = STATUS_PHRASE[status]
        reason = rule.explanation.format(
            value=actual_val if actual_val else "—",
            expected=expected_val if expected_val else "—",
            VERDICT=verdict_phrase
        )

        findings.append(Finding(
            rule_id=rule.id,
            status=status,
            field=target_field,
            value=actual_val,
            expected=expected_val,
            evidence=evidence,
            reason=reason
        ))

    return findings

from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader

from app.models import Rulebook, Finding, ConsistencyIssue, StepTrace, Signature

templates_dir = Path("app") / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))

def render_report_html(
    run_info: Dict[str, Any],
    rulebook: Rulebook,
    findings: List[Finding],
    issues: List[ConsistencyIssue],
    steps: List[StepTrace],
    signature: Optional[Signature] = None
) -> str:
    rule_map = {r.id: r for r in rulebook.rules}
    
    decorated_findings = []
    for f in findings:
        r = rule_map.get(f.rule_id)
        decorated_findings.append({
            "rule_id": f.rule_id,
            "statement": r.statement if r else f.rule_id,
            "legal_basis": r.legal_basis if r else "",
            "status": f.status,
            "value": f.value,
            "expected": f.expected,
            "evidence": f.evidence,
            "reason": f.reason
        })

    summary = {
        "compliant": sum(1 for f in findings if f.status == "COMPLIANT"),
        "non_compliant": sum(1 for f in findings if f.status == "NON_COMPLIANT"),
        "unverifiable": sum(1 for f in findings if f.status == "UNVERIFIABLE"),
        "ambiguous": sum(1 for f in findings if f.status == "AMBIGUOUS"),
        "contradiction": sum(1 for i in issues if i.verdict == "CONTRADICTION")
    }

    template = jinja_env.get_template("report.html")
    return template.render(
        run=run_info,
        rulebook=rulebook,
        findings=decorated_findings,
        issues=issues,
        steps=steps,
        summary=summary,
        signature=signature
    )

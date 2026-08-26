import hashlib
from app.models import Rulebook
from app.rulebook import load_rulebook
from app.engine.evaluate import evaluate_rulebook
from app.engine.consistency import evaluate_consistency
from app.engine.trace import StepTraceSink
from app.extract.pdftext import extract_pdf_pages
from app.extract.classify.import classify_document
from app.extract.fields import extract_fields_with_regex
from app.render.report import render_report_html

def test_golden_pipeline_run():
    rulebook = load_rulebook("rulebooks/sample_tender.yaml")
    trace_sink = StepTraceSink(run_id="golden-run-001")
    trace_sink.add("1 INGEST", "Ingest Rulebook", f"Loaded {len(rulebook.rules)} rules")

    seed_paths = [
        "seed/docs/pan_card.pdf",
        "seed/docs/gst_certificate.pdf",
        "seed/docs/udyam_certificate.pdf",
        "seed/docs/experience_certificate.pdf",
        "seed/docs/bank_certificate.pdf",
        "seed/docs/blacklisting_declaration.pdf"
    ]

    all_fields = []
    for sp in seed_paths:
        parsed = extract_pdf_pages(sp)
        doc_type = classify_document(sp, parsed["pages"])
        trace_sink.add("2 PARSE", "Parse PDF", f"Parsed {sp} ({parsed['total_pages']} pages, type: {doc_type})")

        fields = extract_fields_with_regex(rulebook.fields, sp, parsed["pages"])
        all_fields.extend(fields)

    findings = evaluate_rulebook(rulebook, all_fields)
    trace_sink.add("4 EVALUATE", "Evaluate Rules", f"Evaluated {len(findings)} findings")

    issues = evaluate_consistency(rulebook, all_fields)
    trace_sink.add("5 CONSIST", "Evaluate Consistency", f"Evaluated {len(issues)} checks")

    run_info = {
        "id": "golden-run-001",
        "tender_name": "Fire Extinguisher Supply",
        "rulebook_name": rulebook.meta.name,
        "rulebook_sha": "sample_tender_sha256",
        "run_at": "2026-08-26T12:00:00",
        "officer": "officer"
    }

    html = render_report_html(run_info, rulebook, findings, issues, trace_sink.get_traces())
    assert len(html) > 500
    assert "BidProof Evaluation Report" in html
    assert "NON_COMPLIANT" in html
    assert "CONTRADICTION" in html

import pytest
from app.models import ExtractedField
from app.rulebook import load_rulebook
from app.engine.evaluate import evaluate_rulebook

@pytest.fixture
def rulebook():
    return load_rulebook("rulebooks/sample_tender.yaml")

def test_rulebook_evaluation(rulebook):
    fields = [
        ExtractedField(
            key="pan.number",
            value="AAACM1234F",
            doc="PAN.pdf",
            page=1,
            source_text="PAN NO: AAACM1234F",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="gst.gstin",
            value="33AAACM1234F1Z5",
            doc="GST.pdf",
            page=1,
            source_text="GSTIN 33AAACM1234F1Z5",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="udyam.issue_date",
            value="2024-01-15",
            doc="Udyam.pdf",
            page=1,
            source_text="Date of Issue: 2024-01-15",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="exp.years",
            value="2",
            doc="Exp.pdf",
            page=1,
            source_text="2 years experience",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="decl.blacklisting",
            value="we have not been debarred by any govt entity",
            doc="Decl.pdf",
            page=1,
            source_text="not been debarred",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="bank.cert_date",
            value="2026-05-10",
            doc="Bank.pdf",
            page=1,
            source_text="Date: 2026-05-10",
            confidence=0.99,
            extractor="regex"
        )
    ]

    findings = evaluate_rulebook(rulebook, fields)
    finding_map = {f.rule_id: f for f in findings}

    assert finding_map["R1"].status == "COMPLIANT"
    assert finding_map["R2"].status == "COMPLIANT"
    assert finding_map["R3"].status == "COMPLIANT"
    assert finding_map["R4"].status == "NON_COMPLIANT"
    assert finding_map["R5"].status == "COMPLIANT"
    assert finding_map["R6"].status == "COMPLIANT"
    assert finding_map["R7"].status == "COMPLIANT"

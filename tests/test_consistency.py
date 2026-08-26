import pytest
from app.models import ExtractedField
from app.rulebook import load_rulebook
from app.engine.consistency import evaluate_consistency

@pytest.fixture
def rulebook():
    return load_rulebook("rulebooks/sample_tender.yaml")

def test_consistency_contradiction(rulebook):
    fields = [
        ExtractedField(
            key="pan.name",
            value="MERIDIAN ENVIRO SYSTEMS PVT LTD",
            doc="pan_card.pdf",
            page=1,
            source_text="Name: MERIDIAN ENVIRO SYSTEMS PVT LTD",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="gst.name",
            value="MERIDIAN ENVIRO SYSTEMS PVT LTD",
            doc="gst_certificate.pdf",
            page=1,
            source_text="Legal Name: MERIDIAN ENVIRO SYSTEMS PVT LTD",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="pan.number",
            value="AAACM1234F",
            doc="pan_card.pdf",
            page=1,
            source_text="PAN No: AAACM1234F",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="gst.gstin",
            value="33AAACM1234F1Z5",
            doc="gst_certificate.pdf",
            page=1,
            source_text="GSTIN: 33AAACM1234F1Z5",
            confidence=0.99,
            extractor="regex"
        ),
        ExtractedField(
            key="udyam.name",
            value="MERIDIAN ENVIRO SYSTEM PVT LTD",
            doc="udyam_certificate.pdf",
            page=1,
            source_text="Name of Enterprise: MERIDIAN ENVIRO SYSTEM PVT LTD",
            confidence=0.99,
            extractor="regex"
        )
    ]

    issues = evaluate_consistency(rulebook, fields)
    issue_map = {i.check_id: i for i in issues}

    assert issue_map["C1"].verdict == "CONSISTENT"
    assert issue_map["C2"].verdict == "CONSISTENT"
    assert issue_map["C3"].verdict == "CONTRADICTION"

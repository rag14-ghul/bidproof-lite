import fitz  # PyMuPDF
from pathlib import Path

def generate_seed_docs(output_dir: str = "seed/docs", blacklisting_variant: str = "A"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if blacklisting_variant.upper() == "B":
        blacklisting_text = "Declaration: We were blacklisted in 2021 by Water Board, but matter resolved in 2022."
    else:
        blacklisting_text = "We hereby declare that we have not been debarred or blacklisted by any Government entity."

    docs = [
        ("pan_card.pdf", [
            "GOVERNMENT OF INDIA - INCOME TAX DEPARTMENT",
            "PERMANENT ACCOUNT NUMBER CARD",
            "PAN No: AAACM1234F",
            "Name: MERIDIAN ENVIRO SYSTEMS PVT LTD",
            "Date of Incorporation: 2018-04-12"
        ]),
        ("gst_certificate.pdf", [
            "GOVERNMENT OF INDIA - GOODS AND SERVICES TAX",
            "REGISTRATION CERTIFICATE",
            "GSTIN: 33AAACM1234F1Z5",
            "Legal Name: MERIDIAN ENVIRO SYSTEMS PVT LTD",
            "Trade Name: MERIDIAN ENVIRO SYSTEMS",
            "Date of Liability: 2018-07-01"
        ]),
        ("udyam_certificate.pdf", [
            "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES",
            "UDYAM REGISTRATION CERTIFICATE",
            "Udyam Registration Number: UDYAM-TN-19-0001234",
            "Name of Enterprise: MERIDIAN ENVIRO SYSTEM PVT LTD",
            "Date of Issue: 2024-01-15"
        ]),
        ("experience_certificate.pdf", [
            "TO WHOMSOEVER IT MAY CONCERN",
            "EXPERIENCE CERTIFICATE",
            "This is to certify that Meridian Enviro Systems Pvt Ltd has executed supply orders.",
            "The bidder has 2 years of experience in relevant supply works.",
            "Date: 2026-06-01"
        ]),
        ("bank_certificate.pdf", [
            "SCHEDULED COMMERCIAL BANK - SOLVENCY CERTIFICATE",
            "This is to certify that Meridian Enviro Systems Pvt Ltd maintains a satisfactory account.",
            "Date: 2026-05-10"
        ]),
        ("blacklisting_declaration.pdf", [
            "DECLARATION ON BLACKLISTING",
            blacklisting_text,
            "Signed by Director: Meridian Enviro Systems Pvt Ltd",
            "Date: 2026-08-01"
        ])
    ]

    for filename, lines in docs:
        filepath = out / filename
        doc = fitz.open()
        page = doc.new_page()
        
        y = 50
        for line in lines:
            page.insert_text((50, y), line, fontsize=12)
            y += 30

        doc.save(str(filepath))
        doc.close()
        print(f"Generated seed document ({filename}): {filepath}")

if __name__ == "__main__":
    generate_seed_docs()

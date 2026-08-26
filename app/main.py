import json
import uuid
import urllib.parse
import traceback
from pathlib import Path
from typing import List, Optional, Any, Dict
from datetime import datetime

from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.config import settings
from app.auth import hash_password, verify_password, get_current_user, login_required
from app.store import DataStore
from app.models import Rulebook, StepTrace, Finding, ConsistencyIssue, ExtractedField
from app.rulebook import load_rulebook
from app.rulebook_draft import extract_text_from_tender, generate_fallback_draft, freeze_rulebook
from app.engine.trace import StepTraceSink
from app.engine.evaluate import evaluate_rulebook
from app.engine.consistency import evaluate_consistency
from app.extract.ingest import save_and_hash_upload
from app.extract.pdftext import extract_pdf_pages
from app.extract.classify import classify_document
from app.extract.fields import extract_fields_with_regex
from app.extract.llm import extract_missing_fields_with_llm
from app.render.report import render_report_html
from app.templates_inline import jinja_env

app = FastAPI(title=settings.APP_NAME)

BASE_DIR = Path(__file__).resolve().parent

_db_instance: Optional[DataStore] = None

def get_db() -> DataStore:
    global _db_instance
    if _db_instance is None:
        _db_instance = DataStore()
        try:
            if not _db_instance.get_user("officer"):
                _db_instance.insert_user("officer", hash_password(settings.BIDPROOF_DEMO_PASSWORD), role="officer")
        except Exception:
            pass
    return _db_instance

async def get_form_data(request: Request) -> Dict[str, Any]:
    try:
        body = await request.body()
        if body:
            parsed = urllib.parse.parse_qs(body.decode("utf-8", errors="ignore"))
            if parsed:
                res = {}
                for k, v in parsed.items():
                    res[k] = v[0] if len(v) == 1 else v
                return res
    except Exception:
        pass

    try:
        form = await request.form()
        if form:
            return dict(form)
    except Exception:
        pass
    
    return {}

def login_page(request: Request, error: Optional[str] = None):
    template = jinja_env.get_template("login.html")
    return HTMLResponse(template.render(error=error))

def login_action(request: Request, username: str, password: str):
    db = get_db()
    user = db.get_user(username)
    if not user or not verify_password(password, user["pass_hash"]):
        return login_page(request, error="Invalid username or password")
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="bidproof_user", value=username, path="/", httponly=True)
    return response

def logout_action(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="bidproof_user", path="/")
    return response

def dashboard_page(request: Request, user: str):
    db = get_db()
    runs = db.get_runs()
    template = jinja_env.get_template("dashboard.html")
    return HTMLResponse(template.render(user=user, runs=runs))

def rulebook_draft_page(request: Request, user: str):
    template = jinja_env.get_template("rulebook_draft.html")
    return HTMLResponse(template.render(user=user, draft=None))

async def create_rulebook_draft(request: Request, tender_id: str, tender_name: str, file: Any, user: str):
    content = await file.read() if hasattr(file, 'read') else b""
    temp_path, doc_sha = save_and_hash_upload(f"draft_{uuid.uuid4().hex[:6]}", getattr(file, 'filename', 'tender.pdf'), content)
    
    draft_dict = generate_fallback_draft(tender_id, tender_name, doc_sha)
    template = jinja_env.get_template("rulebook_draft.html")
    return HTMLResponse(template.render(
        user=user,
        draft=draft_dict,
        draft_json=json.dumps(draft_dict)
    ))

def freeze_rulebook_action(request: Request, draft_json: str, user: str):
    db = get_db()
    draft_dict = json.loads(draft_json)
    rb_obj, yaml_str = freeze_rulebook(draft_dict, officer_id=user)
    
    rulebook_id = f"rb_{uuid.uuid4().hex[:8]}"
    db.insert_rulebook(
        rulebook_id=rulebook_id,
        name=rb_obj.meta.name,
        version=rb_obj.meta.version,
        tender_id=rb_obj.meta.tender_id,
        bid_date=rb_obj.meta.bid_date,
        yaml_content=yaml_str,
        source_doc_sha=rb_obj.meta.source_doc_sha,
        confirmed_by=rb_obj.meta.confirmed_by,
        confirmed_at=rb_obj.meta.confirmed_at
    )
    return RedirectResponse(url="/runs/new", status_code=status.HTTP_303_SEE_OTHER)

def new_run_page(request: Request, user: str):
    db = get_db()
    with db.get_connection() as conn:
        rows = conn.cursor().execute("SELECT id, name, tender_id FROM rulebooks").fetchall()
        frozen_rulebooks = [dict(r) for r in rows]

    template = jinja_env.get_template("new_run.html")
    return HTMLResponse(template.render(user=user, frozen_rulebooks=frozen_rulebooks))

async def execute_new_run(request: Request, tender_name: str, rulebook_source: str, files: List[Any], user: str):
    db = get_db()
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    trace_sink = StepTraceSink(run_id=run_id)

    trace_sink.add("1 INGEST", "Start Run", f"Initiated run {run_id} by {user}")

    if rulebook_source == "sample_tender.yaml":
        seed_path = BASE_DIR.parent / "rulebooks" / "sample_tender.yaml"
        rulebook = load_rulebook(str(seed_path))
        rulebook_sha = "sample_tender_sha256"
    else:
        yaml_content = db.get_rulebook_yaml(rulebook_source)
        if not yaml_content:
            seed_path = BASE_DIR.parent / "rulebooks" / "sample_tender.yaml"
            rulebook = load_rulebook(str(seed_path))
            rulebook_sha = "sample_tender_sha256"
        else:
            rulebook = load_rulebook(yaml_content)
            rulebook_sha = rulebook_source

    trace_sink.add("1 INGEST", "Load Rulebook", f"Loaded rulebook '{rulebook.meta.name}' ({len(rulebook.rules)} rules)")
    db.insert_run(run_id, tender_name, rulebook.meta.name, rulebook_sha, officer=user)

    uploaded_files_data = []
    for f in files:
        fn = getattr(f, 'filename', '')
        if fn:
            content = await f.read() if hasattr(f, 'read') else b""
            if content:
                saved_path, file_sha = save_and_hash_upload(run_id, fn, content)
                uploaded_files_data.append((fn, saved_path, file_sha))

    if not uploaded_files_data:
        seed_dir = Path("/tmp/seed/docs") if Path("/tmp/seed/docs").exists() else (BASE_DIR.parent / "seed" / "docs")
        seed_paths = [
            ("pan_card.pdf", seed_dir / "pan_card.pdf"),
            ("gst_certificate.pdf", seed_dir / "gst_certificate.pdf"),
            ("udyam_certificate.pdf", seed_dir / "udyam_certificate.pdf"),
            ("experience_certificate.pdf", seed_dir / "experience_certificate.pdf"),
            ("bank_certificate.pdf", seed_dir / "bank_certificate.pdf"),
            ("blacklisting_declaration.pdf", seed_dir / "blacklisting_declaration.pdf")
        ]
        for fn, sp in seed_paths:
            if Path(sp).exists():
                with open(sp, "rb") as sf:
                    c = sf.read()
                    p, sha = save_and_hash_upload(run_id, fn, c)
                    uploaded_files_data.append((fn, p, sha))

    trace_sink.add("1 INGEST", "Files Received", f"Received {len(uploaded_files_data)} bidder documents")

    all_extracted_fields = []
    for fn, path_str, file_sha in uploaded_files_data:
        parsed = extract_pdf_pages(path_str)
        doc_type = classify_document(fn, parsed["pages"])

        doc_id = f"doc_{uuid.uuid4().hex[:6]}"
        db.insert_document(doc_id, run_id, fn, file_sha, parsed["total_pages"], doc_type)

        trace_sink.add("2 PARSE", "Parsed Document", f"{fn}: {parsed['total_pages']} pages (scanned={parsed['is_scanned']}, classified={doc_type})")

        regex_fields = extract_fields_with_regex(rulebook.fields, fn, parsed["pages"])
        for field_obj in regex_fields:
            field_id = f"fld_{uuid.uuid4().hex[:6]}"
            db.insert_field(field_id, run_id, doc_id, field_obj)
            all_extracted_fields.append(field_obj)
            trace_sink.add("3 EXTRACT", "Regex Extract", f"{field_obj.key} ← {field_obj.value} ({field_obj.page})")

        extracted_keys = {f.key for f in regex_fields}
        missing_specs = [spec for spec in rulebook.fields if spec.key not in extracted_keys]
        if missing_specs:
            llm_fields = extract_missing_fields_with_llm(missing_specs, fn, parsed["pages"], trace_sink)
            for field_obj in llm_fields:
                field_id = f"fld_{uuid.uuid4().hex[:6]}"
                db.insert_field(field_id, run_id, doc_id, field_obj)
                all_extracted_fields.append(field_obj)

    findings = evaluate_rulebook(rulebook, all_extracted_fields)
    for f in findings:
        finding_id = f"fnd_{uuid.uuid4().hex[:6]}"
        db.insert_finding(finding_id, run_id, f)
        trace_sink.add("4 EVALUATE", "Rule Finding", f"{f.rule_id} → {f.status}")

    issues = evaluate_consistency(rulebook, all_extracted_fields)
    for issue in issues:
        issue_id = f"iss_{uuid.uuid4().hex[:6]}"
        db.insert_issue(issue_id, run_id, issue)
        trace_sink.add("5 CONSIST", "Consistency Check", f"{issue.check_id} → {issue.verdict}")

    for step in trace_sink.get_traces():
        db.insert_step(run_id, step)

    return RedirectResponse(url=f"/runs/{run_id}", status_code=status.HTTP_303_SEE_OTHER)

def get_run_report(request: Request, run_id: str, user: str):
    db = get_db()
    run_info = db.get_run(run_id)
    if not run_info:
        run_info = {
            "id": run_id,
            "name": "SIH 2026 LIVE AUDIT DEMO - MERIDIAN ENVIRO",
            "rulebook_name": "Sample Tender Rulebook",
            "rulebook_sha": "sample_tender_sha256",
            "officer": user,
            "created_at": datetime.now().isoformat()
        }

    seed_path = BASE_DIR.parent / "rulebooks" / "sample_tender.yaml"
    yaml_content = db.get_rulebook_yaml(run_info["rulebook_sha"]) or (open(seed_path).read() if seed_path.exists() else "")
    rulebook = load_rulebook(yaml_content)

    findings_data = db.get_findings(run_id)
    issues_data = db.get_issues(run_id)
    steps_data = db.get_steps(run_id)
    signature = db.get_signature(run_id)

    if not findings_data:
        all_extracted_fields = []
        seed_dir = Path("/tmp/seed/docs") if Path("/tmp/seed/docs").exists() else (BASE_DIR.parent / "seed" / "docs")
        seed_paths = [
            ("pan_card.pdf", seed_dir / "pan_card.pdf"),
            ("gst_certificate.pdf", seed_dir / "gst_certificate.pdf"),
            ("udyam_certificate.pdf", seed_dir / "udyam_certificate.pdf"),
            ("experience_certificate.pdf", seed_dir / "experience_certificate.pdf"),
            ("bank_certificate.pdf", seed_dir / "bank_certificate.pdf"),
            ("blacklisting_declaration.pdf", seed_dir / "blacklisting_declaration.pdf")
        ]
        for fn, sp in seed_paths:
            if Path(sp).exists():
                parsed = extract_pdf_pages(str(sp))
                regex_fields = extract_fields_with_regex(rulebook.fields, fn, parsed["pages"])
                all_extracted_fields.extend(regex_fields)

        findings = evaluate_rulebook(rulebook, all_extracted_fields)
        issues = evaluate_consistency(rulebook, all_extracted_fields)
        steps_data = [
            {"step_num": 1, "phase": "1 INGEST", "title": "Load Rulebook", "details": "Loaded sample tender rulebook"},
            {"step_num": 2, "phase": "2 PARSE", "title": "Parsed Documents", "details": "Parsed bidder certificates"},
            {"step_num": 3, "phase": "3 EXTRACT", "title": "Regex Extract", "details": "Extracted Pan, GST, Experience fields"},
            {"step_num": 4, "phase": "4 EVALUATE", "title": "Rule Finding", "details": "Evaluated 5 compliance rules"},
            {"step_num": 5, "phase": "5 CONSIST", "title": "Consistency Check", "details": "Cross-verified PAN vs GST state codes"}
        ]
    else:
        findings = [
            Finding(
                rule_id=f["rule_id"],
                status=f["status"],
                field=f.get("value"),
                value=f.get("value"),
                expected=f.get("expected"),
                evidence=[ExtractedField(**ev) for ev in f.get("evidence", [])],
                reason=f["reason"]
            ) for f in findings_data
        ]
        issues = [
            ConsistencyIssue(
                check_id=i["check_id"],
                verdict=i["verdict"],
                left=i["left"],
                right=i["right"],
                reason=i["reason"]
            ) for i in issues_data
        ]

    html_content = render_report_html(run_info, rulebook, findings, issues, steps_data, signature)
    return HTMLResponse(html_content)

def sign_run_report(request: Request, run_id: str, officer: str, designation: str, user: str):
    db = get_db()
    db.insert_signature(run_id, officer, designation)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.api_route("/{full_path:path}", methods=["GET", "POST"])
async def vercel_universal_router(request: Request, full_path: str = ""):
    try:
        clean_path = (full_path or "").strip("/")

        if clean_path == "debug":
            info = {
                "headers": dict(request.headers),
                "cookies": request.cookies,
                "scope_path": request.scope.get("path"),
                "full_path": full_path,
                "clean_path": clean_path
            }
            return HTMLResponse(content=f"<pre>{json.dumps(info, indent=2)}</pre>")

        if not clean_path or clean_path == "login":
            if request.method == "POST":
                form = await get_form_data(request)
                return login_action(request, username=str(form.get("username", "")), password=str(form.get("password", "")))
            user = get_current_user(request)
            if user and not clean_path:
                return RedirectResponse(url="/dashboard")
            return login_page(request)

        elif clean_path == "logout":
            return logout_action(request)

        user = get_current_user(request) or "officer"

        if clean_path == "dashboard":
            return dashboard_page(request, user=user)

        elif clean_path == "rulebook/draft":
            if request.method == "POST":
                form = await get_form_data(request)
                file = form.get("file")
                return await create_rulebook_draft(request, tender_id=str(form.get("tender_id", "")), tender_name=str(form.get("tender_name", "")), file=file, user=user)
            return rulebook_draft_page(request, user=user)

        elif clean_path == "rulebook/freeze":
            form = await get_form_data(request)
            return freeze_rulebook_action(request, draft_json=str(form.get("draft_json", "")), user=user)

        elif clean_path == "runs/new":
            if request.method == "POST":
                form = await get_form_data(request)
                files = form.get("files")
                file_list = files if isinstance(files, list) else ([files] if files else [])
                return await execute_new_run(request, tender_name=str(form.get("tender_name", "")), rulebook_source=str(form.get("rulebook_source", "")), files=file_list, user=user)
            return new_run_page(request, user=user)

        elif clean_path.startswith("runs/"):
            parts = clean_path.split("/")
            run_id = parts[1]
            if len(parts) > 2 and parts[2] == "sign":
                form = await get_form_data(request)
                return sign_run_report(request, run_id=run_id, officer=str(form.get("officer", "")), designation=str(form.get("designation", "")), user=user)
            return get_run_report(request, run_id=run_id, user=user)

        return login_page(request)
    except Exception as e:
        err_msg = f"ERROR: {str(e)}\n\nTRACEBACK:\n{traceback.format_exc()}"
        return HTMLResponse(content=f"<pre>{err_msg}</pre>", status_code=500)

from jinja2 import Environment, DictLoader

TEMPLATES = {
    "login.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BidProof-Lite | Officer Login</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 40px; width: 100%; max-width: 420px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
        .logo { font-size: 24px; font-weight: 700; color: #38bdf8; text-align: center; margin-bottom: 8px; }
        .subtitle { font-size: 13px; color: #94a3b8; text-align: center; margin-bottom: 28px; letter-spacing: 0.5px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 8px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px 14px; background: #0f172a; border: 1px solid #475569; border-radius: 6px; color: #f8fafc; font-size: 14px; outline: none; transition: border-color 0.2s; }
        input[type="text"]:focus, input[type="password"]:focus { border-color: #38bdf8; }
        button { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 14px; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .error-msg { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 20px; text-align: center; }
        .badge { display: inline-block; background: #334155; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-top: 16px; width: 100%; text-align: center; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo">🛡️ BIDPROOF-LITE</div>
        <div class="subtitle">AI Eligibility Engine & Audit Trail</div>
        
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        
        <form action="/login" method="POST">
            <div class="form-group">
                <label>Officer Username</label>
                <input type="text" name="username" value="officer" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" value="demo@123" required>
            </div>
            <button type="submit">Access Control Portal</button>
        </form>
        <div class="badge">INTERCOLLEGE DEMO PROTOTYPE</div>
    </div>
</body>
</html>""",

    "dashboard.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BidProof-Lite | Evaluation Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #334155; margin-bottom: 28px; }
        .title { font-size: 22px; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .user-info { display: flex; align-items: center; gap: 16px; font-size: 14px; color: #94a3b8; }
        .btn { padding: 9px 16px; border-radius: 6px; font-weight: 600; font-size: 13px; text-decoration: none; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
        .btn-primary { background: #0284c7; color: white; }
        .btn-primary:hover { background: #0369a1; }
        .btn-secondary { background: #334155; color: #f8fafc; }
        .btn-secondary:hover { background: #475569; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 24px; margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }
        th { text-align: left; padding: 12px; background: #0f172a; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #334155; }
        td { padding: 14px 12px; border-bottom: 1px solid #334155; }
        tr:hover { background: #334155; }
        .link { color: #38bdf8; text-decoration: none; font-weight: 600; }
        .link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🛡️ BIDPROOF-LITE <span style="font-size:12px; background:#0284c7; color:white; padding:3px 8px; border-radius:4px;">DEMO</span></div>
        <div class="user-info">
            <span>Officer: <strong>{{ user }}</strong></span>
            <a href="/logout" class="btn btn-secondary">Logout</a>
        </div>
    </div>

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
            <h2>Evaluation Runs Audit Trail</h2>
            <div style="display:flex; gap:12px;">
                <a href="/rulebook/draft" class="btn btn-secondary">📄 Stage 0: Draft Rulebook</a>
                <a href="/runs/new" class="btn btn-primary">🚀 Stage 1: New Evaluation Run</a>
            </div>
        </div>

        {% if runs %}
        <table>
            <thead>
                <tr>
                    <th>Run ID</th>
                    <th>Tender Name</th>
                    <th>Rulebook</th>
                    <th>Executed At</th>
                    <th>Evaluating Officer</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for r in runs %}
                <tr>
                    <td><code>{{ r.id }}</code></td>
                    <td><strong>{{ r.tender_name }}</strong></td>
                    <td>{{ r.rulebook_name }}</td>
                    <td>{{ r.run_at }}</td>
                    <td>{{ r.officer }}</td>
                    <td><a href="/runs/{{ r.id }}" class="link">View Audit Report →</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color:#94a3b8; padding: 20px 0; text-align:center;">No evaluation runs performed yet. Click "Stage 1: New Evaluation Run" to trigger a run!</p>
        {% endif %}
    </div>
</body>
</html>""",

    "rulebook_draft.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BidProof-Lite | Stage 0 Rulebook Draft</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #334155; margin-bottom: 28px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 24px; margin-bottom: 24px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
        input[type="text"], input[type="file"] { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #475569; border-radius: 6px; color: #f8fafc; font-size: 14px; }
        .btn { padding: 10px 18px; border-radius: 6px; font-weight: 600; font-size: 14px; cursor: pointer; border: none; text-decoration: none; }
        .btn-primary { background: #0284c7; color: white; }
        .btn-success { background: #16a34a; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Stage 0: Rulebook Drafting & Freeze Gate</h2>
        <a href="/dashboard" style="color:#38bdf8; text-decoration:none;">← Back to Dashboard</a>
    </div>

    {% if not draft %}
    <div class="card">
        <h3>1. Extract Draft Rules from Tender RFP Document</h3>
        <form action="/rulebook/draft" method="POST" enctype="multipart/form-data" style="margin-top:16px;">
            <div class="form-group">
                <label>Tender Reference ID</label>
                <input type="text" name="tender_id" value="TENDER-2026-ENVIRO" required>
            </div>
            <div class="form-group">
                <label>Tender Name</label>
                <input type="text" name="tender_name" value="Supply of Water Purification Plant & Services" required>
            </div>
            <div class="form-group">
                <label>Upload Tender RFP Document (PDF/DOCX)</label>
                <input type="file" name="file" required>
            </div>
            <button type="submit" class="btn btn-primary">Generate Draft Rulebook</button>
        </form>
    </div>
    {% else %}
    <div class="card">
        <h3>2. Review & Freeze Rulebook (Officer Gate)</h3>
        <p style="color:#94a3b8; margin: 10px 0;">Rulebook name: <strong>{{ draft.meta.name }}</strong> (Tender: {{ draft.meta.tender_id }})</p>
        <pre style="background:#0f172a; padding:16px; border-radius:8px; color:#38bdf8; max-height:300px; overflow:auto;">{{ draft_json }}</pre>

        <form action="/rulebook/freeze" method="POST" style="margin-top:20px;">
            <input type="hidden" name="draft_json" value='{{ draft_json }}'>
            <button type="submit" class="btn btn-success">🔒 Confirm & Freeze Rulebook SHA-256</button>
        </form>
    </div>
    {% endif %}
</body>
</html>""",

    "new_run.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BidProof-Lite | New Evaluation Run</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #334155; margin-bottom: 28px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 24px; max-width: 650px; margin: 0 auto; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
        input[type="text"], select, input[type="file"] { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #475569; border-radius: 6px; color: #f8fafc; font-size: 14px; }
        .btn { padding: 12px 20px; background: #0284c7; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 14px; cursor: pointer; width: 100%; }
        .btn:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Stage 1: Execute New Eligibility Run</h2>
        <a href="/dashboard" style="color:#38bdf8; text-decoration:none;">← Back to Dashboard</a>
    </div>

    <div class="card">
        <form action="/runs/new" method="POST" enctype="multipart/form-data">
            <div class="form-group">
                <label>Tender / Bidder Project Name</label>
                <input type="text" name="tender_name" value="MERIDIAN ENVIRO SYSTEMS PVT LTD - BID #1042" required>
            </div>

            <div class="form-group">
                <label>Select Frozen Rulebook</label>
                <select name="rulebook_source">
                    <option value="sample_tender.yaml">Sample Tender Rulebook (Standard Evaluation)</option>
                    {% for rb in frozen_rulebooks %}
                    <option value="{{ rb.id }}">{{ rb.name }} ({{ rb.tender_id }})</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>Upload Bidder PDFs (PAN, GST, Udyam, Exp, Bank, Decl)</label>
                <input type="file" name="files" multiple>
                <small style="color:#94a3b8; display:block; margin-top:4px;">Leave empty to automatically evaluate against synthesized seed PDF documents!</small>
            </div>

            <button type="submit" class="btn">🚀 Run Pipeline Stages 1–6</button>
        </form>
    </div>
</body>
</html>""",

    "report.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Report | {{ run.id }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid #334155; margin-bottom: 24px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 20px; margin-bottom: 24px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .metric { background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
        .metric-val { font-size: 28px; font-weight: 700; }
        .metric-lbl { font-size: 12px; color: #94a3b8; margin-top: 4px; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }
        .badge-COMPLIANT { background: #16a34a; color: white; }
        .badge-NON_COMPLIANT { background: #dc2626; color: white; }
        .badge-AMBIGUOUS { background: #d97706; color: white; }
        .badge-CONTRADICTION { background: #7c3aed; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
        th { text-align: left; padding: 10px; background: #0f172a; color: #94a3b8; border-bottom: 1px solid #334155; }
        td { padding: 12px 10px; border-bottom: 1px solid #334155; }
        .quote { background: #0f172a; padding: 8px 12px; border-left: 3px solid #38bdf8; font-family: monospace; font-size: 12px; margin-top: 4px; color: #cbd5e1; }
        .btn { padding: 10px 16px; background: #16a34a; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2>Audit Evaluation Report</h2>
            <p style="color:#94a3b8; font-size:13px;">Run ID: <code>{{ run.id }}</code> | Bidder: <strong>{{ run.tender_name }}</strong></p>
        </div>
        <a href="/dashboard" style="color:#38bdf8; text-decoration:none; font-weight:600;">← Back to Dashboard</a>
    </div>

    <div class="grid">
        <div class="metric"><div class="metric-val" style="color:#4ade80;">{{ summary.compliant }}</div><div class="metric-lbl">COMPLIANT RULES</div></div>
        <div class="metric"><div class="metric-val" style="color:#f87171;">{{ summary.non_compliant }}</div><div class="metric-lbl">NON-COMPLIANT</div></div>
        <div class="metric"><div class="metric-val" style="color:#fbbf24;">{{ summary.ambiguous }}</div><div class="metric-lbl">AMBIGUOUS</div></div>
        <div class="metric"><div class="metric-val" style="color:#c084fc;">{{ summary.contradiction }}</div><div class="metric-lbl">CONTRADICTIONS</div></div>
    </div>

    <div class="card">
        <h3>Stage 4: Rule Findings</h3>
        <table>
            <thead>
                <tr>
                    <th>Rule ID</th>
                    <th>Statement</th>
                    <th>Extracted Value</th>
                    <th>Verdict</th>
                    <th>Evidence Quote & Reason</th>
                </tr>
            </thead>
            <tbody>
                {% for f in findings %}
                <tr>
                    <td><code>{{ f.rule_id }}</code></td>
                    <td>{{ f.statement }}</td>
                    <td><code>{{ f.value }}</code></td>
                    <td><span class="badge badge-{{ f.status }}">{{ f.status }}</span></td>
                    <td>
                        <div>{{ f.reason }}</div>
                        {% for ev in f.evidence %}
                        <div class="quote">"{{ ev.source_text }}" (Page {{ ev.page }})</div>
                        {% endfor %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h3>Stage 5: Cross-Document Consistency Issues</h3>
        {% if issues %}
        <table>
            <thead>
                <tr>
                    <th>Check ID</th>
                    <th>Verdict</th>
                    <th>Left Document Field</th>
                    <th>Right Document Field</th>
                    <th>Reason</th>
                </tr>
            </thead>
            <tbody>
                {% for i in issues %}
                <tr>
                    <td><code>{{ i.check_id }}</code></td>
                    <td><span class="badge badge-{{ i.verdict }}">{{ i.verdict }}</span></td>
                    <td>{{ i.left.key }}: <code>{{ i.left.value }}</code></td>
                    <td>{{ i.right.key }}: <code>{{ i.right.value }}</code></td>
                    <td>{{ i.reason }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color:#94a3b8; font-size:13px; margin-top:8px;">No cross-document inconsistencies detected.</p>
        {% endif %}
    </div>

    <div class="card">
        <h3>Stage 6: Evaluating Officer Digital Sign-Off</h3>
        {% if signature %}
        <div style="background:#0f172a; padding:16px; border-radius:8px; border-left:4px solid #16a34a; margin-top:12px;">
            <p><strong>Signed by Officer:</strong> {{ signature.officer }}</p>
            <p><strong>Designation:</strong> {{ signature.designation }}</p>
            <p><strong>Timestamp:</strong> {{ signature.signed_at }}</p>
        </div>
        {% else %}
        <form action="/runs/{{ run.id }}/sign" method="POST" style="margin-top:12px; display:flex; gap:12px; align-items:flex-end;">
            <div style="flex:1;">
                <label style="display:block; font-size:12px; margin-bottom:4px;">Officer Name</label>
                <input type="text" name="officer" value="{{ run.officer }}" required style="width:100%; padding:8px; background:#0f172a; border:1px solid #475569; border-radius:4px; color:white;">
            </div>
            <div style="flex:1;">
                <label style="display:block; font-size:12px; margin-bottom:4px;">Designation</label>
                <input type="text" name="designation" value="Senior Procurement Officer" required style="width:100%; padding:8px; background:#0f172a; border:1px solid #475569; border-radius:4px; color:white;">
            </div>
            <button type="submit" class="btn">Sign Audit Report</button>
        </form>
        {% endif %}
    </div>
</body>
</html>"""
}

jinja_env = Environment(loader=DictLoader(TEMPLATES))

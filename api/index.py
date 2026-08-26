from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BidProof-Lite | Live</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 40px; text-align: center; max-width: 480px; }
        h1 { color: #38bdf8; margin-bottom: 12px; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 24px; }
        .badge { background: #16a34a; color: white; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 12px; display: inline-block; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ BIDPROOF-LITE</h1>
        <p>AI Eligibility Verification & Audit Trail System</p>
        <div class="badge">SYSTEM READY & DEPLOYED ON VERCEL</div>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

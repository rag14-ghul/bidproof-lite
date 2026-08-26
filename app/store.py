import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import settings
from app.models import StepTrace, ExtractedField, Finding, ConsistencyIssue, Signature

class DataStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pass_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rulebooks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version INTEGER NOT NULL,
                tender_id TEXT NOT NULL,
                bid_date TEXT NOT NULL,
                source_doc_sha TEXT,
                confirmed_by TEXT,
                confirmed_at TEXT,
                yaml_content TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                tender_name TEXT NOT NULL,
                rulebook_name TEXT NOT NULL,
                rulebook_sha TEXT NOT NULL,
                run_at TEXT NOT NULL,
                officer TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                pages INTEGER NOT NULL,
                doc_type TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fields (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                doc_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                page INTEGER NOT NULL,
                source_text TEXT NOT NULL,
                confidence REAL NOT NULL,
                extractor TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                status TEXT NOT NULL,
                value TEXT,
                expected TEXT,
                reason TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                check_id TEXT NOT NULL,
                verdict TEXT NOT NULL,
                left_json TEXT NOT NULL,
                right_json TEXT NOT NULL,
                reason TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                seq INTEGER NOT NULL,
                stage TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT NOT NULL,
                ts TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                officer TEXT NOT NULL,
                designation TEXT NOT NULL,
                signed_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );
            """)

            conn.commit()

    def insert_user(self, username: str, pass_hash: str, role: str = "officer"):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO users (username, pass_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username, pass_hash, role, datetime.now().isoformat())
            )
            conn.commit()

    def insert_rulebook(self, rulebook_id: str, name: str, version: int, tender_id: str,
                        bid_date: str, yaml_content: str, source_doc_sha: Optional[str] = None,
                        confirmed_by: Optional[str] = None, confirmed_at: Optional[str] = None):
        with self.get_connection() as conn:
            conn.cursor().execute(
                """INSERT INTO rulebooks 
                   (id, name, version, tender_id, bid_date, source_doc_sha, confirmed_by, confirmed_at, yaml_content)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (rulebook_id, name, version, tender_id, bid_date, source_doc_sha, confirmed_by, confirmed_at, yaml_content)
            )
            conn.commit()

    def insert_run(self, run_id: str, tender_name: str, rulebook_name: str, rulebook_sha: str, officer: str):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO runs (id, tender_name, rulebook_name, rulebook_sha, run_at, officer) VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, tender_name, rulebook_name, rulebook_sha, datetime.now().isoformat(), officer)
            )
            conn.commit()

    def insert_document(self, doc_id: str, run_id: str, filename: str, sha256: str, pages: int, doc_type: str):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO documents (id, run_id, filename, sha256, pages, doc_type) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, run_id, filename, sha256, pages, doc_type)
            )
            conn.commit()

    def insert_field(self, field_id: str, run_id: str, doc_id: str, field: ExtractedField):
        with self.get_connection() as conn:
            conn.cursor().execute(
                """INSERT INTO fields 
                   (id, run_id, doc_id, key, value, page, source_text, confidence, extractor)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (field_id, run_id, doc_id, field.key, field.value, field.page, field.source_text, field.confidence, field.extractor)
            )
            conn.commit()

    def insert_finding(self, finding_id: str, run_id: str, finding: Finding):
        with self.get_connection() as conn:
            evidence_json = json.dumps([e.model_dump() for e in finding.evidence])
            conn.cursor().execute(
                """INSERT INTO findings 
                   (id, run_id, rule_id, status, value, expected, reason, evidence_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (finding_id, run_id, finding.rule_id, finding.status, finding.value, finding.expected, finding.reason, evidence_json)
            )
            conn.commit()

    def insert_issue(self, issue_id: str, run_id: str, issue: ConsistencyIssue):
        with self.get_connection() as conn:
            conn.cursor().execute(
                """INSERT INTO issues 
                   (id, run_id, check_id, verdict, left_json, right_json, reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (issue_id, run_id, issue.check_id, issue.verdict, json.dumps(issue.left), json.dumps(issue.right), issue.reason)
            )
            conn.commit()

    def insert_step(self, run_id: str, step: StepTrace):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO steps (run_id, seq, stage, action, detail, ts) VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, step.seq, step.stage, step.action, step.detail, step.ts)
            )
            conn.commit()

    def insert_signature(self, run_id: str, officer: str, designation: str) -> Signature:
        signed_at = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO signatures (run_id, officer, designation, signed_at) VALUES (?, ?, ?, ?)",
                (run_id, officer, designation, signed_at)
            )
            conn.commit()
            sig_id = cursor.lastrowid
            return Signature(id=sig_id, run_id=run_id, officer=officer, designation=designation, signed_at=signed_at)

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
            return dict(row) if row else None

    def get_runs(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM runs ORDER BY run_at DESC").fetchall()
            return [dict(r) for r in rows]

    def get_findings(self, run_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM findings WHERE run_id = ?", (run_id,)).fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d["evidence"] = json.loads(d["evidence_json"]) if d.get("evidence_json") else []
                res.append(d)
            return res

    def get_issues(self, run_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM issues WHERE run_id = ?", (run_id,)).fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d["left"] = json.loads(d["left_json"]) if d.get("left_json") else {}
                d["right"] = json.loads(d["right_json"]) if d.get("right_json") else {}
                res.append(d)
            return res

    def get_steps(self, run_id: str) -> List[StepTrace]:
        with self.get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM steps WHERE run_id = ? ORDER BY seq ASC", (run_id,)).fetchall()
            return [StepTrace(seq=r["seq"], ts=r["ts"], stage=r["stage"], action=r["action"], detail=r["detail"]) for r in rows]

    def get_signature(self, run_id: str) -> Optional[Signature]:
        with self.get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM signatures WHERE run_id = ? ORDER BY id DESC LIMIT 1", (run_id,)).fetchone()
            return Signature(**dict(row)) if row else None

    def get_rulebook_yaml(self, rulebook_id_or_sha: str) -> Optional[str]:
        with self.get_connection() as conn:
            row = conn.cursor().execute(
                "SELECT yaml_content FROM rulebooks WHERE id = ? OR source_doc_sha = ?",
                (rulebook_id_or_sha, rulebook_id_or_sha)
            ).fetchone()
            return row["yaml_content"] if row else None

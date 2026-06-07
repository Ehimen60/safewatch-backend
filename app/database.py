import sqlite3
import json
import os
from typing import List, Optional, Dict, Any

DB_PATH = "safewatch.db"

def init_db():
    """Initialise the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            site_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            ppe_requirements TEXT NOT NULL,
            workers TEXT NOT NULL,
            summary TEXT NOT NULL,
            total_workers INTEGER DEFAULT 0,
            compliance_rate REAL DEFAULT 0,
            site_status TEXT DEFAULT 'UNKNOWN'
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database ready")

def save_report(report: Dict[str, Any]) -> bool:
    """Save analysis report to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        summary = report.get("summary", {})
        cursor.execute("""
            INSERT INTO reports (
                id, site_name, filename, timestamp,
                ppe_requirements, workers, summary,
                total_workers, compliance_rate, site_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report["id"],
            report["site_name"],
            report["filename"],
            report["timestamp"],
            json.dumps(report["ppe_requirements"]),
            json.dumps(report["workers"]),
            json.dumps(summary),
            summary.get("total_workers", 0),
            summary.get("compliance_rate", 0),
            summary.get("site_status", "UNKNOWN")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def get_reports(limit: int = 20) -> List[Dict]:
    """Get list of recent reports."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, site_name, filename, timestamp,
               total_workers, compliance_rate, site_status
        FROM reports
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "site_name": r[1],
            "filename": r[2],
            "timestamp": r[3],
            "total_workers": r[4],
            "compliance_rate": r[5],
            "site_status": r[6]
        }
        for r in rows
    ]

def get_report_by_id(report_id: str) -> Optional[Dict]:
    """Get full report by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "site_name": row[1],
        "filename": row[2],
        "timestamp": row[3],
        "ppe_requirements": json.loads(row[4]),
        "workers": json.loads(row[5]),
        "summary": json.loads(row[6]),
        "total_workers": row[7],
        "compliance_rate": row[8],
        "site_status": row[9]
    }

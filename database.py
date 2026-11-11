import sqlite3
from pathlib import Path
from typing import List, Dict

DB_DIR = Path.home() / ".shift_tracker"
DB_PATH = DB_DIR / "data.db"

def get_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                hours REAL NOT NULL CHECK(hours > 0),
                rate REAL NOT NULL CHECK(rate >= 0),
                total REAL NOT NULL,
                note TEXT DEFAULT ''
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON shifts(date)")

def upsert_shift(date: str, hours: float, rate: float, note: str) -> bool:
    total = round(hours * rate, 2)
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO shifts (date, hours, rate, total, note)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                hours = excluded.hours,
                rate = excluded.rate,
                total = excluded.total,
                note = excluded.note
            """, (date, hours, rate, total, note))
        return True
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def get_monthly_stats(year: int, month: int) -> Dict[str, float]:
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT COALESCE(SUM(hours), 0.0) as total_hours, 
                   COALESCE(SUM(total), 0.0) as total_earnings
            FROM shifts
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """, (f"{year:04d}", f"{month:02d}"))
        row = cursor.fetchone()
        return {
            "total_hours": float(row["total_hours"]),
            "total_earnings": float(row["total_earnings"])
        }

def get_shifts_by_month(year: int, month: int) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT date, hours, rate, total, note
            FROM shifts
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC
        """, (f"{year:04d}", f"{month:02d}"))
        return [dict(row) for row in cursor.fetchall()]

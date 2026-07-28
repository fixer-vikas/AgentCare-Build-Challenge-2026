import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = os.environ.get("DATABASE_URL", "sqlite://")


def seed_sample_data(db_path: str | None = None) -> None:
    target = db_path or os.path.join(ROOT, "app", "agentcare.sqlite3")
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("INSERT OR IGNORE INTO users (role, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                 ("staff", "Dr. Priya Rao", "staff@example.com", generate_password_hash("staffpass"), "2026-01-01T00:00:00"))
    conn.execute("INSERT OR IGNORE INTO departments (name, description, created_at) VALUES (?, ?, ?)",
                 ("Cardiology", "Heart and vascular care", "2026-01-01T00:00:00"))
    conn.execute("INSERT OR IGNORE INTO departments (name, description, created_at) VALUES (?, ?, ?)",
                 ("Neurology", "Brain and nervous system care", "2026-01-01T00:00:00"))
    conn.execute("INSERT OR IGNORE INTO doctors (department_id, name, specialty, availability, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                 (1, "Dr. Maya Shah", "Cardiology", "Mon/Wed/Fri", 1, "2026-01-01T00:00:00"))
    conn.execute("INSERT OR IGNORE INTO doctors (department_id, name, specialty, availability, active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                 (2, "Dr. Alan Kim", "Neurology", "Tue/Thu", 1, "2026-01-01T00:00:00"))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_sample_data()

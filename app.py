"""Thursday Cookie Lab signup server.

Serves the signup page and a small JSON API from one address.

Storage:
  - When the DATABASE_URL setting is present (on Render), signups are saved in PostgreSQL.
  - Otherwise (on your own computer), they are saved in a local SQLite file, signups.db.

Optional setting:
  - LEADER_KEY: a code club leaders type on the page to mark attendance.
    When it isn't set, attendance marking is turned off.
"""

import os
import secrets
import sqlite3
from datetime import date, datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory

SESSIONS = [
    "Chocolate Chip Cookies (3:00 PM)",
    "Sugar Cookies (4:00 PM)",
    "Oatmeal Cookies (5:00 PM)",
]
SPOTS_PER_SESSION = 10
THURSDAY = 3  # Monday is 0
WEEKS_AHEAD = 4

HERE = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
LEADER_KEY = os.environ.get("LEADER_KEY", "").strip()

app = Flask(__name__, static_folder=None)


# ---------- Database ----------

if DATABASE_URL:
    import psycopg2

    USING = "PostgreSQL"
    ID_COLUMN = "SERIAL PRIMARY KEY"
    IntegrityErrors = (psycopg2.IntegrityError,)

    def connect():
        return psycopg2.connect(DATABASE_URL)

    def sql(text):
        return text  # psycopg2 uses %s placeholders

else:
    USING = "SQLite"
    ID_COLUMN = "INTEGER PRIMARY KEY AUTOINCREMENT"
    IntegrityErrors = (sqlite3.IntegrityError,)
    SQLITE_PATH = os.path.join(HERE, "signups.db")

    def connect():
        return sqlite3.connect(SQLITE_PATH)

    def sql(text):
        return text.replace("%s", "?")  # sqlite3 uses ? placeholders


def create_tables():
    """Create the table if it's missing. Never deletes existing signups."""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS signups (
                id {ID_COLUMN},
                name TEXT NOT NULL,
                name_key TEXT NOT NULL,
                session TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                owner_token TEXT,
                attended BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        # One spot per person per Thursday, even if two requests arrive at once
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS signups_one_per_thursday ON signups (date, name_key)"
        )
        conn.commit()
    finally:
        conn.close()


create_tables()
print(f"Thursday Cookie Lab is saving signups with {USING}.", flush=True)


# ---------- Helpers ----------

COLUMNS = "id, name, session, date, attended, owner_token"


def clean_name(name):
    """'  brock   powell ' -> 'brock powell'"""
    return " ".join(str(name or "").split())[:80]


def name_key(name):
    return clean_name(name).lower()


def owner_token():
    token = request.headers.get("X-Owner-Token", "").strip()
    return token[:100] or None


def belongs_to_viewer(row_owner, token):
    # Signups without an owner (examples) can be changed by anyone who knows the name and slot
    return row_owner is None or (token is not None and secrets.compare_digest(row_owner, token))


def to_json(row, token):
    signup_id, name, session, day, attended, row_owner = row
    return {
        "id": signup_id,
        "name": name,
        "session": session,
        "date": day,
        "attended": bool(attended),
        "yours": belongs_to_viewer(row_owner, token),
    }


def server_today():
    # The server runs on UTC; allow one day of slack so US evenings still count as "today"
    return datetime.now(timezone.utc).date() - timedelta(days=1)


def valid_signup_date(text):
    """A Thursday from this week through the next few weeks."""
    try:
        day = date.fromisoformat(str(text))
    except ValueError:
        return None
    if day.weekday() != THURSDAY:
        return None
    if day < server_today() or day > server_today() + timedelta(weeks=WEEKS_AHEAD + 1):
        return None
    return day.isoformat()


def error(code, status, **extra):
    return jsonify({"error": code, **extra}), status


def read_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


# ---------- Pages ----------

@app.get("/")
def page():
    return send_from_directory(HERE, "index.html")


@app.get("/healthz")
def health():
    return {"ok": True}


# ---------- API ----------

@app.get("/api/config")
def config():
    return {
        "sessions": SESSIONS,
        "spotsPerSession": SPOTS_PER_SESSION,
        "leaderEnabled": bool(LEADER_KEY),
    }


@app.get("/api/signups")
def list_signups():
    token = owner_token()
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT {COLUMNS} FROM signups ORDER BY date, name_key")
        rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify([to_json(row, token) for row in rows])


@app.post("/api/signups")
def sign_up():
    """Sign up, or switch your own spot to a different session on the same Thursday."""
    body = read_body()
    name = clean_name(body.get("name"))
    session = body.get("session")
    day = valid_signup_date(body.get("date"))
    if not name:
        return error("name_missing", 400)
    if session not in SESSIONS:
        return error("session_invalid", 400)
    if not day:
        return error("date_invalid", 400)

    token = owner_token()
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(
            sql(f"SELECT {COLUMNS} FROM signups WHERE date = %s AND name_key = %s"),
            (day, name_key(name)),
        )
        existing = cur.fetchone()
        if existing:
            existing_json = to_json(existing, token)
            if existing_json["session"] == session:
                return error("duplicate", 409, existing=existing_json)
            if not existing_json["yours"]:
                return error("taken", 403, existing=existing_json)

        cur.execute(
            sql("SELECT COUNT(*) FROM signups WHERE date = %s AND session = %s"),
            (day, session),
        )
        if cur.fetchone()[0] >= SPOTS_PER_SESSION:
            return error("full", 409, session=session, date=day)

        if existing:
            cur.execute(
                sql("UPDATE signups SET session = %s, name = %s, attended = FALSE WHERE id = %s"),
                (session, name, existing[0]),
            )
            signup_id = existing[0]
        else:
            created = datetime.now(timezone.utc).isoformat()
            params = (name, name_key(name), session, day, created, token)
            insert = (
                "INSERT INTO signups (name, name_key, session, date, created_at, owner_token) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            if USING == "PostgreSQL":
                cur.execute(insert + " RETURNING id", params)
                signup_id = cur.fetchone()[0]
            else:
                cur.execute(sql(insert), params)
                signup_id = cur.lastrowid
        conn.commit()
    except IntegrityErrors:
        conn.rollback()
        return error("duplicate", 409)
    finally:
        conn.close()

    return jsonify(
        {
            "signup": {"id": signup_id, "name": name, "session": session, "date": day},
            "switchedFrom": existing[2] if existing else None,
        }
    ), 201


@app.post("/api/signups/cancel")
def cancel():
    """Cancel your own signup by giving the same name, Thursday and session."""
    body = read_body()
    name = clean_name(body.get("name"))
    session = body.get("session")
    day = str(body.get("date") or "")
    token = owner_token()

    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(
            sql(f"SELECT {COLUMNS} FROM signups WHERE date = %s AND name_key = %s AND session = %s"),
            (day, name_key(name), session),
        )
        row = cur.fetchone()
        if not row:
            return error("not_found", 404)
        if not belongs_to_viewer(row[5], token):
            return error("not_yours", 403)
        cur.execute(sql("DELETE FROM signups WHERE id = %s"), (row[0],))
        conn.commit()
    finally:
        conn.close()
    return {"canceled": True}


def leader_ok():
    given = request.headers.get("X-Leader-Key", "")
    return bool(LEADER_KEY) and secrets.compare_digest(given, LEADER_KEY)


@app.post("/api/leader")
def check_leader():
    if not leader_ok():
        return error("wrong_code", 403)
    return {"ok": True}


@app.patch("/api/signups/<int:signup_id>/attendance")
def mark_attendance(signup_id):
    """Club leaders mark who came, on Thursdays that have arrived."""
    if not leader_ok():
        return error("wrong_code", 403)
    attended = bool(read_body().get("attended"))
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql("SELECT date FROM signups WHERE id = %s"), (signup_id,))
        row = cur.fetchone()
        if not row:
            return error("not_found", 404)
        if row[0] > (server_today() + timedelta(days=1)).isoformat():
            return error("not_yet", 409)
        cur.execute(sql("UPDATE signups SET attended = %s WHERE id = %s"), (attended, signup_id))
        conn.commit()
    finally:
        conn.close()
    return {"attended": attended}


if __name__ == "__main__":
    # Local run: python app.py  ->  http://localhost:8000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

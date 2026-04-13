"""
Database layer — async SQLite via aiosqlite.

All SQL is in this module. The rest of the app works with Pydantic models.

Schema change (Phase 3): dimension_assessments now stores selected_level (1-4)
per dimension, plus optional notes. The perspective chosen_level can be derived
from dimension selections or overridden by the group.
"""

import aiosqlite
import bcrypt
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import os

from .reference_data import PERSPECTIVE_KEYS, DIMENSION_KEYS

DB_PATH = Path(os.environ.get("DB_PATH", str(Path(__file__).parent.parent / "mognadsdialog.db")))


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                title TEXT NOT NULL,
                facilitator TEXT NOT NULL DEFAULT '',
                participants TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                finalized_at TEXT
            );

            CREATE TABLE IF NOT EXISTS perspective_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES assessments(id),
                perspective_key TEXT NOT NULL,
                chosen_level INTEGER,
                suggested_level INTEGER,
                reasoning TEXT NOT NULL DEFAULT '',
                UNIQUE(assessment_id, perspective_key)
            );

            CREATE TABLE IF NOT EXISTS dimension_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES assessments(id),
                perspective_key TEXT NOT NULL,
                dimension_key TEXT NOT NULL,
                selected_level INTEGER,
                notes TEXT NOT NULL DEFAULT '',
                UNIQUE(assessment_id, perspective_key, dimension_key)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            );

            -- Survey (unit-level maturity measurement)
            CREATE TABLE IF NOT EXISTS surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                title TEXT NOT NULL,
                profile_key TEXT NOT NULL DEFAULT '',
                respondent_name TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS survey_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL REFERENCES surveys(id),
                question_id TEXT NOT NULL,
                selected_level INTEGER,
                comment TEXT NOT NULL DEFAULT '',
                UNIQUE(survey_id, question_id)
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'participant',
                created_at TEXT NOT NULL
            );
        """)
        # Seed default admin if no users exist
        cursor = await db.execute("SELECT COUNT(*) as c FROM users")
        row = await cursor.fetchone()
        if row["c"] == 0:
            pw_hash = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            await db.execute(
                "INSERT INTO users (username, password_hash, display_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                ("admin", pw_hash, "Administratör", "admin", _now()),
            )
        await db.commit()
    finally:
        await db.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    if s is None:
        return None
    return datetime.fromisoformat(s)


# ── Organizations ───────────────────────────────────────────────────

async def create_organization(name: str, description: str = "") -> dict:
    db = await get_db()
    try:
        now = _now()
        cursor = await db.execute(
            "INSERT INTO organizations (name, description, created_at) VALUES (?, ?, ?)",
            (name, description, now),
        )
        await db.commit()
        return {"id": cursor.lastrowid, "name": name, "description": description, "created_at": _parse_dt(now)}
    finally:
        await db.close()


async def list_organizations() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM organizations ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [
            {"id": r["id"], "name": r["name"], "description": r["description"], "created_at": _parse_dt(r["created_at"])}
            for r in rows
        ]
    finally:
        await db.close()


async def get_organization(org_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
        r = await cursor.fetchone()
        if r is None:
            return None
        return {"id": r["id"], "name": r["name"], "description": r["description"], "created_at": _parse_dt(r["created_at"])}
    finally:
        await db.close()


# ── Assessments ─────────────────────────────────────────────────────

async def create_assessment(organization_id: int, title: str, facilitator: str = "", participants: str = "") -> dict:
    db = await get_db()
    try:
        now = _now()
        cursor = await db.execute(
            "INSERT INTO assessments (organization_id, title, facilitator, participants, status, created_at) VALUES (?, ?, ?, ?, 'draft', ?)",
            (organization_id, title, facilitator, participants, now),
        )
        assessment_id = cursor.lastrowid

        for pk in PERSPECTIVE_KEYS:
            await db.execute(
                "INSERT INTO perspective_assessments (assessment_id, perspective_key, reasoning) VALUES (?, ?, '')",
                (assessment_id, pk),
            )
            for dk in DIMENSION_KEYS:
                await db.execute(
                    "INSERT INTO dimension_assessments (assessment_id, perspective_key, dimension_key, notes) VALUES (?, ?, ?, '')",
                    (assessment_id, pk, dk),
                )

        await db.commit()
        return {
            "id": assessment_id, "organization_id": organization_id, "title": title,
            "facilitator": facilitator, "participants": participants,
            "status": "draft", "created_at": _parse_dt(now), "finalized_at": None,
        }
    finally:
        await db.close()


async def list_assessments(organization_id: int) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM assessments WHERE organization_id = ? ORDER BY created_at DESC",
            (organization_id,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"], "organization_id": r["organization_id"], "title": r["title"],
                "facilitator": r["facilitator"], "participants": r["participants"],
                "status": r["status"], "created_at": _parse_dt(r["created_at"]),
                "finalized_at": _parse_dt(r["finalized_at"]),
            }
            for r in rows
        ]
    finally:
        await db.close()


async def get_assessment(assessment_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
        r = await cursor.fetchone()
        if r is None:
            return None
        return {
            "id": r["id"], "organization_id": r["organization_id"], "title": r["title"],
            "facilitator": r["facilitator"], "participants": r["participants"],
            "status": r["status"], "created_at": _parse_dt(r["created_at"]),
            "finalized_at": _parse_dt(r["finalized_at"]),
        }
    finally:
        await db.close()


async def update_assessment_status(assessment_id: int, status: str) -> bool:
    db = await get_db()
    try:
        finalized_at = _now() if status == "finalized" else None
        await db.execute(
            "UPDATE assessments SET status = ?, finalized_at = COALESCE(?, finalized_at) WHERE id = ?",
            (status, finalized_at, assessment_id),
        )
        await db.commit()
        return True
    finally:
        await db.close()


# ── Perspective Assessments ─────────────────────────────────────────

async def update_perspective_assessment(assessment_id: int, perspective_key: str, chosen_level: Optional[int], suggested_level: Optional[int], reasoning: str) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE perspective_assessments SET chosen_level = ?, suggested_level = ?, reasoning = ? WHERE assessment_id = ? AND perspective_key = ?",
            (chosen_level, suggested_level, reasoning, assessment_id, perspective_key),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def get_perspective_assessments(assessment_id: int) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM perspective_assessments WHERE assessment_id = ? ORDER BY perspective_key",
            (assessment_id,),
        )
        pa_rows = await cursor.fetchall()

        cursor = await db.execute(
            "SELECT * FROM dimension_assessments WHERE assessment_id = ?",
            (assessment_id,),
        )
        da_rows = await cursor.fetchall()

        da_by_perspective: dict[str, list[dict]] = {}
        for r in da_rows:
            pk = r["perspective_key"]
            if pk not in da_by_perspective:
                da_by_perspective[pk] = []
            da_by_perspective[pk].append({
                "perspective_key": r["perspective_key"],
                "dimension_key": r["dimension_key"],
                "selected_level": r["selected_level"],
                "notes": r["notes"],
            })

        result = []
        for r in pa_rows:
            pk = r["perspective_key"]
            result.append({
                "assessment_id": r["assessment_id"],
                "perspective_key": pk,
                "chosen_level": r["chosen_level"],
                "suggested_level": r["suggested_level"],
                "reasoning": r["reasoning"],
                "dimension_assessments": da_by_perspective.get(pk, []),
            })
        return result
    finally:
        await db.close()


# ── Dimension Assessments ───────────────────────────────────────────

async def update_dimension_assessment(assessment_id: int, perspective_key: str, dimension_key: str, selected_level: Optional[int], notes: str) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE dimension_assessments SET selected_level = ?, notes = ? WHERE assessment_id = ? AND perspective_key = ? AND dimension_key = ?",
            (selected_level, notes, assessment_id, perspective_key, dimension_key),
        )
        await db.commit()
        return True
    finally:
        await db.close()


# ── Comparison snapshots ────────────────────────────────────────────

async def get_assessment_snapshots(organization_id: int) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM assessments WHERE organization_id = ? ORDER BY created_at ASC",
            (organization_id,),
        )
        assessments = await cursor.fetchall()

        result = []
        for a in assessments:
            cursor = await db.execute(
                "SELECT perspective_key, chosen_level FROM perspective_assessments WHERE assessment_id = ?",
                (a["id"],),
            )
            levels = await cursor.fetchall()
            result.append({
                "assessment_id": a["id"],
                "title": a["title"],
                "created_at": _parse_dt(a["created_at"]),
                "status": a["status"],
                "levels": [{"perspective_key": r["perspective_key"], "chosen_level": r["chosen_level"]} for r in levels],
            })
        return result
    finally:
        await db.close()


# ── Settings ────────────────────────────────────────────────────────

async def get_settings() -> dict[str, str]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT key, value FROM settings")
        rows = await cursor.fetchall()
        return {r["key"]: r["value"] for r in rows}
    finally:
        await db.close()


# ── Surveys ──────────────────────────────────────────────────────────

async def create_survey(organization_id: int, title: str, profile_key: str, respondent_name: str) -> dict:
    db = await get_db()
    try:
        now = _now()
        cursor = await db.execute(
            "INSERT INTO surveys (organization_id, title, profile_key, respondent_name, status, created_at) VALUES (?, ?, ?, ?, 'draft', ?)",
            (organization_id, title, profile_key, respondent_name, now),
        )
        survey_id = cursor.lastrowid
        # Pre-create answers for applicable questions
        from .survey_data import get_questions_for_profile
        questions = get_questions_for_profile(profile_key)
        for q in questions:
            await db.execute(
                "INSERT INTO survey_answers (survey_id, question_id, comment) VALUES (?, ?, '')",
                (survey_id, q["id"]),
            )
        await db.commit()
        return {
            "id": survey_id, "organization_id": organization_id, "title": title,
            "profile_key": profile_key, "respondent_name": respondent_name,
            "status": "draft", "created_at": _parse_dt(now), "completed_at": None,
        }
    finally:
        await db.close()


async def list_surveys(organization_id: int) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM surveys WHERE organization_id = ? ORDER BY created_at DESC",
            (organization_id,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"], "organization_id": r["organization_id"], "title": r["title"],
                "profile_key": r["profile_key"], "respondent_name": r["respondent_name"],
                "status": r["status"], "created_at": _parse_dt(r["created_at"]),
                "completed_at": _parse_dt(r["completed_at"]),
            }
            for r in rows
        ]
    finally:
        await db.close()


async def get_survey(survey_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM surveys WHERE id = ?", (survey_id,))
        r = await cursor.fetchone()
        if r is None:
            return None
        return {
            "id": r["id"], "organization_id": r["organization_id"], "title": r["title"],
            "profile_key": r["profile_key"], "respondent_name": r["respondent_name"],
            "status": r["status"], "created_at": _parse_dt(r["created_at"]),
            "completed_at": _parse_dt(r["completed_at"]),
        }
    finally:
        await db.close()


async def get_survey_answers(survey_id: int) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM survey_answers WHERE survey_id = ?", (survey_id,),
        )
        rows = await cursor.fetchall()
        return [
            {"question_id": r["question_id"], "selected_level": r["selected_level"], "comment": r["comment"]}
            for r in rows
        ]
    finally:
        await db.close()


async def update_survey_answer(survey_id: int, question_id: str, selected_level: Optional[int], comment: str) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE survey_answers SET selected_level = ?, comment = ? WHERE survey_id = ? AND question_id = ?",
            (selected_level, comment, survey_id, question_id),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def complete_survey(survey_id: int) -> bool:
    db = await get_db()
    try:
        now = _now()
        await db.execute(
            "UPDATE surveys SET status = 'completed', completed_at = ? WHERE id = ?",
            (now, survey_id),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def set_setting(key: str, value: str) -> None:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (key, value, value),
        )
        await db.commit()
    finally:
        await db.close()


# ── Users ───────────────────────────────────────────────────────────

def _user_row_to_dict(r) -> dict:
    return {
        "id": r["id"], "username": r["username"], "display_name": r["display_name"],
        "role": r["role"], "created_at": _parse_dt(r["created_at"]),
    }


async def authenticate_user(username: str, password: str) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users WHERE username = ?", (username,))
        r = await cursor.fetchone()
        if r is None:
            return None
        if not bcrypt.checkpw(password.encode(), r["password_hash"].encode()):
            return None
        return _user_row_to_dict(r)
    finally:
        await db.close()


async def get_user(user_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        r = await cursor.fetchone()
        return _user_row_to_dict(r) if r else None
    finally:
        await db.close()


async def list_users() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at")
        rows = await cursor.fetchall()
        return [_user_row_to_dict(r) for r in rows]
    finally:
        await db.close()


async def create_user(username: str, password: str, display_name: str, role: str) -> dict:
    db = await get_db()
    try:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        now = _now()
        cursor = await db.execute(
            "INSERT INTO users (username, password_hash, display_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, pw_hash, display_name, role, now),
        )
        await db.commit()
        return {"id": cursor.lastrowid, "username": username, "display_name": display_name, "role": role, "created_at": _parse_dt(now)}
    finally:
        await db.close()


async def update_user(user_id: int, display_name: str, role: str, password: Optional[str] = None) -> bool:
    db = await get_db()
    try:
        if password:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            await db.execute(
                "UPDATE users SET display_name = ?, role = ?, password_hash = ? WHERE id = ?",
                (display_name, role, pw_hash, user_id),
            )
        else:
            await db.execute(
                "UPDATE users SET display_name = ?, role = ? WHERE id = ?",
                (display_name, role, user_id),
            )
        await db.commit()
        return True
    finally:
        await db.close()


async def delete_user(user_id: int) -> bool:
    db = await get_db()
    try:
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()
        return True
    finally:
        await db.close()

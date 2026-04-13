"""
FastAPI application — Mognadsdialog system support.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

from . import db
from .auth import (
    init_auth, create_session_token, COOKIE_NAME,
    get_current_user, require_auth, require_admin,
)
from .models import (
    OrganizationCreate, OrganizationResponse,
    AssessmentCreate, AssessmentResponse, AssessmentFullResponse,
    PerspectiveAssessmentUpdate,
    DimensionAssessmentUpdate,
    ReferenceDataResponse, PerspectiveInfo, DimensionInfo, MaturityLevelInfo,
    PerspectiveMaturityInfo, SubprocessInfo,
    GuidanceResponse, ComparisonResponse,
)
from .reference_data import (
    PERSPECTIVES, DIMENSIONS, MATURITY_LEVELS, DIMENSION_PROMPTS,
    PERSPECTIVE_KEYS, DIMENSION_KEYS, NEXT_LEVEL_GUIDANCE,
)
from .mcf_maturity_data import (
    PERSPECTIVE_MATURITY, PERSPECTIVE_CULTURE, PERSPECTIVE_SUBPROCESSES,
)

BASE_DIR = Path(__file__).parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    init_auth()
    yield


app = FastAPI(
    title="Mognadsdialog",
    description="Systemstöd för mognadsdialog enligt MSB/MCF-modellen",
    version="0.3.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ── Auth models ─────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4)
    display_name: str = Field(default="")
    role: str = Field(default="participant")

class UserUpdate(BaseModel):
    display_name: str = Field(default="")
    role: str = Field(default="participant")
    password: Optional[str] = Field(default=None)


# ── Auth endpoints ──────────────────────────────────────────────────

@app.post("/api/auth/login")
async def login(data: LoginRequest):
    user = await db.authenticate_user(data.username, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Fel användarnamn eller lösenord")
    token = create_session_token(user["id"], user["role"])
    response = JSONResponse(content={
        "ok": True,
        "user": {"id": user["id"], "username": user["username"], "display_name": user["display_name"], "role": user["role"]},
    })
    response.set_cookie(
        key=COOKIE_NAME, value=token,
        httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7,
    )
    return response


@app.post("/api/auth/logout")
async def logout():
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(COOKIE_NAME)
    return response


@app.get("/api/auth/me")
async def get_me(request: Request):
    session = get_current_user(request)
    if not session:
        return {"authenticated": False}
    user = await db.get_user(session["uid"])
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "user": {"id": user["id"], "username": user["username"], "display_name": user["display_name"], "role": user["role"]},
    }


# ── User management (admin only) ───────────────────────────────────

@app.get("/api/users")
async def list_users(request: Request):
    require_admin(request)
    return await db.list_users()


@app.post("/api/users", status_code=201)
async def create_user(data: UserCreate, request: Request):
    require_admin(request)
    if data.role not in ("admin", "participant"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'participant'")
    try:
        return await db.create_user(data.username, data.password, data.display_name, data.role)
    except Exception:
        raise HTTPException(status_code=400, detail="Användarnamnet är redan taget")


@app.put("/api/users/{user_id}")
async def update_user(user_id: int, data: UserUpdate, request: Request):
    require_admin(request)
    if data.role not in ("admin", "participant"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'participant'")
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.update_user(user_id, data.display_name, data.role, data.password)
    return {"ok": True}


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    session = require_admin(request)
    if session["uid"] == user_id:
        raise HTTPException(status_code=400, detail="Kan inte ta bort dig själv")
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete_user(user_id)
    return {"ok": True}


# ── Reference Data (public, needed for login page structure) ────────

@app.get("/api/reference", response_model=ReferenceDataResponse)
async def get_reference_data():
    perspective_maturity = []
    for p in PERSPECTIVES:
        pm = PERSPECTIVE_MATURITY.get(p.key, {})
        perspective_maturity.append(PerspectiveMaturityInfo(
            perspective_key=p.key,
            culture_labels=PERSPECTIVE_CULTURE.get(p.key, {}),
            subprocesses=[SubprocessInfo(**sp) for sp in PERSPECTIVE_SUBPROCESSES.get(p.key, [])],
            descriptions=pm,
        ))
    return ReferenceDataResponse(
        perspectives=[PerspectiveInfo(key=p.key, name_sv=p.name_sv, name_en=p.name_en, description_sv=p.description_sv) for p in PERSPECTIVES],
        dimensions=[DimensionInfo(key=d.key, name_sv=d.name_sv, name_en=d.name_en, description_sv=d.description_sv, prompts=DIMENSION_PROMPTS.get(d.key, [])) for d in DIMENSIONS],
        maturity_levels=[MaturityLevelInfo(level=m.level, name_sv=m.name_sv, name_en=m.name_en, description_sv=m.description_sv) for m in MATURITY_LEVELS],
        perspective_maturity=perspective_maturity,
    )


# ── Organizations (read: auth, write: admin) ───────────────────────

@app.post("/api/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(data: OrganizationCreate, request: Request):
    require_admin(request)
    return await db.create_organization(data.name, data.description)


@app.get("/api/organizations", response_model=list[OrganizationResponse])
async def list_organizations(request: Request):
    require_auth(request)
    return await db.list_organizations()


@app.get("/api/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: int, request: Request):
    require_auth(request)
    org = await db.get_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@app.put("/api/organizations/{org_id}")
async def update_organization(org_id: int, request: Request):
    require_auth(request)
    data = await request.json()
    org = await db.get_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    await db.update_organization(org_id, data.get("name", org["name"]), data.get("description", org["description"]))
    return {"ok": True}


@app.delete("/api/organizations/{org_id}")
async def delete_organization(org_id: int, request: Request):
    require_admin(request)
    org = await db.get_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    await db.delete_organization(org_id)
    return {"ok": True}


# ── Assessments (read: auth, create/finalize: admin) ───────────────

@app.post("/api/assessments", response_model=AssessmentResponse, status_code=201)
async def create_assessment(data: AssessmentCreate, request: Request):
    require_admin(request)
    org = await db.get_organization(data.organization_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return await db.create_assessment(
        data.organization_id, data.title, data.facilitator, data.participants,
    )


@app.get("/api/organizations/{org_id}/assessments", response_model=list[AssessmentResponse])
async def list_assessments(org_id: int, request: Request):
    require_auth(request)
    return await db.list_assessments(org_id)


@app.get("/api/assessments/{assessment_id}", response_model=AssessmentFullResponse)
async def get_assessment(assessment_id: int, request: Request):
    require_auth(request)
    assessment = await db.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    perspectives = await db.get_perspective_assessments(assessment_id)
    return AssessmentFullResponse(assessment=assessment, perspectives=perspectives)


@app.patch("/api/assessments/{assessment_id}/status")
async def update_assessment_status(assessment_id: int, status: str, request: Request):
    require_admin(request)
    assessment = await db.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    valid = {"draft", "in_progress", "finalized"}
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid}")
    if assessment["status"] == "finalized":
        raise HTTPException(status_code=400, detail="Cannot change status of a finalized assessment")
    await db.update_assessment_status(assessment_id, status)
    return {"ok": True, "status": status}


# ── Perspective Assessments (auth required) ─────────────────────────

@app.put("/api/assessments/{assessment_id}/perspectives/{perspective_key}")
async def update_perspective_assessment(
    assessment_id: int, perspective_key: str, data: PerspectiveAssessmentUpdate, request: Request,
):
    require_auth(request)
    if perspective_key not in PERSPECTIVE_KEYS:
        raise HTTPException(status_code=400, detail=f"Invalid perspective: {perspective_key}")
    assessment = await db.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if assessment["status"] == "finalized":
        raise HTTPException(status_code=400, detail="Assessment is finalized")
    await db.update_perspective_assessment(
        assessment_id, perspective_key, data.chosen_level, data.suggested_level, data.reasoning,
    )
    return {"ok": True}


# ── Dimension Assessments (auth required) ───────────────────────────

@app.put("/api/assessments/{assessment_id}/perspectives/{perspective_key}/dimensions/{dimension_key}")
async def update_dimension_assessment(
    assessment_id: int, perspective_key: str, dimension_key: str,
    data: DimensionAssessmentUpdate, request: Request,
):
    require_auth(request)
    if perspective_key not in PERSPECTIVE_KEYS:
        raise HTTPException(status_code=400, detail=f"Invalid perspective: {perspective_key}")
    if dimension_key not in DIMENSION_KEYS:
        raise HTTPException(status_code=400, detail=f"Invalid dimension: {dimension_key}")
    assessment = await db.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if assessment["status"] == "finalized":
        raise HTTPException(status_code=400, detail="Assessment is finalized")
    await db.update_dimension_assessment(
        assessment_id, perspective_key, dimension_key, data.selected_level, data.notes,
    )
    return {"ok": True}


# ── Guidance (auth required) ────────────────────────────────────────

@app.get("/api/guidance/{perspective_key}/{current_level}", response_model=GuidanceResponse)
async def get_guidance(perspective_key: str, current_level: int, request: Request):
    require_auth(request)
    if perspective_key not in PERSPECTIVE_KEYS:
        raise HTTPException(status_code=400, detail=f"Invalid perspective: {perspective_key}")
    if current_level < 1 or current_level > 4:
        raise HTTPException(status_code=400, detail="Level must be 1-4")
    if current_level == 4:
        return GuidanceResponse(
            perspective_key=perspective_key, current_level=4, next_level=4,
            suggestions=["Ni befinner er på högsta mognadsnivån. Fortsätt det proaktiva arbetet och dela era erfarenheter med andra."],
        )
    suggestions = NEXT_LEVEL_GUIDANCE.get((perspective_key, current_level), [
        "Ingen specifik vägledning tillgänglig för denna kombination.",
    ])
    return GuidanceResponse(
        perspective_key=perspective_key, current_level=current_level,
        next_level=current_level + 1, suggestions=suggestions,
    )


# ── Comparison (admin only) ─────────────────────────────────────────

@app.get("/api/organizations/{org_id}/comparison", response_model=ComparisonResponse)
async def get_comparison(org_id: int, request: Request):
    require_admin(request)
    org = await db.get_organization(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    snapshots = await db.get_assessment_snapshots(org_id)
    return ComparisonResponse(
        organization_id=org_id, organization_name=org["name"], assessments=snapshots,
    )


# ── PDF Export (auth required) ──────────────────────────────────────

@app.get("/api/assessments/{assessment_id}/export/pdf")
async def export_assessment_pdf(assessment_id: int, request: Request):
    require_auth(request)
    from weasyprint import HTML
    from .pdf_report import generate_report_html
    assessment = await db.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    org = await db.get_organization(assessment["organization_id"])
    perspectives = await db.get_perspective_assessments(assessment_id)
    html_str = generate_report_html(assessment, perspectives, org)
    pdf_bytes = HTML(string=html_str).write_pdf()
    filename = f"mognadsdialog-{assessment_id}.pdf"
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Surveys (unit-level maturity measurement) ───────────────────────

@app.get("/api/survey/reference")
async def get_survey_reference():
    from .survey_data import SURVEY_SECTIONS, SURVEY_LEVELS
    units = await db.get_survey_units()
    profiles = await db.get_survey_profiles()
    questions = await db.get_survey_questions_db()
    active_questions = [q for q in questions if q["active"]]
    return {
        "sections": SURVEY_SECTIONS,
        "levels": SURVEY_LEVELS,
        "profiles": {p["key"]: {"name": p["name"], "description": p["description"]} for p in profiles},
        "units": {u["name"]: u["profile_key"] for u in units},
        "unit_list": [u["name"] for u in units],
        "total_questions": len(active_questions),
    }


# ── Survey Config Admin ──────────────────────────────────────────────

@app.get("/api/survey/units")
async def list_survey_units(request: Request):
    require_auth(request)
    return await db.get_survey_units()


@app.post("/api/survey/units", status_code=201)
async def create_survey_unit(request: Request):
    require_admin(request)
    data = await request.json()
    try:
        return await db.create_survey_unit(data["name"], data["profile_key"])
    except Exception:
        raise HTTPException(status_code=400, detail="Enhetsnamnet finns redan")


@app.put("/api/survey/units/{unit_id}")
async def update_survey_unit(unit_id: int, request: Request):
    # All authenticated users can rename units
    require_auth(request)
    data = await request.json()
    # Only admin can change profile_key
    session = get_current_user(request)
    if "profile_key" in data and session["role"] != "admin":
        raise HTTPException(status_code=403, detail="Bara admin kan ändra frågegrupp")
    units = await db.get_survey_units()
    unit = next((u for u in units if u["id"] == unit_id), None)
    if not unit:
        raise HTTPException(status_code=404, detail="Enhet hittades inte")
    await db.update_survey_unit(unit_id, data.get("name", unit["name"]), data.get("profile_key", unit["profile_key"]))
    return {"ok": True}


@app.delete("/api/survey/units/{unit_id}")
async def delete_survey_unit(unit_id: int, request: Request):
    require_admin(request)
    await db.delete_survey_unit(unit_id)
    return {"ok": True}


@app.get("/api/survey/profiles")
async def list_survey_profiles(request: Request):
    require_auth(request)
    return await db.get_survey_profiles()


@app.get("/api/survey/questions")
async def list_survey_questions(request: Request):
    require_admin(request)
    return await db.get_survey_questions_db()


@app.put("/api/survey/questions/{qid}")
async def update_survey_question(qid: str, request: Request):
    require_admin(request)
    data = await request.json()
    await db.update_survey_question(
        qid, data["text"], data.get("help_text", ""), data.get("section", ""),
        data.get("standard", True), data.get("profile_tags", []), data.get("active", True),
    )
    return {"ok": True}


@app.post("/api/survey/questions", status_code=201)
async def create_survey_question_endpoint(request: Request):
    require_admin(request)
    data = await request.json()
    qid = data.get("id", f"custom_{int(__import__('time').time())}")
    await db.create_survey_question(
        qid, data["section"], data["text"], data.get("help_text", ""),
        data.get("standard", True), data.get("profile_tags", []),
    )
    return {"ok": True, "id": qid}


@app.post("/api/surveys", status_code=201)
async def create_survey(request: Request):
    require_admin(request)
    data = await request.json()
    org = await db.get_organization(data["organization_id"])
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return await db.create_survey(
        data["organization_id"], data["title"], data["profile_key"], data.get("respondent_name", ""),
    )


@app.get("/api/organizations/{org_id}/surveys")
async def list_surveys(org_id: int, request: Request):
    require_auth(request)
    return await db.list_surveys(org_id)


@app.get("/api/surveys/{survey_id}")
async def get_survey(survey_id: int, request: Request):
    require_auth(request)
    survey = await db.get_survey(survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    answers = await db.get_survey_answers(survey_id)
    # Enrich answers with question data from DB
    db_questions = await db.get_survey_questions_db()
    q_map = {q["id"]: q for q in db_questions}
    enriched = []
    for a in answers:
        q = q_map.get(a["question_id"], {})
        enriched.append({
            **a,
            "section": q.get("section", ""),
            "text": q.get("text", ""),
            "help_text": q.get("help_text", ""),
        })
    return {"survey": survey, "answers": enriched}


@app.put("/api/surveys/{survey_id}/answers/{question_id}")
async def update_survey_answer(survey_id: int, question_id: str, request: Request):
    require_auth(request)
    survey = await db.get_survey(survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey["status"] == "completed":
        raise HTTPException(status_code=400, detail="Survey is completed")
    data = await request.json()
    await db.update_survey_answer(survey_id, question_id, data.get("selected_level"), data.get("comment", ""))
    return {"ok": True}


@app.post("/api/surveys/{survey_id}/complete")
async def complete_survey(survey_id: int, request: Request):
    require_auth(request)
    survey = await db.get_survey(survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    await db.complete_survey(survey_id)
    return {"ok": True}


@app.delete("/api/surveys/{survey_id}")
async def delete_survey(survey_id: int, request: Request):
    require_admin(request)
    survey = await db.get_survey(survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    await db.delete_survey(survey_id)
    return {"ok": True}


# ── Settings (read: public, write: admin) ───────────────────────────

THEME_DEFAULTS = {
    "primary": "#E27629", "primary_light": "#F09A5B", "accent": "#2E7D32",
    "danger": "#e74c3c", "text": "#2c3e50", "text_light": "#7f8c8d",
    "bg": "#f5f7fa", "app_title": "Mognadsportalen",
}

@app.get("/api/settings")
async def get_settings():
    stored = await db.get_settings()
    result = {**THEME_DEFAULTS, **stored}
    # Auto-detect logo file on disk even if DB setting is missing
    if not result.get("logo_url"):
        img_dir = BASE_DIR / "static" / "img"
        for ext in (".png", ".jpg", ".svg", ".webp"):
            if (img_dir / f"logo{ext}").exists():
                result["logo_url"] = f"/static/img/logo{ext}"
                await db.set_setting("logo_url", result["logo_url"])
                break
    return result


@app.put("/api/settings")
async def update_settings(data: dict, request: Request):
    require_admin(request)
    allowed = set(THEME_DEFAULTS.keys())
    for key, value in data.items():
        if key in allowed:
            await db.set_setting(key, str(value))
    return {"ok": True}


@app.post("/api/settings/logo")
async def upload_logo(file: UploadFile = File(...), request: Request = None):
    require_admin(request)
    if file.content_type not in ("image/png", "image/jpeg", "image/svg+xml", "image/webp"):
        raise HTTPException(status_code=400, detail="Only PNG, JPEG, SVG or WebP allowed")
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")
    img_dir = BASE_DIR / "static" / "img"
    img_dir.mkdir(exist_ok=True)
    ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/svg+xml": ".svg", "image/webp": ".webp"}[file.content_type]
    logo_path = img_dir / f"logo{ext}"
    for old in img_dir.glob("logo.*"):
        old.unlink()
    logo_path.write_bytes(contents)
    await db.set_setting("logo_url", f"/static/img/logo{ext}")
    return {"ok": True, "logo_url": f"/static/img/logo{ext}"}


@app.delete("/api/settings/logo")
async def delete_logo(request: Request):
    require_admin(request)
    img_dir = BASE_DIR / "static" / "img"
    for old in img_dir.glob("logo.*"):
        old.unlink()
    await db.set_setting("logo_url", "")
    return {"ok": True}


# ── SPA fallback ────────────────────────────────────────────────────

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(str(BASE_DIR / "static" / "index.html"))

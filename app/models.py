"""
Pydantic models — API schemas for the Mognadsdialog system.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# ── Organization ────────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")


class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime


# ── Assessment ──────────────────────────────────────────────────────

class AssessmentCreate(BaseModel):
    organization_id: int
    title: str = Field(..., min_length=1, max_length=300)
    facilitator: str = Field(default="")
    participants: str = Field(default="", description="Comma-separated list of participants")


class AssessmentResponse(BaseModel):
    id: int
    organization_id: int
    title: str
    facilitator: str
    participants: str
    status: str
    created_at: datetime
    finalized_at: Optional[datetime] = None


# ── Dimension Assessment (level selection per dimension) ────────────

class DimensionAssessmentUpdate(BaseModel):
    selected_level: Optional[int] = Field(default=None, ge=1, le=4)
    notes: str = Field(default="")


class DimensionAssessmentResponse(BaseModel):
    perspective_key: str
    dimension_key: str
    selected_level: Optional[int] = None
    notes: str


# ── Perspective Assessment ──────────────────────────────────────────

class PerspectiveAssessmentUpdate(BaseModel):
    chosen_level: Optional[int] = Field(default=None, ge=1, le=4)
    suggested_level: Optional[int] = Field(default=None, ge=1, le=4)
    reasoning: str = Field(default="")


class PerspectiveAssessmentResponse(BaseModel):
    assessment_id: int
    perspective_key: str
    chosen_level: Optional[int] = None
    suggested_level: Optional[int] = None
    reasoning: str
    dimension_assessments: list[DimensionAssessmentResponse]


# ── Full assessment ─────────────────────────────────────────────────

class AssessmentFullResponse(BaseModel):
    assessment: AssessmentResponse
    perspectives: list[PerspectiveAssessmentResponse]


# ── Reference data ──────────────────────────────────────────────────

class PerspectiveInfo(BaseModel):
    key: str
    name_sv: str
    name_en: str
    description_sv: str


class DimensionInfo(BaseModel):
    key: str
    name_sv: str
    name_en: str
    description_sv: str
    prompts: list[str]


class MaturityLevelInfo(BaseModel):
    level: int
    name_sv: str
    name_en: str
    description_sv: str


class SubprocessInfo(BaseModel):
    name: str
    description: str


class PerspectiveMaturityInfo(BaseModel):
    perspective_key: str
    culture_labels: dict[int, str]
    subprocesses: list[SubprocessInfo]
    descriptions: dict[str, dict[int, str]]  # dimension_key -> level -> text


class ReferenceDataResponse(BaseModel):
    perspectives: list[PerspectiveInfo]
    dimensions: list[DimensionInfo]
    maturity_levels: list[MaturityLevelInfo]
    perspective_maturity: list[PerspectiveMaturityInfo]


# ── Guidance ────────────────────────────────────────────────────────

class GuidanceResponse(BaseModel):
    perspective_key: str
    current_level: int
    next_level: int
    suggestions: list[str]


# ── Comparison ──────────────────────────────────────────────────────

class PerspectiveLevelSnapshot(BaseModel):
    perspective_key: str
    chosen_level: Optional[int] = None


class AssessmentSnapshot(BaseModel):
    assessment_id: int
    title: str
    created_at: datetime
    status: str
    levels: list[PerspectiveLevelSnapshot]


class ComparisonResponse(BaseModel):
    organization_id: int
    organization_name: str
    assessments: list[AssessmentSnapshot]

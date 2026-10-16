import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from fastapi import APIRouter, HTTPException, Request, Query

from app.schemas.resume_data import ResumeData

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

TEMPLATE_OPTIONS = [
    {"id": "classic", "name": "Classic", "description": "Traditional professional layout", "tag": "ATS-friendly"},
    {"id": "modern", "name": "Modern", "description": "Contemporary clean layout", "tag": "Modern"},
    {"id": "editorial", "name": "Editorial", "description": "Elegant typography and editorial header", "tag": "Premium"},
    {"id": "executive", "name": "Executive", "description": "Formal leadership-focused layout", "tag": "Professional"},
    {"id": "corporate", "name": "Corporate", "description": "Conservative business-ready layout", "tag": "ATS-friendly"},
    {"id": "minimal", "name": "Minimal", "description": "Simple ATS-friendly layout", "tag": "ATS-friendly"},
    {"id": "simple", "name": "Simple", "description": "No-frills, readable layout", "tag": "ATS-friendly"},
    {"id": "elegant", "name": "Elegant", "description": "Serif typography and subtle details", "tag": "Elegant"},
    {"id": "swiss", "name": "Swiss", "description": "Grid-inspired typography", "tag": "ATS-friendly"},
    {"id": "one-page", "name": "One Page", "description": "Compact layout for concise resumes", "tag": "Compact"},
    {"id": "developer", "name": "Developer", "description": "Code-inspired technical resume", "tag": "Tech"},
    {"id": "software-engineer", "name": "Software Engineer", "description": "Projects and skills forward", "tag": "Tech"},
    {"id": "technical", "name": "Technical", "description": "Structured engineering-focused layout", "tag": "Engineering"},
    {"id": "creative", "name": "Creative", "description": "Expressive color and section markers", "tag": "Creative"},
    {"id": "portfolio", "name": "Portfolio", "description": "Project-forward visual hierarchy", "tag": "Portfolio"},
    {"id": "sidebar", "name": "Sidebar", "description": "Two-column layout with information rail", "tag": "Two-column"},
    {"id": "split-layout", "name": "Split Layout", "description": "Balanced two-column layout", "tag": "Two-column"},
    {"id": "dark-sidebar", "name": "Dark Sidebar", "description": "High contrast dark information rail", "tag": "Premium"},
    {"id": "student", "name": "Student / Fresher", "description": "Education and projects prioritized", "tag": "Student"},
    {"id": "internship", "name": "Internship", "description": "Placement and internship focused", "tag": "Fresher"},
]


@router.get("/create-resume", response_class=HTMLResponse)
async def template_gallery(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_resume.html",
        context={"templates": TEMPLATE_OPTIONS},
    )



@router.get("/create-resume/build/{template_id}", response_class=HTMLResponse)
async def resume_builder(
    request: Request,
    template_id: str,
    source: str | None = Query(default=None),
):
    selected = next(
        (item for item in TEMPLATE_OPTIONS if item["id"] == template_id),
        None,
    )

    if selected is None:
        raise HTTPException(
            status_code=404,
            detail="Resume template not found",
        )

    empty_resume = ResumeData().model_dump()

    return templates.TemplateResponse(
        request=request,
        name="resume_builder.html",
        context={
            "selected_template": selected,
            "resume_json": json.dumps(empty_resume),
            "resume_source": source if source == "uploaded" else "template",
        },
    )



@router.post("/api/resume-preview", response_class=HTMLResponse)
async def live_resume_preview(request: Request):
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=422, detail="Request body must be an object.")

        template_id = payload.get("template_id", "classic")
        allowed_ids = {item["id"] for item in TEMPLATE_OPTIONS}
        if template_id not in allowed_ids:
            raise HTTPException(status_code=400, detail="Unknown resume template.")

        incoming = payload.get("resume", {})
        if not isinstance(incoming, dict):
            raise HTTPException(status_code=422, detail="Resume data must be an object.")

        # Preserve the current nested schema while accepting older flat personal fields.
        normalized = dict(incoming)
        personal = incoming.get("personal")
        if not isinstance(personal, dict):
            personal = {}

        personal_fields = (
            "full_name", "job_title", "email", "phone",
            "location", "website", "linkedin", "summary",
        )
        normalized["personal"] = {
            field: personal.get(field, incoming.get(field, ""))
            for field in personal_fields
        }

        resume = ResumeData.model_validate(normalized)
        template = templates.get_template(f"resumes/{template_id}.html")
        html = template.render(request=request, resume=resume.model_dump())
        return HTMLResponse(content=html)

    except ValidationError as exc:
        return JSONResponse(
            {"error": "Some resume fields are invalid.", "details": exc.errors()},
            status_code=422,
        )

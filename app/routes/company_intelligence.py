
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.services.company_intelligence_service import (
    analyze_job_description,
    get_company,
    search_companies,
)

router = APIRouter(tags=["Company Intelligence"])

BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

class JobAnalysisRequest(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    job_description: str = Field(min_length=50, max_length=15000)


# @router.get("/company-intelligence", response_class=HTMLResponse)
# async def company_intelligence_page(request: Request):
#     return request.app.state.templates.TemplateResponse(
#         request=request,
#         name="company_intelligence.html",
#         context={"page_title": "Company Intelligence"},
#     )

@router.get("/company-intelligence")
async def company_intelligence_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="company_intelligence.html",
        context={}
    )


@router.get("/api/companies")
async def companies(
    q: Annotated[str, Query(max_length=100)] = ""
):
    return {"companies": search_companies(q)}


@router.get("/api/companies/{company_name}")
async def company_details(company_name: str):
    company = get_company(company_name)

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company profile not found. Try another search or paste a job description."
        )

    return {"company": company}


@router.post("/api/companies/analyze-job")
async def analyze_job(payload: JobAnalysisRequest):
    try:
        result = analyze_job_description(
            company=payload.company,
            role=payload.role,
            job_description=payload.job_description,
        )
        return {"analysis": result}

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception as exc:
        # Avoid exposing provider errors, secrets, or stack traces to clients.
        raise HTTPException(
            status_code=502,
            detail="Job analysis failed. Please try again later."
        ) from exc

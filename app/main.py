from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import mongodb  # Preserve the existing MongoDB initialization.
from app.routes.auth import router as auth_router
from app.routes.resume import router as resume_router
from app.routes.ats import router as ats_router
from app.routes.resume_builder import router as resume_builder_router
from app.routes.ai_assistant import router as ai_assistant_router
from app.routes.company_intelligence import router as company_intelligence_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Resume Creator")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home", status_code=307)


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/editor")
async def editor(request: Request):
    return templates.TemplateResponse(request=request, name="editor.html")


@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/ats")
async def ats_page(request: Request):
    return templates.TemplateResponse(request=request, name="ats.html")


app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(ats_router)
app.include_router(resume_builder_router)
app.include_router(ai_assistant_router)
app.include_router(company_intelligence_router)
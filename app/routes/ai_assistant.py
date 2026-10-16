
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_assistant_service import run_ai_task

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


class AIAssistantRequest(BaseModel):
    task: Literal[
        "improve_summary",
        "improve_bullet",
        "job_match",
    ]
    text: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(default="", max_length=20000)


@router.post("/assist")
def ai_assist(request: AIAssistantRequest):
    try:
        result = run_ai_task(
            task=request.task,
            text=request.text,
            job_description=request.job_description,
        )

        return {
            "success": True,
            "task": request.task,
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except Exception:
        # Keep API keys and provider error details out of responses.
        raise HTTPException(
            status_code=502,
            detail="The AI service failed. Please try again later.",
        )

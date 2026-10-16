
from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz

from app.services.gemini_service import (
    analyze_resume,
    normalize_resume_data,
)
from app.services.pdf_layout_service import extract_pdf_layout

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    pdf_bytes = await file.read()

    # Basic upload size limit: 10 MB.
    if not pdf_bytes or len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="PDF must be non-empty and no larger than 10 MB.",
        )

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf_document:
            if pdf_document.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported.",
                )

            layout_data = extract_pdf_layout(pdf_document)
            text_pages: list[str] = []

            # Extract text from every page.
            for page in pdf_document:
                page_text = page.get_text("text")

                if isinstance(page_text, str):
                    text_pages.append(page_text)

            extracted_text = "\n".join(text_pages)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No selectable text was found. This PDF may be scanned; "
                    "OCR support is needed for this file."
                ),
            )

        ai_response = analyze_resume(extracted_text)
        resume_data = normalize_resume_data(ai_response)

        return {
            "message": "PDF processed successfully",
            "text": extracted_text,
            "layout": layout_data,
            "ai_analysis": ai_response,
            "resume_data": resume_data,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print("Resume upload error:", repr(exc))
        raise HTTPException(
            status_code=500,
            detail="Could not process this resume. Check the server log.",
        )

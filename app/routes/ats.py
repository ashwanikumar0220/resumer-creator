from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import fitz

from app.services.ats_service import analyze_ats


router = APIRouter(
    prefix="/ats",
    tags=["ATS"]
)


@router.post("/analyze")
async def analyze_resume_ats(
    file: UploadFile = File(...)
):

    # --------------------------------------
    # Check file type
    # --------------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )


    # --------------------------------------
    # Read PDF
    # --------------------------------------

    pdf_bytes = await file.read()


    if not pdf_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )


    # --------------------------------------
    # Open PDF with PyMuPDF
    # --------------------------------------

    try:

        pdf_document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )


    # --------------------------------------
    # Extract text
    # --------------------------------------

    extracted_text = ""


    for page in pdf_document:
        extracted_text = extracted_text + str(page.get_text("text"))+ "\n"

    pdf_document.close()


    # --------------------------------------
    # Check extracted text
    # --------------------------------------

    if not extracted_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "in this PDF."
            )
        )


    # --------------------------------------
    # Send text to Gemini
    # --------------------------------------

    ats_result = analyze_ats(
        extracted_text
    )


    if ats_result is None:

        raise HTTPException(
            status_code=500,
            detail="ATS analysis failed."
        )


    # --------------------------------------
    # Return result to frontend
    # --------------------------------------

    return {

        "message":
            "ATS analysis completed",

        "score":
            ats_result["score"],

        "skills_match":
            ats_result["skills_match"],

        "experience":
            ats_result["experience"],

        "keywords":
            ats_result["keywords"],

        "formatting":
            ats_result["formatting"],

        "suggestions":
            ats_result["suggestions"]

    }
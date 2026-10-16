
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    return Groq(api_key=api_key)


def run_ai_task(task: str, text: str, job_description: str = "") -> str:
    """Run a resume-writing or job-matching task using Groq."""

    if not text or not text.strip():
        raise ValueError("Please provide resume text or content.")

    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    instructions = {
        "improve_summary": """
Rewrite the supplied professional summary to make it clear,
professional, concise, and relevant to the candidate's experience.
Do not invent qualifications, years of experience, or achievements.
Return only the improved summary.
""",
        "improve_bullet": """
Improve the supplied resume content into strong, concise,
professional resume bullet points. Use action verbs where appropriate.
Do not invent metrics, responsibilities, skills, or achievements.
Return only the improved content.
""",
        "job_match": """
Compare the resume against the job description.
Identify matching skills, relevant experience, missing or unclear
keywords, and practical improvements. Do not claim that the result
is a guaranteed ATS score or invent candidate qualifications.
Return clear headings and concise bullet points.
""",
    }

    if task not in instructions:
        raise ValueError("Unsupported AI task.")

    prompt = f"{instructions[task]}\n\nRESUME OR CONTENT:\n{text}"

    if task == "job_match":
        if not job_description.strip():
            raise ValueError(
                "A job description is required for job matching."
            )
        prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"

    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume-writing assistant. "
                    "Preserve factual accuracy and never invent information."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise RuntimeError("The AI returned an empty response.")

    return result.strip()

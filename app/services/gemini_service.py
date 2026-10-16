import os
import json

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


# --------------------------------------
# Groq Client
# --------------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# --------------------------------------
# Resume Analysis
# --------------------------------------

def analyze_resume(resume_text: str):

    prompt = f"""
You are an AI resume parser.

Extract information from the resume and organize it
according to the provided JSON schema.

Rules:

- Extract only information actually present in the resume.
- Do not invent information.
- If a single value is not found, return null.
- If a section with multiple items is not found, return [].
- Keep descriptions and bullet points as close as possible
  to the original resume.
- Do not rewrite or improve the resume.
- Preserve the original meaning and wording.

Resume:

{resume_text}
"""

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume parser. "
                        "Extract resume information accurately "
                        "without inventing information."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            response_format={
                "type": "json_schema",

                "json_schema": {

                    "name": "resume_parser",

                    "strict": True,

                    "schema": {

                        "type": "object",

                        "properties": {

                            # --------------------------------------
                            # Personal Details
                            # --------------------------------------

                            "personal_details": {

                                "type": "object",

                                "properties": {

                                    "name": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },

                                    "email": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },

                                    "phone": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },

                                    "location": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },

                                    "linkedin": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },

                                    "github": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    }
                                },

                                "required": [
                                    "name",
                                    "email",
                                    "phone",
                                    "location",
                                    "linkedin",
                                    "github"
                                ],

                                "additionalProperties": False
                            },


                            # --------------------------------------
                            # Summary
                            # --------------------------------------

                            "summary": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            },


                            # --------------------------------------
                            # Experience
                            # --------------------------------------

                            "experience": {

                                "type": "array",

                                "items": {

                                    "type": "object",

                                    "properties": {

                                        "company": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "role": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "start_date": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "end_date": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "description": {

                                            "type": "array",

                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    },

                                    "required": [
                                        "company",
                                        "role",
                                        "start_date",
                                        "end_date",
                                        "description"
                                    ],

                                    "additionalProperties": False
                                }
                            },


                            # --------------------------------------
                            # Education
                            # --------------------------------------

                            "education": {

                                "type": "array",

                                "items": {

                                    "type": "object",

                                    "properties": {

                                        "institution": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "degree": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "start_date": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "end_date": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        }
                                    },

                                    "required": [
                                        "institution",
                                        "degree",
                                        "start_date",
                                        "end_date"
                                    ],

                                    "additionalProperties": False
                                }
                            },


                            # --------------------------------------
                            # Projects
                            # --------------------------------------

                            "projects": {

                                "type": "array",

                                "items": {

                                    "type": "object",

                                    "properties": {

                                        "name": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "description": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },

                                        "technologies": {

                                            "type": "array",

                                            "items": {
                                                "type": "string"
                                            }
                                        },

                                        "link": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        }
                                    },

                                    "required": [
                                        "name",
                                        "description",
                                        "technologies",
                                        "link"
                                    ],

                                    "additionalProperties": False
                                }
                            },


                            # --------------------------------------
                            # Skills
                            # --------------------------------------

                            "skills": {

                                "type": "array",

                                "items": {
                                    "type": "string"
                                }
                            },


                            # --------------------------------------
                            # Certifications
                            # --------------------------------------

                            "certifications": {

                                "type": "array",

                                "items": {
                                    "type": "string"
                                }
                            },


                            # --------------------------------------
                            # Achievements
                            # --------------------------------------

                            "achievements": {

                                "type": "array",

                                "items": {
                                    "type": "string"
                                }
                            },


                            # --------------------------------------
                            # Languages
                            # --------------------------------------

                            "languages": {

                                "type": "array",

                                "items": {
                                    "type": "string"
                                }
                            }
                        },

                        "required": [
                            "personal_details",
                            "summary",
                            "experience",
                            "education",
                            "projects",
                            "skills",
                            "certifications",
                            "achievements",
                            "languages"
                        ],

                        "additionalProperties": False
                    }
                }
            }
        )


        # --------------------------------------
        # Get response
        # --------------------------------------

        content = response.choices[0].message.content


        if content:

            return json.loads(content)


        return None


    except Exception as e:

        print(
            "Groq Resume Parser Error:",
            e
        )

        return None



def normalize_resume_data(parsed: dict | None) -> dict:
    """Map existing Groq parser output into the shared ResumeData schema."""
    from app.schemas.resume_data import ResumeData

    parsed = parsed or {}
    personal = parsed.get("personal_details") or {}

    def clean(value):
        return str(value).strip() if value is not None else ""

    def list_of_strings(values):
        if not isinstance(values, list):
            return []
        result = []
        for value in values:
            if isinstance(value, str) and value.strip():
                result.append(value.strip())
            elif isinstance(value, dict):
                # Accept common parser output shapes without inventing data.
                text = value.get("name") or value.get("title") or value.get("content")
                if text:
                    result.append(str(text).strip())
        return result

    education = []
    for item in parsed.get("education") or []:
        if not isinstance(item, dict):
            continue
        education.append({
            "institution": clean(item.get("institution")),
            "degree": clean(item.get("degree")),
            "field_of_study": "",
            "start_date": clean(item.get("start_date")),
            "end_date": clean(item.get("end_date")),
            "grade": "",
            "description": "",
        })

    experience = []
    for item in parsed.get("experience") or []:
        if not isinstance(item, dict):
            continue
        experience.append({
            "company": clean(item.get("company")),
            "position": clean(item.get("role") or item.get("position")),
            "location": clean(item.get("location")),
            "start_date": clean(item.get("start_date")),
            "end_date": clean(item.get("end_date")),
            "description": clean(item.get("description")),
        })

    projects = []
    for item in parsed.get("projects") or []:
        if not isinstance(item, dict):
            continue
        technologies = item.get("technologies") or []
        if isinstance(technologies, str):
            technologies_text = technologies
        else:
            technologies_text = ", ".join(list_of_strings(technologies))
        projects.append({
            "name": clean(item.get("name")),
            "technologies": clean(technologies_text),
            "link": clean(item.get("link")),
            "description": clean(item.get("description")),
        })

    certifications = []
    for item in parsed.get("certifications") or []:
        if isinstance(item, str):
            certifications.append({"name": clean(item), "issuer": "", "date": ""})
        elif isinstance(item, dict):
            certifications.append({
                "name": clean(item.get("name")),
                "issuer": clean(item.get("issuer")),
                "date": clean(item.get("date")),
            })

    normalized = {
        "personal": {
            "full_name": clean(personal.get("name")),
            "job_title": clean(personal.get("job_title") or personal.get("title")),
            "email": clean(personal.get("email")),
            "phone": clean(personal.get("phone")),
            "location": clean(personal.get("location")),
            "website": clean(personal.get("website") or personal.get("github")),
            "linkedin": clean(personal.get("linkedin")),
            "summary": clean(parsed.get("summary")),
        },
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": list_of_strings(parsed.get("skills")),
        "certifications": certifications,
        "languages": list_of_strings(parsed.get("languages")),
        "achievements": list_of_strings(parsed.get("achievements")),
        "custom_sections": [],
    }

    # Validate and enforce the same limits used by the builder.
    return ResumeData.model_validate(normalized).model_dump()

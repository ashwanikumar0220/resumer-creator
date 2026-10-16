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
# ATS Analysis
# --------------------------------------

def analyze_ats(resume_text: str):

    prompt = f"""
You are a professional ATS resume analyzer.

Analyze the following resume text and evaluate how ATS-friendly
the resume appears.

Give scores from 0 to 100 for:

1. skills_match
2. experience
3. keywords
4. formatting

Then calculate an overall ATS score.

Rules:

- Do not invent information.
- Analyze only information present in the resume.
- Do not assume skills that are not mentioned.
- Give practical and specific suggestions.
- Keep suggestions short and useful.
- The formatting score should represent how ATS-friendly
  the extracted resume structure appears.
- Do not claim that the resume is guaranteed to pass or fail
  a real ATS.
- The overall score should be a reasonable combined assessment
  of the four category scores.
- Return only the requested JSON structure.

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
                        "You are an expert ATS resume analyzer. "
                        "Analyze resumes objectively and return "
                        "accurate structured results."
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
                    "name": "ats_analysis",

                    "strict": True,

                    "schema": {

                        "type": "object",

                        "properties": {

                            "score": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },

                            "skills_match": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },

                            "experience": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },

                            "keywords": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },

                            "formatting": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },

                            "suggestions": {
                                "type": "array",

                                "items": {
                                    "type": "string"
                                }
                            }
                        },

                        "required": [
                            "score",
                            "skills_match",
                            "experience",
                            "keywords",
                            "formatting",
                            "suggestions"
                        ],

                        "additionalProperties": False
                    }
                }
            }
        )

        # --------------------------------------
        # Get model response
        # --------------------------------------

        content = response.choices[0].message.content

        if not content:
            return None

        # --------------------------------------
        # Convert JSON string to Python dict
        # --------------------------------------

        return json.loads(content)

    except Exception as e:

        print("ATS Groq Error:", e)

        return None
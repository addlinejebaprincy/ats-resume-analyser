import os
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


load_dotenv()
class AIAnalysisUnavailableError(Exception):
    """Raised when Gemini analysis cannot be completed safely."""


class Improvement(BaseModel):
    title: str = Field(description="Short name of the resume problem.")
    explanation: str = Field(
        description="Why this problem weakens the resume."
    )
    recommendation: str = Field(
        description="A specific way to improve it."
    )


class ProjectFeedback(BaseModel):
    project_name: str = Field(
        description="Name of the project found in the resume."
    )
    assessment: str = Field(
        description="Evaluation of how effectively the project is described."
    )
    improved_bullet: str = Field(
        description="An improved project bullet using only facts explicitly stated "
    "in the resume. Never add unsupported tools, metrics, or features."
    )


class AIResumeAnalysis(BaseModel):
    professional_summary: str = Field(
        description="A detailed overall assessment of the resume."
    )
    strengths: List[str] = Field(
        description="Specific strengths supported by the resume text."
    )
    priority_improvements: List[Improvement] = Field(
        description="The most important improvements in priority order."
    )
    project_feedback: List[ProjectFeedback] = Field(
        description="Detailed feedback for projects found in the resume."
    )
    job_alignment: str = Field(
        description="How well the resume matches the supplied job description."
    )


def analyze_resume_with_ai(resume_text, job_description=""):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    job_context = (
        job_description.strip()
        if job_description.strip()
        else "No job description was provided."
    )

    prompt = f"""
You are an experienced resume reviewer and technical recruiter.

Analyze the supplied resume carefully. Base every observation only on the
information present in the resume. Do not invent experience, qualifications,
metrics, projects, or skills.When rewriting a project bullet, use only technologies, features, and
results explicitly stated in the resume. Never add missing job-description
skills to a project bullet. If there is insufficient project information,
provide a cautious rewrite without inventing details.

Provide:
1. A detailed professional assessment.
2. Evidence-based strengths.
3. Prioritized and practical improvements.
4. Feedback for every project that is present.
5. An assessment of alignment with the job description.

If the document does not appear to be a resume, clearly explain that in the
professional summary and do not invent resume content.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{job_context}
"""

    try:
        client = genai.Client(api_key=api_key)

        interaction = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            store=False,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": AIResumeAnalysis.model_json_schema(),
            },
        )

        return AIResumeAnalysis.model_validate_json(
            interaction.output_text
        )

    except Exception as error:
        raise AIAnalysisUnavailableError(
            "Detailed AI analysis is temporarily unavailable."
        ) from error

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        store=False,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AIResumeAnalysis.model_json_schema(),
        },
    )

    return AIResumeAnalysis.model_validate_json(
        interaction.output_text
    )
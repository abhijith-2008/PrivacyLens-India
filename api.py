
"""
PrivacyLens India - FastAPI backend.

Reuses the existing report and DPDP analysis pipeline.
"""

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analyzer import PrivacyPolicyAnalyzer
from report import build_report
from dpdp_checklist import build_dpdp_checklist


app = FastAPI(
    title="PrivacyLens India API",
    description=(
        "API for extractive privacy-policy summaries, "
        "OPP-115 ML findings, and informational DPDP checks."
    ),
    version="1.0.0",
)


# Temporary CORS configuration for local extension development.
# We will restrict this appropriately before public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalysisRequest(BaseModel):
    policy_text: str = Field(
        min_length=50,
        max_length=200_000,
        description="Privacy policy text to analyse.",
    )


@lru_cache(maxsize=1)
def get_analyzer():
    """Load the existing ML model once and reuse it."""
    return PrivacyPolicyAnalyzer()


@app.get("/")
def home():
    return {
        "message": "PrivacyLens India API is running!",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "PrivacyLens India API",
    }


@app.post("/analyze")
def analyze_policy(request: AnalysisRequest):
    """Analyse policy text using the existing project pipeline."""

    policy_text = request.policy_text.strip()

    if len(policy_text) < 50:
        raise HTTPException(
            status_code=422,
            detail="Please provide at least 50 characters of policy text.",
        )

    try:
        analyzer = get_analyzer()

        # Reuse the existing report-generation pipeline.
        report = build_report(
            policy_text,
            analyzer=analyzer,
        )

        # Reuse the existing DPDP checklist.
        checklist = build_dpdp_checklist(
            policy_text,
            include_model_report=False,
        )

        return {
            "product": "PrivacyLens India",
            "status": "success",
            "summary": {
                "type": report["summary_type"],
                "note": report["summary_note"],
                "sentences": report["summary_sentences"],
            },
            "privacy_findings": {
                "count": report["finding_count"],
                "categories": report["findings"],
                "section_count": report["section_count"],
                "threshold": report["threshold"],
            },
            "dpdp_checklist": checklist["checklist"],
            "limitations": report["limitations"],
            "disclaimer": checklist["disclaimer"],
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="The PrivacyLens ML model could not be loaded.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Keep internal exception details out of public responses.
        print(f"PrivacyLens API error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again.",
        ) from exc

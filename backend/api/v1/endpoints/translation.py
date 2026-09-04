"""
Translation API Endpoint - Downstream translation service wrapper
"""

from fastapi import APIRouter, HTTPException, status
from backend.schemas.contracts import TranslationRequest, TranslationResponse
from backend.services.llm_service import translate_decision_card

router = APIRouter(prefix="/translate", tags=["Translation"])

@router.post("", response_model=TranslationResponse)
def translate_card(req: TranslationRequest):
    """
    Translates a finalized DecisionCard into Marathi (mr) and Hindi (hi).
    Generative AI / template dictionary is strictly downstream.
    """
    if req.target_language:
        target_langs = [req.target_language]
    elif req.target_languages:
        target_langs = req.target_languages
    else:
        target_langs = ["mr", "hi"]

    for lang in target_langs:
        if lang not in ["mr", "hi"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported target language '{lang}'. Only 'mr' and 'hi' are supported."
            )

    translations = translate_decision_card(
        decision_card=req.decision_card,
        target_languages=target_langs
    )

    return TranslationResponse(
        decision_id=req.decision_card.decision_id,
        translations=translations
    )

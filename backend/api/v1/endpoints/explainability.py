"""
Explainability Drawer API Endpoint
Retrieves deep auditability parameters for a finalized decision card.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import DBDecisionRecord
from backend.schemas.contracts import ExplainabilityDetails

router = APIRouter(prefix="/explainability", tags=["Explainability Drawer"])

@router.get("/{decision_id}", response_model=ExplainabilityDetails)
def get_explainability_details(decision_id: str, db: Session = Depends(get_db)):
    """
    Retrieves rule traces, threshold evaluations, and exact input metrics
    used during deterministic arbitration for a specific decision_id.
    """
    record = db.query(DBDecisionRecord).filter(
        (DBDecisionRecord.decision_id == decision_id) | (DBDecisionRecord.explainability_id == decision_id)
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explainability record for decision ID / explainability ID '{decision_id}' not found."
        )

    try:
        details_dict = json.loads(record.explainability_json)
        return ExplainabilityDetails(**details_dict)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corrupted explainability record payload: {err}"
        )

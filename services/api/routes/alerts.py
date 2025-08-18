"""Alert management endpoints (stub implementation)."""

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class AlertCreateRequest(BaseModel):
    """Alert creation request model."""

    query_text: str = Field(..., min_length=3, max_length=500)
    positive_filters: Optional[List[str]] = Field(default=None)
    negative_filters: Optional[List[str]] = Field(default=None)
    subreddits: Optional[List[str]] = Field(default=None)
    frequency_minutes: int = Field(default=180, ge=60, le=1440)  # 1 hour to 24 hours


class AlertResponse(BaseModel):
    """Alert response model."""

    id: str
    query_text: str
    positive_filters: Optional[List[str]]
    negative_filters: Optional[List[str]]
    subreddits: Optional[List[str]]
    frequency_minutes: int
    is_active: bool
    created_at: str


class AlertUpdateRequest(BaseModel):
    """Alert update request model."""

    query_text: Optional[str] = Field(default=None, min_length=3, max_length=500)
    positive_filters: Optional[List[str]] = Field(default=None)
    negative_filters: Optional[List[str]] = Field(default=None)
    subreddits: Optional[List[str]] = Field(default=None)
    frequency_minutes: Optional[int] = Field(default=None, ge=60, le=1440)
    is_active: Optional[bool] = Field(default=None)


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(request: AlertCreateRequest):
    """
    Create a new alert for saved searches.
    
    TODO: This is a stub implementation. In the full version:
    1. Store alert in database with user association
    2. Generate embedding for the query
    3. Set up Celery task scheduling
    """
    logger.info(f"Creating alert stub for query: '{request.query_text[:50]}...'")
    
    # For now, return a mock response
    alert_id = str(uuid.uuid4())
    
    return AlertResponse(
        id=alert_id,
        query_text=request.query_text,
        positive_filters=request.positive_filters,
        negative_filters=request.negative_filters,
        subreddits=request.subreddits,
        frequency_minutes=request.frequency_minutes,
        is_active=True,
        created_at="2024-01-01T00:00:00Z",
    )


@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts():
    """
    List user's alerts.
    
    TODO: Implement user authentication and database query.
    """
    logger.info("Listing alerts stub")
    
    # Return empty list for now
    return []


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str):
    """
    Get specific alert by ID.
    
    TODO: Implement database lookup and user ownership check.
    """
    logger.info(f"Getting alert stub: {alert_id}")
    
    # For now, return a mock alert or 404
    raise HTTPException(status_code=404, detail="Alert not found")


@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: str, request: AlertUpdateRequest):
    """
    Update an existing alert.
    
    TODO: Implement database update and user ownership check.
    """
    logger.info(f"Updating alert stub: {alert_id}")
    
    raise HTTPException(status_code=404, detail="Alert not found")


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Delete an alert.
    
    TODO: Implement database deletion and user ownership check.
    """
    logger.info(f"Deleting alert stub: {alert_id}")
    
    raise HTTPException(status_code=404, detail="Alert not found")

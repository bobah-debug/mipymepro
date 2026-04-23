from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def dashboard(
    year: int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    return get_dashboard(db, y, m)

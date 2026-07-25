from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("/", response_model=List[schemas.BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Budget).filter(models.Budget.user_id == current_user.id).all()

@router.post("/", response_model=schemas.BudgetResponse)
def create_or_update_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    existing = db.query(models.Budget).filter(
        models.Budget.category == budget.category,
        models.Budget.user_id == current_user.id
    ).first()

    if existing:
        existing.monthly_limit = budget.monthly_limit
        db.commit()
        db.refresh(existing)
        return existing

    new_budget = models.Budget(**budget.dict(), user_id=current_user.id)
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget
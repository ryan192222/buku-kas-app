from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("/", response_model=List[schemas.GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()

@router.post("/", response_model=schemas.GoalResponse)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_goal = models.Goal(**goal.dict(), user_id=current_user.id)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.put("/{goal_id}/add-savings", response_model=schemas.GoalResponse)
def add_savings(
    goal_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Target tabungan tidak ditemukan")

    goal.current_amount += amount
    db.commit()
    db.refresh(goal)
    return goal
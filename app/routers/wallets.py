from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.get("/", response_model=List[schemas.WalletResponse])
def get_wallets(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).all()

@router.post("/", response_model=schemas.WalletResponse)
def create_wallet(
    wallet: schemas.WalletCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    new_wallet = models.Wallet(
        name=wallet.name, 
        balance=wallet.balance, 
        user_id=current_user.id
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

@router.delete("/{wallet_id}")
def delete_wallet(
    wallet_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id, 
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Dompet tidak ditemukan")
    
    db.delete(wallet)
    db.commit()
    return {"message": "Dompet berhasil dihapus"}
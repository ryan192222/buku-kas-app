import os
import shutil
from uuid import uuid4
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/transactions", tags=["Transactions"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[schemas.TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).order_by(models.Transaction.date.desc()).all()

@router.post("/", response_model=schemas.TransactionResponse)
def create_transaction(
    type: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    wallet_id: int = Form(...),
    description: Optional[str] = Form(None),
    receipt: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Cek kepemilikan dompet
    wallet = db.query(models.Wallet).filter(
        models.Wallet.id == wallet_id, 
        models.Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Dompet tidak ditemukan!")

    # Simpan file struk jika ada
    receipt_path = None
    if receipt and receipt.filename:
        file_ext = receipt.filename.split(".")[-1]
        file_name = f"{uuid4().hex}.{file_ext}"
        receipt_path = f"uploads/{file_name}"
        full_path = os.path.join("static", receipt_path)
        
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(receipt.file, buffer)

    # Otomatis update Saldo Dompet
    if type == "pemasukan":
        wallet.balance += amount
    elif type == "pengeluaran":
        wallet.balance -= amount

    # Buat Transaksi Baru
    new_trx = models.Transaction(
        type=type,
        amount=amount,
        category=category,
        description=description,
        wallet_id=wallet_id,
        receipt_image=receipt_path,
        user_id=current_user.id
    )
    
    db.add(new_trx)
    db.commit()
    db.refresh(new_trx)
    return new_trx

@router.delete("/{trx_id}")
def delete_transaction(
    trx_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    trx = db.query(models.Transaction).filter(
        models.Transaction.id == trx_id, 
        models.Transaction.user_id == current_user.id
    ).first()

    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    # Kembalikan saldo dompet
    wallet = db.query(models.Wallet).filter(models.Wallet.id == trx.wallet_id).first()
    if wallet:
        if trx.type == "pemasukan":
            wallet.balance -= trx.amount
        elif trx.type == "pengeluaran":
            wallet.balance += trx.amount

    # Hapus file foto struk jika ada
    if trx.receipt_image:
        full_path = os.path.join("static", trx.receipt_image)
        if os.path.exists(full_path):
            os.remove(full_path)

    db.delete(trx)
    db.commit()
    return {"message": "Transaksi berhasil dihapus"}
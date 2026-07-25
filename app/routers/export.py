import io
import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/excel")
def export_to_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Ambil transaksi user
    trxs = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()
    
    data = []
    for t in trxs:
        wallet = db.query(models.Wallet).filter(models.Wallet.id == t.wallet_id).first()
        data.append({
            "ID Transaksi": t.id,
            "Tanggal": t.date.strftime("%Y-%m-%d %H:%M"),
            "Jenis": t.type.capitalize(),
            "Kategori": t.category,
            "Jumlah (Rp)": t.amount,
            "Dompet": wallet.name if wallet else "Unknown",
            "Keterangan": t.description or "-"
        })

    df = pd.DataFrame(data)

    # Simpan ke stream memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan Keuangan')
    output.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="Laporan_Keuangan.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
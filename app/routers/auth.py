import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- KONFIGURASI PENGIRIMAN EMAIL (GMAIL) ---
SMTP_EMAIL = "ryanhidayah503@gmail.com"      # Ganti dengan email Gmail kamu
SMTP_PASSWORD = "qhsy jxbl rojz dsun"   # Ganti dengan Password Aplikasi (App Password) Gmail

def send_otp_email(receiver_email: str, otp_code: str):
    # Jika belum diisi kredensial Gmail-nya, cetak OTP di terminal untuk testing
    if SMTP_EMAIL == "buk":
        print(f"\n==========================================")
        print(f"📩 [DEMO OTP] Kode Verifikasi untuk {receiver_email}: {otp_code}")
        print(f"==========================================\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Buku Kas App <{SMTP_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"Kode Verifikasi Buku Kas: {otp_code}"

        body = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Verifikasi Akun Buku Kas Anda</h2>
            <p>Kode OTP verifikasi pendaftaran akun Anda adalah:</p>
            <h1 style="color: #2563eb; letter-spacing: 5px;">{otp_code}</h1>
            <p>Kode ini berlaku selama 10 menit. Jangan berikan kode ini kepada siapapun.</p>
        </div>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Gagal mengirim email: {e}")
        print(f"[FALLBACK OTP] Kode untuk {receiver_email}: {otp_code}")

@router.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if db_user and db_user.is_verified:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar & terverifikasi!")

    otp_code = str(random.randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    hashed_pwd = auth.get_password_hash(user_data.password)

    if db_user and not db_user.is_verified:
        db_user.hashed_password = hashed_pwd
        db_user.otp_code = otp_code
        db_user.otp_expires_at = otp_expiry
        db.commit()
    else:
        new_user = models.User(
            email=user_data.email,
            hashed_password=hashed_pwd,
            is_verified=False,
            otp_code=otp_code,
            otp_expires_at=otp_expiry
        )
        db.add(new_user)
        db.commit()

    send_otp_email(user_data.email, otp_code)

    return {"message": "Kode OTP telah dikirim ke email Anda!"}

@router.post("/verify-otp")
def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan!")

    if user.is_verified:
        return {"message": "Akun sudah terverifikasi. Silakan login."}

    if user.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Kode OTP salah!")

    if datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Kode OTP sudah kadaluwarsa! Silakan daftar ulang.")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None

    # Buat Dompet Default
    default_wallet = models.Wallet(name="Cash / Tunai", balance=0.0, user_id=user.id)
    db.add(default_wallet)
    db.commit()

    return {"message": "Verifikasi berhasil! Akun Anda telah aktif, silakan login."}

@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan!")
    
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    send_otp_email(data.email, otp)
    return {"message": "Kode OTP reset password telah dikirim ke email Anda."}

@router.post("/reset-password")
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or user.otp_code != data.otp_code:
        raise HTTPException(status_code=400, detail="Kode OTP salah atau tidak valid!")
    
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Kode OTP sudah kadaluwarsa!")
    
    user.hashed_password = auth.get_password_hash(data.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    return {"message": "Password berhasil diubah! Silakan login dengan password baru."}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Email belum diverifikasi! Silakan verifikasi kode OTP terlebih dahulu."
        )

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
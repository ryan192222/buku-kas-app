from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# --- SCHEMA USER & AUTH ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class VerifyOTP(BaseModel):
    email: EmailStr
    otp_code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- SCHEMA WALLET ---
class WalletBase(BaseModel):
    name: str
    balance: float = 0.0

class WalletCreate(WalletBase):
    pass

class WalletResponse(WalletBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- SCHEMA TRANSAKSI ---
class TransactionBase(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = None
    wallet_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    date: datetime
    receipt_image: Optional[str] = None
    user_id: int
    class Config:
        from_attributes = True

# --- SCHEMA BUDGET ---
class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float

class BudgetResponse(BudgetCreate):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- SCHEMA GOAL ---
class GoalCreate(BaseModel):
    title: str
    target_amount: float

class GoalResponse(GoalCreate):
    id: int
    current_amount: float
    user_id: int
    class Config:
        from_attributes = True
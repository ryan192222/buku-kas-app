from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import auth, wallets, transactions, budgets, goals, export, ai

# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Buku Kas Keuangan Pribadi (Super App)")

# Mount folder static untuk Frontend dan File Struk
app.mount("/static", StaticFiles(directory="static"), name="static")

# Daftarkan Router Backend
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(goals.router)
app.include_router(export.router)
app.include_router(ai.router)  # <--- Router AI didaftarkan di sini

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
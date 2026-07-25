from fastapi import APIRouter, HTTPException
from google import genai

router = APIRouter()

# Inisialisasi klien Gemini menggunakan mode Vertex AI (Google Cloud)
client = genai.Client(
    vertexai=True,
    project="dependable-star-481809-b5",
    location="us-central1"
)

@router.get("/ai/insight")
async def get_ai_insight():
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Berikan ringkasan dan saran pengelolaan keuangan yang bijak berdasarkan data pengeluaran."
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Gagal mengambil data dari AI: {str(e)}"
        )
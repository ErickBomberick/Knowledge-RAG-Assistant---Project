import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag import ask_question, ingest_file

app = FastAPI(
    title="Proiect",
    version="0.1.0"
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "RAG Assistant is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    allowed_extensions = [".pdf", ".txt", ".md"]
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Format invalid. Acceptăm doar PDF, TXT sau MD."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_file(str(file_path))

    return {
        "message": "Fișier încărcat și indexat cu succes.",
        "result": result,
    }


@app.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Întrebarea nu poate fi goală."
        )

    result = ask_question(request.question)

    return result
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag import ask_question, ingest_file, reset_vector_store, search_documents

app = FastAPI(
    title="Client Knowledge RAG Assistant",
    description="RAG assistant pentru documentație de business folosind Gemini, LangChain și ChromaDB.",
    version="0.2.0"
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class AskRequest(BaseModel):
    question: str
class SearchRequest(BaseModel):
    query: str
    k: int = 4


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

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = ingest_file(str(file_path))

        return {
            "message": "Fișier încărcat și indexat cu succes.",
            "result": result,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la procesarea fișierului: {str(error)}"
        )

@app.post("/ask")
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Întrebarea nu poate fi goală."
        )

    try:
        result = ask_question(request.question)
        return result

    except Exception as error:
        error_message = str(error)

        if "503" in error_message or "UNAVAILABLE" in error_message:
            raise HTTPException(
                status_code=503,
                detail="Serviciul AI este temporar indisponibil sau supraîncărcat. Încearcă din nou peste câteva minute."
            )

        if "429" in error_message or "quota" in error_message.lower():
            raise HTTPException(
                status_code=429,
                detail="Quota Gemini API a fost depășită. Verifică limitele contului sau încearcă mai târziu."
            )

        if "404" in error_message or "not found" in error_message.lower():
            raise HTTPException(
                status_code=502,
                detail="Modelul AI configurat nu este disponibil. Verifică GEMINI_MODEL din fișierul .env."
            )

        raise HTTPException(
            status_code=500,
            detail=f"Eroare la generarea răspunsului AI: {error_message}"
        )


@app.post("/reset")
def reset():
    try:
        result = reset_vector_store()
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la resetarea vector store-ului: {str(error)}"
        )
    
@app.post("/search")
def search(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query-ul nu poate fi gol."
        )

    if request.k < 1 or request.k > 10:
        raise HTTPException(
            status_code=400,
            detail="k trebuie să fie între 1 și 10."
        )

    try:
        result = search_documents(request.query, request.k)
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Eroare la căutarea în documente: {str(error)}"
        )
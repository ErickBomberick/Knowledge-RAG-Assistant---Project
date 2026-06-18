import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "client_documents"

gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

embeddings = GoogleGenerativeAIEmbeddings(
    model=embedding_model,
    task_type="RETRIEVAL_DOCUMENT",
)

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

llm = ChatGoogleGenerativeAI(
    model=gemini_model,
    temperature=0,
)


def load_document(file_path: str):
    file_extension = Path(file_path).suffix.lower()

    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError("Format nesuportat. Folosește PDF, TXT sau MD.")

    return loader.load()


def ingest_file(file_path: str) -> dict[str, Any]:
    documents = load_document(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
    )

    chunks = splitter.split_documents(documents)

    filename = Path(file_path).name

    for chunk in chunks:
        chunk.metadata["source_file"] = filename

    vector_store.add_documents(chunks)

    return {
        "file": filename,
        "pages_loaded": len(documents),
        "chunks_created": len(chunks),
    }


def ask_question(question: str) -> dict[str, Any]:
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(question)

    if not docs:
        return {
            "answer": "Nu am găsit informații relevante în documentele încărcate.",
            "sources": [],
        }

    context = "\n\n".join(
        [
            f"Sursa: {doc.metadata.get('source_file', 'necunoscut')}, "
            f"pagina: {doc.metadata.get('page', 'n/a')}\n"
            f"{doc.page_content}"
            for doc in docs
        ]
    )

    messages = [
        (
            "system",
            """
Ești un asistent AI pentru documentație de business.
Răspunde doar pe baza contextului primit.
Dacă informația nu există în context, spune clar că nu știi.
Răspunde în română.
Include la final o secțiune scurtă numită "Surse folosite".
""",
        ),
        (
            "human",
            f"""
Context:
{context}

Întrebare:
{question}
""",
        ),
    ]

    response = llm.invoke(messages)

    sources = []

    for doc in docs:
        sources.append(
            {
                "file": doc.metadata.get("source_file", "necunoscut"),
                "page": doc.metadata.get("page", "n/a"),
                "preview": doc.page_content[:250],
            }
        )

    return {
        "answer": response.content,
        "sources": sources,
    }
def reset_vector_store() -> dict[str, str]:
    vector_store.reset_collection()

    return {
        "message": "Vector store resetat cu succes."
    }
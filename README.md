# Client Knowledge RAG Assistant

A web-based Retrieval Augmented Generation (RAG) assistant that allows users to upload business documents and ask questions based on their content.

The project was built as a practical AI portfolio project focused on document understanding, semantic search, LLM integration, and source-based question answering.

## Overview

Client Knowledge RAG Assistant helps users query internal business documents such as CRM manuals, ERP documentation, support procedures, legal documents, financial documentation, or operational guides.

Instead of sending an entire document directly to an LLM, the application uses a RAG pipeline:

1. The user uploads a document.
2. The document is split into smaller text chunks.
3. Each chunk is converted into embeddings.
4. The embeddings are stored in a local vector database.
5. When the user asks a question, the application retrieves the most relevant chunks.
6. The selected context is sent to the LLM.
7. The AI generates an answer and returns the sources used.

## Features

* Upload PDF, TXT, and Markdown documents
* Document parsing and text chunking
* Embedding generation using Gemini embeddings
* Semantic search using ChromaDB
* AI-generated answers using Gemini
* Source previews for generated answers
* Indexed document list
* Reset functionality for clearing indexed documents
* Duplicate document prevention during indexing
* Error handling for model, quota, and API failures
* Simple web interface built with HTML, CSS, and JavaScript
* FastAPI backend with interactive Swagger documentation

## Tech Stack

### Backend

* Python
* FastAPI
* LangChain
* ChromaDB
* Google Gemini API
* Uvicorn

### Frontend

* HTML
* CSS
* JavaScript

### AI / RAG

* Gemini LLM for answer generation
* Gemini embeddings for semantic search
* ChromaDB as local vector database
* Recursive text splitting for document chunking

## Project Structure

```text
client-knowledge-rag-assistant/
│
├── app/
│   ├── main.py          # FastAPI routes and API logic
│   └── rag.py           # RAG logic: loading, chunking, embeddings, retrieval, AI answers
│
├── static/
│   ├── index.html       # Web interface
│   ├── style.css        # UI styling
│   └── script.js        # Frontend API calls
│
├── sample_docs/
│   └── crm_manual.md    # Demo document for testing
│
├── data/
│   └── uploads/         # Uploaded documents, ignored by Git
│
├── chroma_db/           # Local ChromaDB storage, ignored by Git
│
├── .env.example         # Example environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## How It Works

### 1. Document Upload

The user uploads a document through the web interface or the `/upload` endpoint.

The backend saves the file locally and sends it to the RAG pipeline.

### 2. Document Processing

The document is loaded using LangChain document loaders.

Supported formats:

* `.pdf`
* `.txt`
* `.md`

The text is split into chunks using `RecursiveCharacterTextSplitter`.

Current chunk settings:

```python
chunk_size = 600
chunk_overlap = 100
```

### 3. Embeddings and Vector Storage

Each chunk is converted into an embedding using Gemini embeddings.

The chunks and their metadata are stored in ChromaDB.

Each stored chunk includes metadata such as:

* source file name
* page number, when available

### 4. Semantic Search

When a user asks a question, the question is also converted into an embedding.

ChromaDB retrieves the most relevant chunks based on semantic similarity.

For AI answers, the application retrieves the top 2 most relevant chunks.

### 5. AI Answer Generation

The retrieved chunks are sent as context to Gemini.

The model is instructed to answer only using the provided context and to respond in Romanian.

The API returns:

* generated answer
* source previews
* source file names
* page metadata, when available

## API Endpoints

### `GET /`

Serves the web interface.

### `GET /health`

Checks if the API is running.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /upload`

Uploads and indexes a document.

Supported file types:

* PDF
* TXT
* Markdown

Example response:

```json
{
  "message": "Fișier încărcat și indexat cu succes.",
  "result": {
    "file": "crm_manual.md",
    "pages_loaded": 1,
    "chunks_created": 3
  }
}
```

### `POST /ask`

Generates an AI answer based on the indexed documents.

Example request:

```json
{
  "question": "Cine poate șterge clienți?"
}
```

Example response:

```json
{
  "answer": "Doar utilizatorii cu rol de administrator pot șterge clienți.",
  "sources": [
    {
      "file": "crm_manual.md",
      "page": "n/a",
      "preview": "Doar utilizatorii cu rol de administrator pot șterge clienți..."
    }
  ]
}
```

### `POST /search`

Performs semantic search without generating an AI answer.

This is useful for debugging and inspecting the retrieval step.

Example request:

```json
{
  "query": "ticket de suport",
  "k": 3
}
```

### `GET /documents`

Returns the list of indexed documents.

Example response:

```json
{
  "documents": [
    {
      "filename": "crm_manual.md",
      "chunks_created": 3
    }
  ]
}
```

### `POST /reset`

Clears the vector database and indexed document list.

Example response:

```json
{
  "message": "Vector store resetat cu succes."
}
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ErickBomberick/Knowledge-RAG-Assistant---Project.git
cd Knowledge-RAG-Assistant---Project
```

### 2. Create a virtual environment

On Windows:

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment file

Create a `.env` file based on `.env.example`.

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-2-preview
```

The `.env` file should not be committed to GitHub.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

Open the web interface:

```text
http://127.0.0.1:8000/
```

Open Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Demo Usage

A demo document is included in:

```text
sample_docs/crm_manual.md
```

Recommended test questions:

```text
Cine poate șterge clienți?
```

```text
Ce trebuie să conțină un ticket de suport?
```

```text
Unde apar facturile scadente?
```

## Error Handling

The application includes error handling for common API/model failures:

* invalid file formats
* empty questions
* Gemini quota errors
* unavailable AI model errors
* temporary model overload
* vector store reset errors

Instead of returning only generic internal server errors, the API returns clearer messages that help identify the cause of the problem.

## What I Learned

This project helped me practice:

* building APIs with FastAPI
* working with LLM APIs
* implementing a RAG pipeline
* using embeddings for semantic search
* storing vectors in ChromaDB
* using LangChain document loaders and text splitters
* designing source-based AI responses
* handling API errors and quota limitations
* building a simple frontend for an AI backend
* organizing a project for GitHub and portfolio use

## Future Improvements

Possible next improvements:

* add user authentication
* add support for multiple clients or workspaces
* add document deletion per file
* add conversation history
* add PostgreSQL with pgvector instead of local ChromaDB
* add Docker support
* add automated RAG evaluation
* add better PDF citation with exact page references
* deploy the application online
* add support for more file formats

## Status

MVP completed.

The project currently supports document upload, semantic indexing, AI question answering, source previews, indexed document listing, reset functionality, duplicate prevention, and a custom web interface.

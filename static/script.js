const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const searchButton = document.getElementById("searchButton");
const resetButton = document.getElementById("resetButton");

const answerBox = document.getElementById("answerBox");
const sourcesBox = document.getElementById("sourcesBox");
const loading = document.getElementById("loading");

const documentsBox = document.getElementById("documentsBox");

function setLoading(isLoading) {
    loading.classList.toggle("hidden", !isLoading);

    askButton.disabled = isLoading;
    searchButton.disabled = isLoading;
    uploadButton.disabled = isLoading;
    resetButton.disabled = isLoading;
}

function showAnswer(text) {
    answerBox.classList.remove("empty");
    answerBox.textContent = text;
}

function showSources(sources) {
    sourcesBox.classList.remove("empty");

    if (!sources || sources.length === 0) {
        sourcesBox.textContent = "Nu există surse pentru acest răspuns.";
        return;
    }

    sourcesBox.innerHTML = "";

    sources.forEach((source, index) => {
        const item = document.createElement("div");
        item.className = "source-item";

        const title = document.createElement("div");
        title.className = "source-title";
        title.textContent = `${index + 1}. ${source.file || "necunoscut"} - pagina ${source.page || "n/a"}`;

        const preview = document.createElement("div");
        preview.className = "source-preview";
        preview.textContent = source.preview || source.content || "";

        item.appendChild(title);
        item.appendChild(preview);
        sourcesBox.appendChild(item);
    });
}

async function uploadDocument() {
    const file = fileInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Alege mai întâi un fișier.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    uploadStatus.textContent = "Se încarcă și se indexează documentul...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Eroare la upload.");
        }

        uploadStatus.textContent =
            `Document indexat cu succes: ${data.result.file}. ` +
            `Chunks create: ${data.result.chunks_created}.`;
            
        await loadDocuments();
    } catch (error) {
        uploadStatus.textContent = error.message;
    } finally {
        setLoading(false);
    }
}

async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        showAnswer("Scrie o întrebare înainte.");
        return;
    }

    setLoading(true);
    showAnswer("Se generează răspunsul...");
    sourcesBox.textContent = "Se caută sursele...";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Eroare la generarea răspunsului.");
        }

        showAnswer(data.answer);
        showSources(data.sources);
    } catch (error) {
        showAnswer(error.message);
        sourcesBox.textContent = "Nu s-au putut încărca sursele.";
    } finally {
        setLoading(false);
    }
}

async function searchDocuments() {
    const query = questionInput.value.trim();

    if (!query) {
        showAnswer("Scrie un query înainte.");
        return;
    }

    setLoading(true);
    showAnswer("Se caută fragmente relevante...");
    sourcesBox.textContent = "";

    try {
        const response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query, k: 4 }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Eroare la căutare.");
        }

        showAnswer(`Am găsit ${data.results_count} fragmente relevante.`);
        showSources(data.results);
    } catch (error) {
        showAnswer(error.message);
        sourcesBox.textContent = "Nu s-au putut încărca rezultatele.";
    } finally {
        setLoading(false);
    }
}

async function resetVectorStore() {
    const confirmed = confirm("Sigur vrei să ștergi documentele indexate?");
    if (!confirmed) {
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/reset", {
            method: "POST",
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Eroare la reset.");
        }

        showAnswer(data.message);
        sourcesBox.textContent = "Sursele au fost resetate.";
        uploadStatus.textContent = "";

    await loadDocuments();
    } catch (error) {
        showAnswer(error.message);
    } finally {
        setLoading(false);
    }
}

async function loadDocuments() {
    try {
        const response = await fetch("/documents");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Eroare la încărcarea documentelor.");
        }

        documentsBox.classList.remove("empty");

        if (!data.documents || data.documents.length === 0) {
            documentsBox.classList.add("empty");
            documentsBox.textContent = "Nu există documente indexate încă.";
            return;
        }

        documentsBox.innerHTML = "";

        data.documents.forEach((indexedDocument) => {
            const item = document.createElement("div");
            item.className = "document-item";

            const title = document.createElement("div");
            title.className = "document-title";
            title.textContent = indexedDocument.filename;

            const meta = document.createElement("div");
            meta.className = "document-meta";
            meta.textContent = `Chunks create: ${indexedDocument.chunks_created}`;

            item.appendChild(title);
            item.appendChild(meta);
            documentsBox.appendChild(item);
        });
    } catch (error) {
        documentsBox.textContent = error.message;
    }
}

uploadButton.addEventListener("click", uploadDocument);
askButton.addEventListener("click", askQuestion);
searchButton.addEventListener("click", searchDocuments);
resetButton.addEventListener("click", resetVectorStore);

loadDocuments();
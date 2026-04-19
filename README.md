# 🤖 Smart FAQ Chatbot

A Retrieval-Augmented Generation (RAG) powered chatbot that turns your documents into an interactive knowledge base. Upload PDFs, Word files, or Markdown documents and ask questions in plain language. Built with **Google Gemini** and **ChromaDB**.

---

## ✨ Features
- **Upload & Parse:** Supports PDF, DOCX, MD, and TXT files.
- **Semantic Search:** Uses ChromaDB for fast, cosine-similarity based document retrieval.
- **AI Answers:** Google Gemini generates accurate answers based *only* on your documents.
- **Source Citations:** Every answer includes the exact document chunks used.
- **Premium UI:** Modern, dark glassmorphism interface built with Streamlit.

---

## 🛠️ Tech Stack
- **UI:** Streamlit
- **LLM & Embeddings:** Google Gemini (`gemini-2.5-flash`, `gemini-embedding-001`)
- **Vector DB:** ChromaDB
- **Document Parsing:** `pypdf`, `python-docx`

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- [Google Gemini API Key](https://aistudio.google.com/)

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd faq_bot

# Create virtual environment and activate
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
# .\.venv\Scripts\Activate.ps1 # Windows (PowerShell)
# source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/gemini-embedding-001
CHROMA_PERSIST_DIR=./chroma_db
COLLECTION_NAME=faq_collection
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K=5
```

### 4. Run the App
```bash
cd app
streamlit run app.py
```
App will be available at: **http://localhost:8501**

---

## 🐳 Docker Support
Run the application easily using Docker Compose (preserves ChromaDB data):
```bash
docker compose up --build
```
Access at: **http://localhost:8503**

---


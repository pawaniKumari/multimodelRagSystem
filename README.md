# 🇱🇰 Sri Lanka Tourism Multimodal RAG System

An end-to-end Multimodal Retrieval-Augmented Generation (RAG) system built with **Streamlit**, **PostgreSQL (pgvector)**, and **Hugging Face Transformers**.

This system allows users to search, filter, and interact with information about Sri Lankan tourist destinations using a combination of **Structured SQL Queries**, **Semantic Text Search**, and **CLIP Visual Similarity Search**.

---

## 📌 Features & Architecture

The application is structured into four core search capabilities:

1. **🔀 Hybrid RAG Search (Main Demo):**
   - Combines relational SQL filtering (e.g., category, entrance fee caps) with vector semantic search (`all-MiniLM-L6-v2`).
   - Passes retrieved context directly to an LLM to generate natural, context-aware answers for tourism queries.

2. **📊 Structured Search:**
   - Standard relational SQL queries over structured metadata (district, category, entrance fee, accessibility, trekking difficulty).

3. **📝 Semantic Search:**
   - Natural language vector search powered by text embeddings (`384-dim`) to locate places based on descriptions.

4. **🖼️ Image Similarity Search:**
   - Powered by **CLIP** (`openai/clip-vit-base-patch32`, `512-dim` visual embeddings).
   - **Text-to-Image:** Find destinations matching a descriptive query (e.g., _"leopard in safari forest"_).
   - **Image-to-Image:** Upload a sample photo to retrieve visually similar destinations across Sri Lanka.

---

## ⚙️ Installation & Setup Instructions

### 1. Prerequisites

Ensure you have the following installed on your system:

- **Python 3.10+**
- **PostgreSQL (v13+)** with the **`pgvector`** extension enabled.

---

### 2. Database & `pgvector` Setup

1. Open your PostgreSQL tool (pgAdmin or `psql`) and create a target database:

   ```sql
   CREATE DATABASE srilanka_tourism;
   ```

2. Enable the pgvector extension inside your newly created database:
   ```sql
   \c srilanka_tourism;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## 3. Environment & Dependency Setup

Navigate to the project directory:

```bash
cd rag
```

Create and activate a virtual environment:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install required Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables (.env)

Create a `.env` file in the root directory (`rag/.env`) and add your database configuration:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=srilanka_tourism
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

---

## 5. Data Ingestion & Database Population

Populate PostgreSQL with text embeddings and CLIP visual embeddings generated from your dataset:

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH="."
python -m scripts.ingest_data
```

**Linux / macOS:**

```bash
PYTHONPATH=. python3 -m scripts.ingest_data
```

---

## 6. Test Embedding Setup (Optional Verification)

To verify that local image embedding generation is functioning before running the app:

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH="."
python -c "from src.embeddings import generate_image_embedding_from_file; vec = generate_image_embedding_from_file('data/images/bambarakanda.jpg'); print('Vector Length:', len(vec) if vec else 'NULL')"
```

---

## 7. Run the Application

Launch the Streamlit web app:

```bash
python -m streamlit run app.py
```

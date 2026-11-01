# ResearchLens AI 🔬
### Agentic AI System for Research Paper Discovery, Verification and Scientific Reasoning

ResearchLens AI is an AI-powered research assistant designed to help students and researchers discover relevant research papers, extract important findings, compare methodologies, verify scientific claims and identify potential research gaps.

Instead of manually reading hundreds of research papers, users can upload PDF documents and ask research-related questions. The system retrieves relevant evidence using hybrid search and generates evidence-backed answers with citations.

---

## 🎯 Project Objectives

- Upload and process multiple research papers in PDF format.
- Extract text and organize research papers into meaningful chunks.
- Search papers using keyword-based and semantic search.
- Retrieve relevant research evidence.
- Generate answers supported by paper references.
- Compare methodologies and experimental findings.
- Identify contradictions between research papers.
- Verify claims against retrieved evidence.
- Highlight limitations and potential research gaps.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | Backend API framework |
| Streamlit | Frontend interface |
| PyMuPDF | PDF text extraction |
| Sentence Transformers | Semantic embeddings |
| BM25 | Keyword-based retrieval |
| SQLite | Database storage |
| Git & GitHub | Version control and collaboration |

---

## 🏗️ Project Architecture

```text
ResearchLens-AI/
│
├── backend/
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── modules/
│   ├── document_processor.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── retrieval.py
│   ├── research_engine.py
│   └── verification.py
│
├── data/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sristy09agr-ctrl/ResearchLens-AI.git
```

### 2. Open the project folder

```bash
cd ResearchLens-AI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```bash
venv\Scripts\Activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Start the FastAPI backend

```bash
uvicorn backend.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit frontend

Open another terminal and run:

```bash
streamlit run frontend/app.py
```

---

## 🔍 Core Modules

**1. Document Processor**
- Accepts PDF documents.
- Extracts text using PyMuPDF.
- Preserves page-level information.

**2. Text Chunking**
- Divides extracted text into smaller passages.
- Maintains paper and page references.

**3. Embedding Generation**
- Converts text passages into numerical embeddings.
- Uses Sentence Transformers.

**4. Hybrid Retrieval**
- BM25 for keyword matching.
- Dense vector search for semantic similarity.
- Combines results to improve evidence retrieval.

**5. Research Engine**
- Synthesizes retrieved evidence.
- Compares findings across papers.
- Generates evidence-backed research summaries.

**6. Claim Verification**
- Checks claims against retrieved passages.
- Identifies supported, contradicted and insufficiently supported claims.

---

## 👥 Team Collaboration

This project is developed collaboratively by a team of three members.

GitHub repository:

https://github.com/sristy09agr-ctrl/ResearchLens-AI

Main development branch: `main`

---

## 📊 Expected Deliverables

- Interactive research assistant.
- PDF upload and processing.
- Hybrid keyword and semantic retrieval.
- Evidence-backed answers with citations.
- Research paper comparison.
- Claim verification.
- Research gap identification.
- Structured research report.

---

## ⚠️ Limitations

- The quality of answers depends on the quality of uploaded research papers.
- Scanned PDFs may require OCR support.
- Generated research gaps require human validation.
- Retrieved evidence does not automatically establish scientific truth.
- The system is intended as a research assistance tool, not a replacement for academic judgment.

---

## 🔮 Future Scope

- Cross-paper citation graph.
- Advanced reranking using cross-encoders.
- Agentic query decomposition and iterative retrieval.
- Improved contradiction detection.
- Support for larger research collections.
- Downloadable research reports.

---

**ResearchLens AI — Turning Research Papers into Research Insights.**

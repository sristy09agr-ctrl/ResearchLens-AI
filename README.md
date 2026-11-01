# 🔬 ResearchLens AI
### Agentic AI System for Research Paper Discovery, Verification, and Scientific Reasoning

**ResearchLens AI** is an AI-powered research assistant designed to help students, researchers, and academics discover relevant research papers, extract key findings, compare research methodologies, verify scientific claims, and identify potential research gaps.

Instead of manually reviewing hundreds of research papers, users can upload PDF documents and ask research-related questions. The system uses **hybrid information retrieval**, combining keyword-based and semantic search, to retrieve relevant research evidence and generate evidence-backed responses with paper references and citations.

The goal of ResearchLens AI is to make academic research more efficient, organized, and evidence-driven.

---

## 🎯 Project Objectives

- Upload and process multiple research papers in PDF format.
- Extract text and organize research documents into meaningful chunks.
- Perform keyword-based and semantic searches across uploaded papers.
- Retrieve relevant research passages using hybrid search.
- Generate evidence-backed answers with source references and citations.
- Compare research methodologies, approaches, and experimental findings.
- Identify similarities and contradictions across research papers.
- Verify scientific claims against retrieved research evidence.
- Highlight research limitations and potential research gaps.
- Generate structured research insights to support academic decision-making.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| PDF Upload | Upload multiple research papers in PDF format. |
| Text Extraction | Extract research content using PyMuPDF. |
| Text Chunking | Divide documents into smaller, searchable passages. |
| Semantic Search | Retrieve relevant passages based on contextual meaning. |
| Keyword Search | Find relevant content using BM25 ranking. |
| Hybrid Retrieval | Combine keyword-based and semantic retrieval. |
| Evidence-Based Q&A | Generate answers grounded in retrieved research passages. |
| Paper Comparison | Compare findings and methodologies across papers. |
| Claim Verification | Identify supported, contradicted, and insufficiently supported claims. |
| Research Gap Identification | Highlight potential limitations and unexplored research areas. |

---

## 🛠️ Technology Stack

The following technologies and tools are used in the project:

### Frontend Technologies

| Technology | Purpose |
|---|---|
| Streamlit | Develop the interactive web-based user interface. |
| Python | Implement frontend application logic and interactions. |

### Backend Technologies

| Technology | Purpose |
|---|---|
| Python | Core backend programming language. |
| FastAPI | Build RESTful APIs and handle frontend-backend communication. |
| Uvicorn | Run the FastAPI application server. |

### AI and Information Retrieval

| Technology | Purpose |
|---|---|
| Sentence Transformers | Generate semantic embeddings for research passages. |
| BM25 | Perform keyword-based document retrieval. |
| Hybrid Search | Combine semantic and keyword-based retrieval results. |

### Document Processing and Storage

| Technology | Purpose |
|---|---|
| PyMuPDF | Extract text and page-level information from PDF documents. |
| SQLite | Store structured application and document-related metadata. |

### Development Tools

| Technology | Purpose |
|---|---|
| Git | Track source code changes and manage development. |
| GitHub | Host the project repository and support team collaboration. |
| Virtual Environment | Isolate project dependencies. |
| pip | Install and manage Python packages. |

---

## 🏗️ System Architecture

ResearchLens AI follows a modular architecture consisting of a frontend, backend, document-processing pipeline, retrieval system, and research analysis modules.

### Architecture Overview

```text
                 USER
                   |
                   v
          STREAMLIT FRONTEND
              (app.py)
                   |
                   v
             FASTAPI BACKEND
              (main.py)
                   |
          +--------+--------+
          |                 |
          v                 v
    PDF PROCESSING     USER QUERIES
          |                 |
          v                 v
     TEXT EXTRACTION    QUERY PROCESSING
      (PyMuPDF)              |
          |                 |
          v                 |
      TEXT CHUNKING          |
          |                 |
          v                 |
    EMBEDDING GENERATION     |
 (Sentence Transformers)    |
          |                 |
          +--------+--------+
                   |
                   v
             HYBRID SEARCH
                   |
          +--------+--------+
          |                 |
          v                 v
       BM25 SEARCH     SEMANTIC SEARCH
          |                 |
          +--------+--------+
                   |
                   v
          EVIDENCE RETRIEVAL
                   |
                   v
          RESEARCH ENGINE
                   |
          +--------+--------+
          |        |        |
          v        v        v
       ANSWER   COMPARISON  CLAIM
     GENERATION   ENGINE  VERIFICATION
          |        |        |
          +--------+--------+
                   |
                   v
          EVIDENCE-BACKED
              RESULTS
                   |
                   v
           STREAMLIT UI
```

### Project Folder Structure

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
│   └── (Uploaded documents and application data)
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation and Setup

Follow these steps to set up ResearchLens AI on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/sristy09agr-ctrl/ResearchLens-AI.git
```

### 2. Navigate to the Project Directory

```bash
cd ResearchLens-AI
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 5. Install Project Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

ResearchLens AI consists of two main components: the FastAPI backend and the Streamlit frontend.

Both components must be running to use the complete application.

### Step 1: Start the FastAPI Backend

Open a terminal in the project root directory and execute:

```bash
uvicorn backend.main:app --reload
```

The backend server will start at:

```text
http://127.0.0.1:8000
```

**API Documentation (Swagger UI):**

```text
http://127.0.0.1:8000/docs
```

### Step 2: Start the Streamlit Frontend

Open another terminal, activate the virtual environment, and execute:

```bash
streamlit run frontend/app.py
```

The Streamlit application will open in your browser, typically at:

```text
http://localhost:8501
```

---

## 🔍 Core Modules and Their Responsibilities

### 1. Document Processor (`document_processor.py`)

Responsible for processing uploaded research papers.

**Responsibilities:**
- Accept PDF research documents.
- Extract textual content using PyMuPDF.
- Retrieve page-level information.
- Organize extracted content for further processing.

### 2. Text Chunking (`chunking.py`)

Converts extracted research text into smaller, manageable passages.

**Responsibilities:**
- Divide lengthy research documents into smaller text chunks.
- Maintain document and page references.
- Prepare passages for embedding generation and retrieval.

### 3. Embedding Generation (`embeddings.py`)

Converts text passages into numerical vector representations.

**Responsibilities:**
- Generate semantic embeddings using Sentence Transformers.
- Represent research passages in vector space.
- Support meaning-based similarity comparisons.

### 4. Hybrid Retrieval (`retrieval.py`)

Retrieves relevant research passages using a combination of keyword-based and semantic search.

**Responsibilities:**
- Use BM25 for keyword-based retrieval.
- Use semantic embeddings for contextual retrieval.
- Combine retrieval results to improve evidence discovery.
- Return relevant passages for downstream analysis.

### 5. Research Engine (`research_engine.py`)

Processes retrieved research evidence and generates meaningful research insights.

**Responsibilities:**
- Synthesize information from multiple research papers.
- Generate research-related answers.
- Compare methodologies and experimental findings.
- Identify similarities and differences between studies.
- Support evidence-based research summaries.

### 6. Claim Verification (`verification.py`)

Evaluates scientific claims against retrieved research evidence.

**Responsibilities:**
- Analyze user-provided scientific claims.
- Retrieve relevant supporting or contradicting passages.
- Classify claims as:
  - Supported
  - Contradicted
  - Insufficiently supported
- Provide evidence references for verification results.

---

## 🔄 Application Workflow

The system follows a structured workflow to transform uploaded research papers into useful research insights.

1. **Document Upload:** Users upload one or more research papers in PDF format through the Streamlit interface.
2. **Text Extraction:** PyMuPDF extracts textual content and page-level information.
3. **Text Chunking:** Extracted content is divided into smaller passages.
4. **Embedding Generation:** Sentence Transformers converts passages into semantic embeddings.
5. **Query Processing:** The user's research question is processed by the backend.
6. **Hybrid Retrieval:** BM25 and semantic search retrieve relevant passages.
7. **Evidence Analysis:** The research engine analyzes retrieved passages.
8. **Research Reasoning:** The system generates answers, compares papers, or verifies scientific claims.
9. **Result Presentation:** Evidence-backed results and source references are displayed through the Streamlit interface.

---

## 👥 Team Collaboration

ResearchLens AI is developed collaboratively by a team of three members.

**GitHub Repository:**

[ResearchLens-AI](https://github.com/sristy09agr-ctrl/ResearchLens-AI)

**Main Development Branch:** `main`

Git and GitHub are used for source code management, version control, and collaborative development.

---

## 📊 Expected Deliverables

The project aims to deliver the following functionalities:

- Interactive AI-powered research assistant.
- Multiple PDF document upload and processing.
- Automatic text extraction and chunking.
- Semantic and keyword-based hybrid retrieval.
- Evidence-backed question answering with citations.
- Cross-paper research comparison.
- Scientific claim verification.
- Identification of research limitations and potential gaps.
- Structured research summaries and reports.

---

## ⚠️ Limitations

- Answer quality depends on the quality, relevance, and completeness of uploaded research papers.
- Scanned PDFs may require additional OCR functionality for accurate text extraction.
- Generated research gaps are suggestions and require validation by human researchers.
- Retrieved evidence does not automatically establish scientific truth.
- Claim verification depends on the available evidence and cannot guarantee absolute scientific correctness.
- The system's retrieval quality depends on embedding models, chunking strategies, and search configuration.
- ResearchLens AI is designed as a research assistance tool and does not replace expert academic judgment.

---

## 🔮 Future Scope

Several improvements can extend the capabilities of ResearchLens AI:

- **Agentic Query Decomposition:** Break complex research questions into smaller, manageable subqueries.
- **Iterative Retrieval:** Perform multiple retrieval cycles to improve evidence coverage.
- **Advanced Reranking:** Integrate cross-encoder models to improve retrieval relevance.
- **Citation Graph Analysis:** Explore relationships between research papers through citation networks.
- **Improved Contradiction Detection:** Identify conflicting experimental results and scientific arguments.
- **OCR Integration:** Support scanned research documents and image-based PDFs.
- **Large-Scale Document Processing:** Improve performance when working with extensive research collections.
- **Downloadable Research Reports:** Export structured research summaries and findings.
- **Advanced Research Agents:** Introduce specialized agents for literature review, comparison, verification, and research gap analysis.

---

## 🔐 Disclaimer

ResearchLens AI is intended to assist with academic research, literature exploration, and scientific evidence analysis.

AI-generated responses may contain errors or incomplete interpretations. Users should always consult the original research papers and independently validate important scientific conclusions before relying on them in academic or professional work.

---

## 🌟 Project Vision

**ResearchLens AI — Turning Research Papers into Research Insights.**

Making scientific literature discovery, verification, and reasoning faster, smarter, and more accessible.

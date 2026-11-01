# 🔬 ResearchLens AI
### Agentic AI System for Research Paper Discovery, Verification, and Scientific Reasoning

**ResearchLens AI** is an AI-powered research assistant designed to help students, researchers, and academics discover relevant research papers, extract important findings, compare research methodologies, verify scientific claims, and identify potential research gaps.

Instead of manually reviewing hundreds of research papers, users can upload PDF documents and ask research-related questions. The system uses **Hybrid Information Retrieval**, combining keyword-based and semantic search, to retrieve relevant research evidence and generate evidence-backed responses with source references and citations.

ResearchLens AI aims to make academic research more efficient, organized, and evidence-driven.

---

## 🎯 Project Objectives

- Upload and process multiple research papers in PDF format.
- Extract text and organize research documents into meaningful chunks.
- Perform keyword-based and semantic searches across uploaded papers.
- Retrieve relevant research evidence using hybrid search.
- Generate evidence-backed answers with paper references and citations.
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
| Text Chunking | Divide documents into smaller searchable passages. |
| Semantic Search | Retrieve relevant passages based on contextual meaning. |
| Keyword Search | Find relevant content using BM25 ranking. |
| Hybrid Retrieval | Combine keyword-based and semantic retrieval. |
| Evidence-Based Q&A | Generate answers based on retrieved research passages. |
| Paper Comparison | Compare findings and methodologies across research papers. |
| Claim Verification | Identify supported, contradicted, and insufficiently supported claims. |
| Research Gap Identification | Highlight potential limitations and unexplored research areas. |

---

## 🛠️ Technology Stack

The project uses the following technologies and tools:

### 1. Frontend Technologies

| Technology | Purpose |
|---|---|
| React.js | Build the interactive and dynamic user interface. |
| JavaScript | Implement frontend functionality and application logic. |
| HTML5 | Structure the web application interface. |
| CSS3 | Style components and create responsive layouts. |
| React Components | Build reusable UI elements. |
| Fetch API / Axios | Communicate with backend APIs. |

### 2. Backend Technologies

| Technology | Purpose |
|---|---|
| Python | Core backend programming language. |
| FastAPI | Develop RESTful APIs and handle frontend-backend communication. |
| Uvicorn | Run the FastAPI application server. |

### 3. AI and Information Retrieval

| Technology | Purpose |
|---|---|
| Sentence Transformers | Generate semantic embeddings for research passages. |
| BM25 | Perform keyword-based document retrieval. |
| Hybrid Search | Combine keyword-based and semantic retrieval results. |

### 4. Document Processing and Storage

| Technology | Purpose |
|---|---|
| PyMuPDF | Extract text and page-level information from PDF documents. |
| SQLite | Store structured application and document-related metadata. |

### 5. Development Tools

| Technology | Purpose |
|---|---|
| Git | Track source code changes and manage development. |
| GitHub | Host the project repository and support collaboration. |
| npm | Manage frontend dependencies and packages. |
| pip | Install and manage Python dependencies. |
| Virtual Environment | Isolate backend project dependencies. |

---

## 🏗️ System Architecture

ResearchLens AI follows a modular architecture consisting of a React.js frontend, FastAPI backend, document-processing pipeline, hybrid retrieval system, and research analysis modules.

### Architecture Overview

```text
                   USER
                     |
                     v
             REACT.JS FRONTEND
                (JavaScript)
                     |
                     | HTTP Requests
                     | REST API
                     v
              FASTAPI BACKEND
                 (Python)
                     |
             +-------+-------+
             |               |
             v               v
        PDF UPLOAD       USER QUERIES
             |               |
             v               v
       DOCUMENT          QUERY
       PROCESSING       PROCESSING
             |               |
             v               |
       TEXT EXTRACTION       |
         (PyMuPDF)           |
             |               |
             v               |
        TEXT CHUNKING        |
             |               |
             v               |
     EMBEDDING GENERATION    |
    (Sentence Transformers) |
             |               |
             +-------+-------+
                     |
                     v
               HYBRID SEARCH
                     |
             +-------+-------+
             |               |
             v               v
         BM25 SEARCH    SEMANTIC SEARCH
             |               |
             +-------+-------+
                     |
                     v
             EVIDENCE RETRIEVAL
                     |
                     v
              RESEARCH ENGINE
                     |
             +-------+-------+
             |       |       |
             v       v       v
          ANSWER  PAPER   CLAIM
        GENERATION COMPARISON VERIFICATION
             |       |       |
             +-------+-------+
                     |
                     v
              EVIDENCE-BACKED
                  RESULTS
                     |
                     v
               FASTAPI RESPONSE
                     |
                     v
              REACT.JS FRONTEND
                     |
                     v
               USER INTERFACE
```

### Frontend Architecture

The frontend is developed using React.js and JavaScript.

**Responsibilities:**

- Provide an interactive web interface.
- Allow users to upload research papers.
- Display uploaded document information.
- Accept research-related questions.
- Send requests to FastAPI backend endpoints.
- Display AI-generated research answers.
- Present retrieved evidence and paper citations.
- Display research comparisons and claim verification results.

### Backend Architecture

The backend is developed using Python and FastAPI.

**Responsibilities:**

- Handle HTTP requests from the React frontend.
- Receive and process uploaded PDF documents.
- Extract and organize research text.
- Generate semantic embeddings.
- Perform keyword-based and semantic retrieval.
- Analyze retrieved research evidence.
- Generate research insights and answers.
- Verify scientific claims.
- Return structured responses to the frontend.

---

## 📁 Project Folder Structure

The following represents the logical project organization. Adjust folder names to match the actual repository structure.

```text
ResearchLens-AI/
│
├── frontend/
│   ├── public/
│   │
│   ├── src/
│   │   ├── components/
│   │   │
│   │   ├── pages/
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── assets/
│   │   │
│   │   ├── App.js
│   │   └── index.js
│   │
│   ├── package.json
│   └── package-lock.json
│
├── backend/
│   └── main.py
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

### Folder and File Descriptions

| Folder/File | Responsibility |
|---|---|
| `frontend/` | Contains the React.js frontend application. |
| `frontend/public/` | Stores static frontend assets. |
| `frontend/src/` | Contains React application source code. |
| `frontend/src/components/` | Contains reusable React components. |
| `frontend/src/pages/` | Contains application pages and views. |
| `frontend/src/services/` | Handles API communication with FastAPI. |
| `frontend/src/assets/` | Stores images, icons, and other frontend assets. |
| `frontend/src/App.js` | Main React application component. |
| `backend/main.py` | Main FastAPI application entry point. |
| `modules/` | Contains document processing, retrieval, and research logic. |
| `data/` | Stores uploaded documents and application data. |
| `requirements.txt` | Lists Python backend dependencies. |
| `package.json` | Defines frontend dependencies and scripts. |
| `.gitignore` | Specifies files and folders excluded from Git tracking. |

---

## ⚙️ Installation and Setup

Follow these steps to run ResearchLens AI locally.

### Prerequisites

Make sure the following tools are installed:

- Python 3.10 or later (depending on dependency compatibility).
- Node.js and npm.
- Git.
- A code editor such as Visual Studio Code.

### 1. Clone the Repository

```bash
git clone https://github.com/sristy09agr-ctrl/ResearchLens-AI.git
```

### 2. Navigate to the Project Directory

```bash
cd ResearchLens-AI
```

### 3. Set Up the Backend

Create a Python virtual environment:

```bash
python -m venv venv
```

**Activate the virtual environment:**

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the React.js dependencies:

```bash
npm install
```

---

## 🚀 Running the Application

ResearchLens AI consists of two main components:

1. React.js frontend.
2. Python FastAPI backend.

Both applications must run simultaneously.

### Step 1: Start the Backend Server

From the project root directory, execute:

```bash
uvicorn backend.main:app --reload
```

The backend server will run at:

```text
http://127.0.0.1:8000
```

**FastAPI Swagger Documentation:**

```text
http://127.0.0.1:8000/docs
```

### Step 2: Start the React.js Frontend

Open another terminal:

```bash
cd frontend
```

Start the React development server:

```bash
npm start
```

If the project uses Vite instead of Create React App, use:

```bash
npm run dev
```

The frontend URL depends on your React setup. Common development addresses are:

```text
http://localhost:3000
```

or

```text
http://localhost:5173
```

### Step 3: Use the Application

Once both servers are running:

1. Open the React application in your browser.
2. Upload one or more research papers.
3. Allow the backend to extract and process document content.
4. Enter a research-related question.
5. Retrieve relevant evidence using hybrid search.
6. View evidence-backed answers and references.
7. Compare research papers or verify scientific claims.

---

## 🔗 Frontend and Backend Communication

The React.js frontend communicates with the FastAPI backend through REST APIs using HTTP requests.

### Communication Workflow

1. A user performs an action through the React interface.
2. React sends an HTTP request to the corresponding FastAPI endpoint.
3. FastAPI receives and processes the request.
4. The backend executes the required document-processing or research operation.
5. FastAPI returns a structured JSON response.
6. React receives the response and updates the user interface.

### Example API Communication

A React frontend can communicate with the backend using the Fetch API.

```javascript
const response = await fetch(
  "http://127.0.0.1:8000/your-api-endpoint"
);

const data = await response.json();
```

For PDF uploads, the frontend can use `FormData`:

```javascript
const formData = new FormData();

formData.append("file", selectedFile);

const response = await fetch(
  "http://127.0.0.1:8000/your-upload-endpoint",
  {
    method: "POST",
    body: formData
  }
);

const result = await response.json();
```

**Note:** The endpoint paths above are illustrative. Replace them with the actual routes implemented in `backend/main.py`. The backend should also configure CORS to allow requests from the frontend development origin.

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

Retrieves relevant research passages using keyword-based and semantic search.

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

## 🔄 Complete Application Workflow

ResearchLens AI follows a structured workflow to transform uploaded research papers into meaningful research insights.

| Step | Process | Description |
|---|---|---|
| 1 | Document Upload | User uploads research papers through the React interface. |
| 2 | API Communication | React sends PDF files to FastAPI. |
| 3 | Text Extraction | PyMuPDF extracts document text and page information. |
| 4 | Text Chunking | Extracted text is divided into smaller passages. |
| 5 | Embedding Generation | Sentence Transformers creates semantic embeddings. |
| 6 | Query Processing | The backend processes the user's research question. |
| 7 | Hybrid Retrieval | BM25 and semantic search retrieve relevant passages. |
| 8 | Evidence Analysis | The research engine analyzes retrieved passages. |
| 9 | Research Reasoning | The system generates answers, comparisons, or claim verification results. |
| 10 | Result Presentation | FastAPI returns results and React displays them to the user. |

---

## 👥 Team Collaboration

ResearchLens AI is developed collaboratively by a team of three members.

**GitHub Repository:**

https://github.com/sristy09agr-ctrl/ResearchLens-AI

**Main Development Branch:** `main`

Git and GitHub are used for source code management, version control, and collaborative development.

---

## 📊 Expected Deliverables

The project aims to deliver the following functionalities:

- Interactive React.js-based research assistant.
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
- Claim verification depends on available evidence and cannot guarantee absolute scientific correctness.
- Retrieval quality depends on embedding models, chunking strategies, and search configuration.
- The system is designed as a research assistance tool and does not replace expert academic judgment.

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

AI-generated responses may contain errors or incomplete interpretations. Users should always consult original research papers and independently validate important scientific conclusions before relying on them in academic or professional work.

---

## 🌟 Project Vision

**ResearchLens AI — Turning Research Papers into Research Insights.**

Making scientific literature discovery, verification, and reasoning faster, smarter, and more accessible.

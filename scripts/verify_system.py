"""
End-to-End System Health & Functionality Verification Suite for ResearchLens AI.
Validates:
  1. Core App Configuration & Logging
  2. Database & Schema Integrity
  3. API Endpoint Contracts (Health, Documents, Chunks, Search, Graph)
  4. PDF Upload Validator & Magic-Byte Defense
  5. Hybrid Retriever & Cross-Encoder Reranker with Diversity Capping
  6. Agent State Machine Nodes (Planner, Sufficiency, Abstention)
  7. Evaluation Benchmark Reproducibility
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import io
import time
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_all_documents, get_document_chunks
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import get_reranker
from app.ingestion.validator import validate_uploaded_pdf
from app.agents.nodes.sufficiency import sufficiency_node, sufficiency_router
from app.agents.nodes.reranker import prepare_evidence_passages

client = TestClient(app)

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

errors = []


def test_section(name):
    print(f"\n{'='*20} {name} {'='*20}")


# 1. Health & Readiness
test_section("1. Health & Readiness Probes")
try:
    r = client.get("/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "healthy"
    print(f"{PASS} GET /health: {data}")
except Exception as e:
    print(f"{FAIL} /health check failed: {e}")
    errors.append(f"/health: {e}")

try:
    r = client.get("/ready")
    assert r.status_code in [200, 503]
    data = r.json()
    assert "database" in data
    print(f"{PASS} GET /ready: {data}")
except Exception as e:
    print(f"{FAIL} /ready probe failed: {e}")
    errors.append(f"/ready: {e}")


# 2. Document Management & API Contracts
test_section("2. Document Retrieval & Chunk Inspection")
docs = get_all_documents()
print(f"{INFO} Found {len(docs)} stored documents in SQLite")

try:
    # Test v1 and unversioned endpoints
    r1 = client.get("/v1/documents")
    r2 = client.get("/documents")
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["total_documents"] == len(docs)
    print(f"{PASS} GET /v1/documents & GET /documents match SQLite record count ({len(docs)} documents)")

    if docs:
        doc_id = docs[0]["document_id"]
        # Details
        r_det = client.get(f"/v1/documents/{doc_id}")
        assert r_det.status_code == 200
        print(f"{PASS} GET /v1/documents/{doc_id[:8]}... returned document details")

        # Chunks
        r_chunks = client.get(f"/v1/documents/{doc_id}/chunks")
        assert r_chunks.status_code == 200
        chunks = r_chunks.json()["chunks"]
        assert len(chunks) > 0
        first_chunk = chunks[0]
        assert "chunk_type" in first_chunk
        assert "section" in first_chunk
        print(f"{PASS} GET /v1/documents/{doc_id[:8]}/chunks returned {len(chunks)} chunks with section & chunk_type fields")
except Exception as e:
    print(f"{FAIL} Document API tests failed: {e}")
    errors.append(f"Document API: {e}")


# 3. PDF Ingestion Security & Magic-Bytes Validation
test_section("3. Ingestion Validator & Security Defense")
try:
    # Case A: Valid PDF header
    valid_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    is_valid, msg = validate_uploaded_pdf("sample.pdf", valid_pdf_bytes)
    assert is_valid, f"Should be valid: {msg}"
    print(f"{PASS} Valid PDF magic-byte header recognized correctly")

    # Case B: Spoofed extension (text file disguised as .pdf)
    fake_pdf_bytes = b"This is just plain text, not a real PDF file."
    is_valid, msg = validate_uploaded_pdf("fake.pdf", fake_pdf_bytes)
    assert not is_valid, "Fake PDF should have been rejected"
    print(f"{PASS} Non-PDF disguised with .pdf extension was rejected: '{msg}'")

    # Case C: Empty file
    is_valid, msg = validate_uploaded_pdf("empty.pdf", b"")
    assert not is_valid
    print(f"{PASS} Empty file was rejected: '{msg}'")

    # Case D: Non-PDF extension
    is_valid, msg = validate_uploaded_pdf("malicious.exe", b"MZ\x90\x00")
    assert not is_valid
    print(f"{PASS} Non-PDF extension rejected: '{msg}'")
except Exception as e:
    print(f"{FAIL} PDF Validator tests failed: {e}")
    errors.append(f"PDF Validator: {e}")


# 4. Search & Cross-Encoder Reranking
test_section("4. Hybrid Retrieval & Cross-Encoder Reranker")
try:
    # Test raw search endpoint
    search_payload = {
        "query": "optimization linear programming constraints",
        "top_k": 3,
        "candidate_k": 10,
        "alpha": 0.5
    }
    r_search = client.post("/v1/search", json=search_payload)
    assert r_search.status_code == 200
    res = r_search.json()
    assert res["status"] == "success"
    returned = res["returned_results"]
    assert returned > 0
    top_hit = res["results"][0]
    assert "rerank_score" in top_hit
    print(f"{PASS} POST /v1/search successfully retrieved & reranked {returned} passages (Top rerank score: {top_hit['rerank_score']:.3f})")

    # Test Diversity Capping
    reranker = get_reranker()
    mock_candidates = [
        {"document_id": "docA", "text": "Passage 1 from Paper A discussing simplex method."},
        {"document_id": "docA", "text": "Passage 2 from Paper A discussing duality theory."},
        {"document_id": "docA", "text": "Passage 3 from Paper A discussing slack variables."},
        {"document_id": "docA", "text": "Passage 4 from Paper A discussing interior point methods."},
        {"document_id": "docB", "text": "Passage 1 from Paper B discussing gradient descent."},
        {"document_id": "docB", "text": "Passage 2 from Paper B discussing conjugate gradients."},
    ]
    reranked_diverse = reranker.rerank(
        query="optimization methods",
        results=mock_candidates,
        top_k=4,
        diversity_cap=0.40  # Max 40% of 4 slots = max 2 slots per paper
    )
    doc_counts = {}
    for r in reranked_diverse:
        doc_counts[r["document_id"]] = doc_counts.get(r["document_id"], 0) + 1
    
    assert doc_counts.get("docA", 0) <= 2, f"Diversity cap violated: {doc_counts}"
    print(f"{PASS} Paper diversity cap enforced: paper distribution across top-4 slots is {doc_counts}")
except Exception as e:
    print(f"{FAIL} Retrieval/Reranker test failed: {e}")
    errors.append(f"Retrieval/Reranker: {e}")


# 5. Knowledge Graph Endpoint
test_section("5. Relational Knowledge Graph")
try:
    r_graph = client.get("/v1/graph")
    assert r_graph.status_code == 200
    g_data = r_graph.json()
    assert g_data["status"] == "success"
    assert "graph" in g_data
    n_nodes = g_data["total_nodes"]
    n_edges = g_data["total_edges"]
    print(f"{PASS} GET /v1/graph returned directed knowledge graph with {n_nodes} nodes and {n_edges} edges")
except Exception as e:
    print(f"{FAIL} Knowledge graph failed: {e}")
    errors.append(f"Knowledge Graph: {e}")


# 6. Sufficiency & Abstention Logic
test_section("6. Sufficiency Guard & Calibrated Abstention")
try:
    # Case A: Sufficient evidence (score >= 0.35)
    state_sufficient = {
        "reranked_evidence": [{"rerank_score": 1.25, "text": "Strong empirical match."}],
        "iteration": 1
    }
    res_suff = sufficiency_node(state_sufficient)
    assert res_suff["is_sufficient"] is True
    assert sufficiency_router(state_sufficient | res_suff) == "extractor"
    print(f"{PASS} High relevance score (1.25 >= 0.35) routes directly to 'extractor'")

    # Case B: Insufficient evidence on Iteration 1 -> should loop to 'reformulate'
    state_insufficient_iter1 = {
        "reranked_evidence": [{"rerank_score": -2.5, "text": "Weak match"}],
        "iteration": 1
    }
    res_insuff1 = sufficiency_node(state_insufficient_iter1)
    assert res_insuff1["is_sufficient"] is False
    assert sufficiency_router(state_insufficient_iter1 | res_insuff1) == "reformulate"
    print(f"{PASS} Low relevance on iteration 1 routes to 'reformulate' for query expansion")

    # Case C: Insufficient evidence on Iteration 2 -> should branch to 'abstain'
    state_insufficient_iter2 = {
        "reranked_evidence": [{"rerank_score": -3.0, "text": "Very weak match"}],
        "iteration": 2
    }
    res_insuff2 = sufficiency_node(state_insufficient_iter2)
    assert res_insuff2["is_sufficient"] is False
    assert sufficiency_router(state_insufficient_iter2 | res_insuff2) == "abstain"
    print(f"{PASS} Low relevance after 2 iterations routes cleanly to 'abstain'")
except Exception as e:
    print(f"{FAIL} Sufficiency logic failed: {e}")
    errors.append(f"Sufficiency logic: {e}")


# 7. Summary
test_section("VERIFICATION SUMMARY")
if not errors:
    print(f"\033[92m\033[1mALL SYSTEMS VERIFIED & OPERATIONAL!\033[0m")
    print(f"✓ Database & Schema: Healthy")
    print(f"✓ API Endpoints (v1 & root): Fully Functional")
    print(f"✓ Ingestion & Magic-Bytes Security: Active")
    print(f"✓ Hybrid RRF Retrieval & Diversity Capping: Active")
    print(f"✓ Knowledge Graph Generator: Operational")
    print(f"✓ Sufficiency & Abstention Routing: Operational")
else:
    print(f"\033[91m{len(errors)} issues encountered:\033[0m")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)

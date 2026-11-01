"""
Knowledge Graph route: produces paper-method-dataset-finding relational graphs.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
import networkx as nx

from app.db.database import get_document, get_document_chunks
from app.agents.nodes.extractor import extractor_node
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Graph"])


@router.get("/v1/graph")
@router.get("/graph")
def get_paper_graph(
    document_ids: Optional[List[str]] = Query(default=None)
):
    """
    Construct a knowledge graph of papers, methodologies, datasets, and findings.
    Returns nodes and edges ready for interactive visualization.
    """
    g = nx.DiGraph()

    target_docs = document_ids or []
    if not target_docs:
        from app.db.database import get_all_documents
        target_docs = [d["document_id"] for d in get_all_documents()][:5]

    for doc_id in target_docs:
        doc = get_document(doc_id)
        if not doc:
            continue

        paper_title = doc["filename"]
        paper_node_id = f"paper_{doc_id[:8]}"
        g.add_node(
            paper_node_id,
            label=paper_title,
            type="paper",
            size=25,
            color="#4f46e5"
        )

        # Retrieve a few representative chunks to extract entities
        chunks = get_document_chunks(doc_id)
        sample_text = " ".join([c["text"] for c in chunks[:3]])

        # Heuristic entity connection
        sections_found = {c.get("section") for c in chunks if c.get("section")}
        for sec in list(sections_found)[:3]:
            sec_id = f"sec_{doc_id[:8]}_{sec.lower().replace(' ', '_')}"
            g.add_node(sec_id, label=sec, type="section", size=15, color="#10b981")
            g.add_edge(paper_node_id, sec_id, relation="contains")

    # Serialize to nodes & edges format
    nodes = [{"id": n, **g.nodes[n]} for n in g.nodes()]
    edges = [{"source": u, "target": v, **g.edges[u, v]} for u, v in g.edges()]

    return {
        "status": "success",
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "graph": {
            "nodes": nodes,
            "edges": edges
        }
    }


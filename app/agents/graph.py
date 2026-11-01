"""
LangGraph execution graph for ResearchLens AI agentic workflow.
Includes dynamic fallback runner when langgraph is not installed.
"""

from typing import Dict, Any, Optional
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retriever_node
from app.agents.nodes.reranker import reranker_node
from app.agents.nodes.sufficiency import sufficiency_node, sufficiency_router
from app.agents.nodes.extractor import extractor_node
from app.agents.nodes.comparator import comparator_node
from app.agents.nodes.synthesizer import synthesizer_node
from app.agents.nodes.verifier import verifier_node
from app.agents.nodes.reformulate import reformulate_node, abstain_node
from app.core.logging import get_logger

logger = get_logger(__name__)

# Try importing LangGraph
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    END = "__END__"


def create_research_graph():
    """Build and compile the LangGraph agent state machine."""
    if LANGGRAPH_AVAILABLE:
        builder = StateGraph(AgentState)

        # Register nodes
        builder.add_node("planner", planner_node)
        builder.add_node("retriever", retriever_node)
        builder.add_node("reranker", reranker_node)
        builder.add_node("sufficiency", sufficiency_node)
        builder.add_node("reformulate", reformulate_node)
        builder.add_node("abstain", abstain_node)
        builder.add_node("extractor", extractor_node)
        builder.add_node("comparator", comparator_node)
        builder.add_node("synthesizer", synthesizer_node)
        builder.add_node("verifier", verifier_node)

        # Set entry point
        builder.set_entry_point("planner")

        # Edges
        builder.add_edge("planner", "retriever")
        builder.add_edge("retriever", "reranker")
        builder.add_edge("reranker", "sufficiency")

        # Conditional sufficiency routing
        builder.add_conditional_edges(
            "sufficiency",
            sufficiency_router,
            {
                "extractor": "extractor",
                "reformulate": "reformulate",
                "abstain": "abstain"
            }
        )

        builder.add_edge("reformulate", "retriever")
        builder.add_edge("abstain", END)

        builder.add_edge("extractor", "comparator")
        builder.add_edge("comparator", "synthesizer")
        builder.add_edge("synthesizer", "verifier")
        builder.add_edge("verifier", END)

        return builder.compile()
    else:
        return FallbackGraphRunner()


class FallbackGraphRunner:
    """Deterministic state-machine runner replicating the LangGraph workflow."""

    def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        state = dict(initial_state)

        # 1. Planner
        logger.info("[GraphNode] Running planner")
        state.update(planner_node(state))

        while True:
            # 2. Retriever
            logger.info("[GraphNode] Running retriever (iter %d)", state.get("iteration", 1))
            state.update(retriever_node(state))

            # 3. Reranker
            logger.info("[GraphNode] Running reranker")
            state.update(reranker_node(state))

            # 4. Sufficiency
            logger.info("[GraphNode] Running sufficiency")
            state.update(sufficiency_node(state))

            # Check next step
            next_step = sufficiency_router(state)
            if next_step == "reformulate":
                logger.info("[GraphNode] Evidence insufficient; executing reformulate loop")
                state.update(reformulate_node(state))
                continue
            elif next_step == "abstain":
                logger.info("[GraphNode] Reached max iterations; abstaining")
                state.update(abstain_node(state))
                return state
            else:
                # Proceed to synthesis
                break

        # 5. Extractor
        logger.info("[GraphNode] Running extractor")
        state.update(extractor_node(state))

        # 6. Comparator
        logger.info("[GraphNode] Running comparator")
        state.update(comparator_node(state))

        # 7. Synthesizer
        logger.info("[GraphNode] Running synthesizer")
        state.update(synthesizer_node(state))

        # 8. Verifier
        logger.info("[GraphNode] Running verifier")
        state.update(verifier_node(state))

        return state


# Compiled singleton graph
research_graph = create_research_graph()


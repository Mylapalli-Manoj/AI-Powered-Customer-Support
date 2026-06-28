"""
graph.py
--------
Builds the LangGraph workflow that wires together every step of the
Customer Support Automation System:

  Intent Classification -> RAG Retrieval -> Memory Lookup
      -> Route to Department Agent -> Human Approval (if needed)
      -> Supervisor Review -> Final Response

Task 1: Design a LangGraph workflow for the Customer Support Automation System.
Task 4: Implement conditional routing to direct queries to the appropriate support agent.
"""

from langgraph.graph import StateGraph, END

from state import SupportState
import memory
import rag
import agents


# ---------- Node functions ----------
# Each node takes the current state, does its job, and returns the
# fields it wants to update in the state.

def classify_node(state: SupportState) -> dict:
    intent = agents.classify_intent(state["query"])
    print(f"[Intent Classifier] -> {intent}")
    return {"intent": intent}


def retrieve_node(state: SupportState) -> dict:
    context = rag.retrieve_context(state["query"])
    print(f"[RAG Retrieval] -> Retrieved {len(context)} characters of context")
    return {"retrieved_context": context}


def memory_node(state: SupportState) -> dict:
    history = memory.get_history(state["customer_name"])
    print(f"[Memory Lookup] -> {'Found history' if history else 'No prior history'}")
    return {"memory_context": history}


def department_node(state: SupportState) -> dict:
    """Routes to the correct department agent based on intent."""
    intent = state["intent"]
    query = state["query"]
    context = state.get("retrieved_context", "")
    memory_ctx = state.get("memory_context", "")

    if intent == "Sales":
        draft = agents.sales_agent(query, context, memory_ctx)
    elif intent == "Technical Support":
        draft = agents.technical_support_agent(query, context, memory_ctx)
    elif intent == "Billing":
        draft = agents.billing_agent(query, context, memory_ctx)
    else:
        draft = agents.account_agent(query, context, memory_ctx)

    needs_approval = agents.needs_human_approval(query)
    print(f"[{intent} Agent] -> Draft created. Needs approval: {needs_approval}")

    return {"draft_response": draft, "needs_approval": needs_approval}


def human_approval_node(state: SupportState) -> dict:
    """
    Simulates pausing for a human supervisor's approval.
    In this demo, it asks YOU (running the program) to approve or reject.
    """
    print("\n" + "=" * 60)
    print("HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Customer query: {state['query']}")
    print(f"Draft response: {state['draft_response']}")
    decision = input("Approve this response? (yes/no): ").strip().lower()

    status = "approved" if decision == "yes" else "rejected"
    print(f"[Human Supervisor] -> {status}")
    return {"approval_status": status}


def supervisor_node(state: SupportState) -> dict:
    """Final AI quality check before sending the response to the customer."""
    if state.get("approval_status") == "rejected":
        final = "We're sorry, but this request requires further review by our team. A representative will contact you shortly."
    else:
        final = agents.supervisor_review(state["query"], state["draft_response"])

    print(f"[Supervisor Review] -> Final response ready")
    return {"final_response": final}


def save_memory_node(state: SupportState) -> dict:
    """Saves this interaction into SQLite memory for future recall."""
    memory.save_interaction(
        customer_name=state["customer_name"],
        query=state["query"],
        intent=state["intent"],
        response=state["final_response"],
    )
    print(f"[Memory] -> Interaction saved for {state['customer_name']}")
    return {}


# ---------- Conditional routing function ----------

def route_after_department(state: SupportState) -> str:
    """Decides whether to go to human approval or straight to supervisor."""
    if state.get("needs_approval"):
        return "human_approval"
    return "supervisor"


# ---------- Build the graph ----------

def build_graph():
    graph = StateGraph(SupportState)

    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("memory_lookup", memory_node)
    graph.add_node("department", department_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("save_memory", save_memory_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "memory_lookup")
    graph.add_edge("memory_lookup", "department")

    graph.add_conditional_edges(
        "department",
        route_after_department,
        {
            "human_approval": "human_approval",
            "supervisor": "supervisor",
        }
    )

    graph.add_edge("human_approval", "supervisor")
    graph.add_edge("supervisor", "save_memory")
    graph.add_edge("save_memory", END)

    return graph.compile()
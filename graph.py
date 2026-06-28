from langgraph.graph import StateGraph, END

from state import SupportState
import memory
import rag
import agents


# -----------------------------
# NODE 0: MEMORY CHECK (NEW FIX)
# -----------------------------
def memory_check_node(state: SupportState) -> dict:
    """
    Detects memory-only queries BEFORE routing.
    """
    if agents.is_memory_query(state["query"]):
        history = memory.get_history(state["customer_name"])
        print("[Memory Direct Access] -> Handling without routing")

        return {
            "memory_context": history,
            "intent": "Memory"
        }

    return {"intent": None}


# -----------------------------
# CLASSIFIER NODE
# -----------------------------
def classify_node(state: SupportState) -> dict:
    intent = agents.classify_intent(state["query"])
    print(f"[Intent Classifier] -> {intent}")
    return {"intent": intent}


def retrieve_node(state: SupportState) -> dict:
    if state.get("intent") == "Memory":
        return {"retrieved_context": ""}

    context = rag.retrieve_context(state["query"])
    print(f"[RAG Retrieval] -> Retrieved {len(context)} characters of context")
    return {"retrieved_context": context}


def memory_node(state: SupportState) -> dict:
    if state["intent"] == "Memory":
        return {}

    history = memory.get_history(state["customer_name"])
    print(f"[Memory Lookup] -> {'Found history' if history else 'No prior history'}")
    return {"memory_context": history}


def department_node(state: SupportState) -> dict:
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

    elif intent == "Account":
        draft = agents.account_agent(query, context, memory_ctx)

    elif intent == "Memory":
        draft = memory_ctx or "No previous support history found."

    else:
        draft = "Unable to classify request."

    needs_approval = agents.needs_human_approval(query)

    print(f"[{intent} Agent] -> Draft created. Needs approval: {needs_approval}")

    return {
        "draft_response": draft,
        "needs_approval": needs_approval
    }


def human_approval_node(state: SupportState) -> dict:
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
    if state.get("approval_status") == "rejected":
        final = "Your request requires further review by our team. A representative will contact you shortly."
    else:
        final = agents.supervisor_review(state["query"], state["draft_response"])

    print("[Supervisor Review] -> Final response ready")
    return {"final_response": final}


def save_memory_node(state: SupportState) -> dict:
    memory.save_interaction(
        customer_name=state["customer_name"],
        query=state["query"],
        intent=state["intent"],
        response=state["final_response"],
    )

    print(f"[Memory] -> Interaction saved for {state['customer_name']}")
    return {}


# -----------------------------
# ROUTING FIX
# -----------------------------
def route_after_department(state: SupportState) -> str:
    if state.get("needs_approval"):
        return "human_approval"
    return "supervisor"


# -----------------------------
# BUILD GRAPH (FIXED FLOW)
# -----------------------------
def build_graph():
    graph = StateGraph(SupportState)

    graph.add_node("memory_check", memory_check_node)
    graph.add_node("classify", classify_node)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("memory_lookup", memory_node)
    graph.add_node("department", department_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("save_memory", save_memory_node)

    graph.set_entry_point("memory_check")


    # STEP 1: memory shortcut OR classification
    graph.add_conditional_edges(
        "memory_check",
        lambda state: "memory" if state.get("intent") == "Memory" else "classify",
        {
            "memory": "memory_lookup_only",
            "classify": "classify",
        }
    )


    # STEP 2: NORMAL PATH (RAG INCLUDED)
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "memory_lookup")
    graph.add_edge("memory_lookup", "department")


    # STEP 3: MEMORY ONLY PATH (NO RAG)
    graph.add_node("memory_lookup_only", memory_node)

    graph.add_edge("memory_lookup_only", "department")


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
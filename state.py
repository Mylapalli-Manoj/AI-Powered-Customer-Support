"""
state.py
---------
Defines the shared State structure that flows through every node
in our LangGraph Customer Support Automation workflow.

Every node reads from this State and writes its results back into it,
so the next node can use that information.
"""

from typing import TypedDict, Optional


class SupportState(TypedDict):
    # The customer's name, used to look up their conversation history
    customer_name: str

    # The original message/question the customer typed
    query: str

    # The department this query was classified into:
    # "Sales", "Technical Support", "Billing", or "Account"
    intent: Optional[str]

    # Relevant text retrieved from company documents (RAG step)
    retrieved_context: Optional[str]

    # Past conversation history pulled from SQLite memory
    memory_context: Optional[str]

    # The draft response written by the department agent
    draft_response: Optional[str]

    # Whether this request needs human approval (True/False)
    needs_approval: bool

    # Human supervisor's decision: "approved" or "rejected" or None if not needed
    approval_status: Optional[str]

    # The final response shown to the customer, after supervisor review
    final_response: Optional[str]
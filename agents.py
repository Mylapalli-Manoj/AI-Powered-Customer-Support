"""
agents.py
---------
Defines all the AI agents used in our Customer Support Automation
system:
  - Intent Classifier (Task 3)
  - Sales Agent, Technical Support Agent, Billing Agent, Account Agent (Task 5)
  - Supervisor Agent (Task 9)

All agents use Groq's free LLM API through LangChain.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Groq provides an OpenAI-compatible API, so we just point ChatOpenAI
# at Groq's endpoint instead of OpenAI's.
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.3,
)


# ---------- Task 3: Intent Classification ----------

def classify_intent(query: str) -> str:
    """
    Reads the customer's query and classifies it into one of:
    Sales, Technical Support, Billing, or Account.
    """
    prompt = f"""You are an intent classifier for a customer support system.
Classify the following customer query into EXACTLY ONE of these categories:
Sales, Technical Support, Billing, Account

Rules:
- Sales: product info, subscription plans, pricing
- Technical Support: app errors, installation, login problems, configuration
- Billing: invoices, payments, refunds
- Account: password reset, profile updates, account activation/deactivation

Customer query: "{query}"

Respond with ONLY the category name, nothing else."""

    response = llm.invoke(prompt)
    intent = response.content.strip()

    # Basic safety net in case the model adds extra words
    for category in ["Sales", "Technical Support", "Billing", "Account"]:
        if category.lower() in intent.lower():
            return category

    return "Technical Support"  # fallback default


# ---------- Task 5: Department Agents ----------

def _run_department_agent(department: str, query: str, retrieved_context: str, memory_context: str) -> str:
    """Shared helper that powers each department-specific agent."""
    prompt = f"""You are a {department} support agent at ABC Technologies.

Relevant company information:
{retrieved_context}

Customer's past conversation history:
{memory_context if memory_context else "No prior history."}

Customer query: "{query}"

Write a helpful, professional, concise response to the customer (3-5 sentences)."""

    response = llm.invoke(prompt)
    return response.content.strip()


def sales_agent(query: str, retrieved_context: str, memory_context: str) -> str:
    return _run_department_agent("Sales", query, retrieved_context, memory_context)


def technical_support_agent(query: str, retrieved_context: str, memory_context: str) -> str:
    return _run_department_agent("Technical Support", query, retrieved_context, memory_context)


def billing_agent(query: str, retrieved_context: str, memory_context: str) -> str:
    return _run_department_agent("Billing", query, retrieved_context, memory_context)


def account_agent(query: str, retrieved_context: str, memory_context: str) -> str:
    return _run_department_agent("Account", query, retrieved_context, memory_context)


# ---------- Task 8: Human-in-the-loop check ----------

RISKY_KEYWORDS = [
    "refund", "cancel", "cancellation", "close my account",
    "account closure", "compensation", "escalate", "escalation", "manager"
]


def needs_human_approval(query: str) -> bool:
    """
    Checks whether a query touches a sensitive area that must be
    reviewed by a human supervisor before responding.
    """
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in RISKY_KEYWORDS)


# ---------- Task 9: Supervisor Agent ----------

def supervisor_review(query: str, draft_response: str) -> str:
    """
    Reviews and improves a draft response before it is sent to the customer.
    """
    prompt = f"""You are a quality-control supervisor at a customer support center.
Review the draft response below for tone, clarity, and professionalism.
Improve it if needed, but keep it concise (3-5 sentences). Return ONLY the
final response text, with no preamble or explanation.

Customer query: "{query}"

Draft response: "{draft_response}"
"""

    response = llm.invoke(prompt)
    return response.content.strip()
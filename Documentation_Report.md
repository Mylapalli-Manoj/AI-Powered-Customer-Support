# Documentation Report
## AI-Powered Customer Support Automation System

**Course:** IBM Agentic AI — VIT May 2026 Batch
**Author:** GraceCoder25

---

## 1. Project Overview

ABC Technologies receives a high volume of daily customer support requests covering product information, technical issues, billing queries, account management, and refund requests. All requests were previously handled manually by support executives, leading to longer response times and higher operational costs.

This project implements an **AI-Powered Customer Support Automation System** using **LangGraph** to automate the end-to-end handling of customer queries — from intent classification through to final response generation — while preserving human oversight for sensitive requests.

## 2. System Architecture

The system is implemented as a LangGraph workflow consisting of the following nodes:

1. **Intent Classification** — reads the customer's query and classifies it into one of four categories: Sales, Technical Support, Billing, or Account.
2. **RAG Retrieval** — searches a knowledge base of company documents (policy, pricing, technical manual, FAQ) for context relevant to the query.
3. **Memory Lookup** — retrieves the customer's past conversation history from a SQLite database.
4. **Department Agent (conditional routing)** — the query is routed to one of four specialized agents (Sales, Technical Support, Billing, Account) based on the classified intent. Each agent generates a draft response using the retrieved context and memory.
5. **Human-in-the-Loop Approval** — if the query involves a refund, cancellation, account closure, compensation request, or escalation, the workflow pauses and requires a human supervisor to approve or reject the draft response before continuing.
6. **Supervisor Review** — a final AI-driven quality check reviews and refines the response for tone, clarity, and professionalism before it is sent to the customer.
7. **Memory Storage** — the final interaction (query, intent, and response) is saved to SQLite for future recall.

## 3. State Design

A shared `SupportState` (TypedDict) flows through every node in the graph. It holds:
- `customer_name`, `query` — the incoming request
- `intent` — the classified department
- `retrieved_context` — RAG search results
- `memory_context` — past conversation history
- `draft_response` — the department agent's initial response
- `needs_approval`, `approval_status` — human-in-the-loop tracking
- `final_response` — the response ultimately sent to the customer

This design allows every node to read only the state fields it needs and write back only the fields it produces, keeping the graph modular and easy to extend.

## 4. RAG Implementation

Company documents (`company_policy.txt`, `pricing_guide.txt`, `technical_manual.txt`, `faq.txt`) are loaded, split into overlapping chunks using `RecursiveCharacterTextSplitter`, and embedded using the `sentence-transformers/all-MiniLM-L6-v2` model. A FAISS vector store enables fast similarity search, returning the most relevant chunks for each customer query.

## 5. Memory Implementation

Conversation history is stored in a local SQLite database (`memory.db`), with one row per interaction containing the customer's name, query, classified intent, response, and timestamp. When a new query arrives, the system retrieves the customer's most recent interactions and passes them as context to the department agent, enabling continuity across conversations (e.g., answering "What was my previous support issue?").

## 6. Human-in-the-Loop Design

A simple keyword-based check (`needs_human_approval`) flags queries containing terms such as "refund," "cancel," "compensation," or "escalate." When flagged, the workflow pauses execution and prompts a human supervisor (via terminal input in this demo) to approve or reject the draft response. Rejected responses are replaced with a standard message indicating the request requires further review.

## 7. Testing & Demonstration

The system was tested against the five sample queries provided in the assignment:

| Query | Expected Path | Result |
|-------|---------------|--------|
| "What are the pricing plans available for your software?" | Sales | Correctly routed to Sales agent |
| "I forgot my account password." | Account | Correctly routed to Account agent |
| "My application crashes whenever I upload a file." | Technical Support | Correctly routed to Technical Support agent |
| "I need a refund for my annual subscription." | Billing — requires approval | Correctly routed to Billing agent; human approval correctly triggered |
| "What was my previous support issue?" | Memory recall | Correctly recalled prior refund conversation from memory |

All five queries produced correct routing, retrieval, and (where applicable) human-in-the-loop behavior, confirming the system meets the functional requirements described in the assignment.

## 8. Technology Stack

- **LangGraph** — workflow orchestration and conditional routing
- **LangChain** — LLM integration layer
- **Groq (Llama 3.3 70B)** — free LLM inference for classification and response generation
- **FAISS + Sentence Transformers** — RAG retrieval pipeline
- **SQLite** — persistent conversation memory

## 9. Conclusion

This project demonstrates a complete agentic AI workflow that automates customer support triage while retaining a human checkpoint for high-risk actions. The modular LangGraph design — separating intent classification, retrieval, memory, department-specific response generation, and supervisory review into distinct nodes — makes the system easy to extend with additional departments, knowledge sources, or approval rules in the future.
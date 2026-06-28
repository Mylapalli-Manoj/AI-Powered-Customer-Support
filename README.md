
# AI-Powered Customer Support Automation System

An agentic AI system built with **LangGraph** that automatically classifies customer support queries, routes them to the appropriate department agent, retrieves relevant information from company documents (RAG), remembers past customer conversations (SQLite memory), and pauses for human approval on sensitive requests before sending a final response.

Built for the IBM Agentic AI course assignment.

## Features

- **Intent Classification** — automatically detects whether a query is Sales, Technical Support, Billing, or Account related
- **Conditional Routing** — directs each query to a specialized department agent
- **RAG (Retrieval-Augmented Generation)** — searches company documents (policy, pricing, technical manual, FAQ) for relevant context
- **SQLite Memory** — stores and recalls each customer's conversation history
- **Human-in-the-Loop Approval** — pauses for supervisor approval on high-risk requests (refunds, cancellations, account closures, escalations)
- **Supervisor Review Agent** — performs a final quality check before sending the response to the customer

## Tech Stack

- Python 3.x
- [LangGraph](https://github.com/langchain-ai/langgraph) — workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — LLM integration
- [Groq](https://console.groq.com) (Llama 3.3 70B) — free LLM inference
- [FAISS](https://github.com/facebookresearch/faiss) — vector search for RAG
- [Sentence Transformers](https://www.sbert.net/) — text embeddings
- SQLite — conversation memory storage

## Project Structure
ai-customer-support-automation/

├── knowledge_base/          # Company documents used for RAG

│   ├── company_policy.txt

│   ├── pricing_guide.txt

│   ├── technical_manual.txt

│   └── faq.txt

├── state.py                 # Shared LangGraph state definition

├── memory.py                 # SQLite conversation memory

├── rag.py                    # RAG retrieval pipeline

├── agents.py                 # Intent classifier, department agents, supervisor agent

├── graph.py                  # LangGraph workflow definition

├── main.py                   # Entry point — runs 5 demo queries

├── requirements.txt

└── README.md
## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/GraceCoder25/ai-customer-support-automation.git
cd ai-customer-support-automation
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Create a `.env` file in the project root and add:
GROQ_API_KEY=your_groq_api_key_here
A free API key can be obtained from console.groq.com.

## Running the Project

```bash
python main.py
```

The script will run through 5 sample customer queries automatically. When a query involves a refund, cancellation, or other sensitive request, the program will pause and ask for approval in the terminal:
Approve this response? (yes/no):
Type `yes` or `no` and press Enter to continue.

## Sample Queries Demonstrated

| # | Query | Expected Path |
|---|-------|----------------|
| 1 | "What are the pricing plans available for your software?" | Sales |
| 2 | "I forgot my account password." | Account |
| 3 | "My application crashes whenever I upload a file." | Technical Support |
| 4 | "I need a refund for my annual subscription." | Billing — requires human approval |
| 5 | "What was my previous support issue?" | Memory recall — no department routing needed |

## Author

Built by GraceCoder25 as part of the IBM VIT Agentic AI course (May 2026 batch).



"""
main.py
-------
Entry point for the AI-Powered Customer Support Automation System.

Runs the LangGraph workflow against the 5 sample demonstration
queries from the assignment.

Task 10: Demonstrate the system using the five sample customer queries.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

from memory import init_db
from graph import build_graph

console = Console()

# The 5 sample queries from the assignment
DEMO_QUERIES = [
    {
        "customer_name": "Manoj",
        "query": "What are the pricing plans available for your software?"
    },
    {
        "customer_name": "Ravi",
        "query": "I forgot my account password."
    },
    {
        "customer_name": "Arun",
        "query": "My application crashes whenever I upload a file."
    },
    {
        "customer_name": "Mahesh",
        "query": "I need a refund for my annual subscription."
    },
    {
        "customer_name": "Mahesh",
        "query": "What was my previous support issue?"
    },
]


def run_demo():

    console.rule("[bold blue]ABC Technologies - AI Customer Support [/bold blue]")

    console.print("[bold green]Initializing SQLite Database...[/bold green]")

    init_db()

    app = build_graph()

    for i, item in enumerate(DEMO_QUERIES, start=1):

        console.print()
        console.rule(f"[bold yellow]DEMO QUERY {i}[/bold yellow]")

        query_table = Table(show_header=False, box=None)

        query_table.add_row(
            "[cyan]Customer[/cyan]",
            item["customer_name"]
        )

        query_table.add_row(
            "[cyan]Customer Query[/cyan]",
            item["query"]
        )

        console.print(query_table)

        initial_state = {

            "customer_name": item["customer_name"],

            "query": item["query"],

            "intent": None,

            "retrieved_context": None,

            "memory_context": None,

            "draft_response": None,

            "needs_approval": False,

            "approval_status": None,

            "final_response": None,

        }

        result = app.invoke(initial_state)

        workflow = Table(show_header=False, box=None)

        workflow.add_row(
            "[green]Intent[/green]",
            str(result["intent"])
        )

        workflow.add_row(
            "[green]Human Approval[/green]",
            "Required" if result["needs_approval"] else "Not Required"
        )

        workflow.add_row(
            "[green]Approval Status[/green]",
            str(result["approval_status"])
        )

        memory_status = (
            "Retrieved"
            if result.get("memory_context")
            else "Not Used"
        )

        rag_status = (
            "Retrieved"
            if result.get("retrieved_context")
            else "Not Used"
        )

        workflow.add_row(
            "[green]Memory[/green]",
            memory_status
        )

        workflow.add_row(
            "[green]RAG[/green]",
            rag_status
        )

        console.print(
            Panel(
                workflow,
                title="[bold cyan]Workflow Summary[/bold cyan]",
                border_style="cyan"
            )
        )

        console.print(
            Panel(
                result["final_response"],
                title="[bold green]Final Response To Customer[/bold green]",
                border_style="green"
            )
        )

    console.rule("[bold green]All Demonstration Queries Completed Successfully[/bold green]")


if __name__ == "__main__":
    run_demo()
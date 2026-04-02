"""
FixdAI CLI Query
================
Ask bike repair questions from the command line.

Usage:
    python src/query.py "How do I bleed Shimano hydraulic brakes?"
    python src/query.py  # Interactive mode
"""

import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from chain import build_chain, query_with_sources

console = Console()


def display_result(question: str, result: dict):
    """Pretty-print the answer and sources."""
    console.print()

    # Answer
    console.print(Panel(
        Markdown(result["answer"]),
        title=f"[bold]🔧 {question}[/bold]",
        border_style="blue",
        padding=(1, 2),
    ))

    # Sources
    if result["sources"]:
        console.print("\n[bold]📄 Sources:[/bold]")
        for i, src in enumerate(result["sources"], 1):
            console.print(f"  [{i}] [dim]{src['doc_name']}[/dim] ({src['page']})")
            preview = src["content"][:150].replace("\n", " ")
            console.print(f"      [dim italic]{preview}...[/dim italic]")
    console.print()


def interactive_mode(chain):
    """Run an interactive question loop."""
    console.print("\n[bold]🔧 FixdAI — Bike Repair Assistant[/bold]")
    console.print("[dim]Type your question and press Enter. Type 'quit' to exit.[/dim]\n")

    while True:
        try:
            question = console.input("[bold blue]> [/bold blue]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            break

        if not question or question.lower() in ("quit", "exit", "q"):
            console.print("[dim]Bye![/dim]")
            break

        with console.status("[bold blue]Thinking...[/bold blue]"):
            result = query_with_sources(question, chain)

        display_result(question, result)


def main():
    console.print("[dim]Loading FixdAI chain...[/dim]")
    chain = build_chain()
    console.print("[green]✓[/green] Ready\n")

    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])
        with console.status("[bold blue]Thinking...[/bold blue]"):
            result = query_with_sources(question, chain)
        display_result(question, result)
    else:
        # Interactive mode
        interactive_mode(chain)


if __name__ == "__main__":
    main()

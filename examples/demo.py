#!/usr/bin/env python3
"""
ClearCraft Demo Script

Demonstrates the key features of ClearCraft text enhancement.
Run this script to see ClearCraft in action!
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector
from clearcraft.similarity import SimilarityChecker

console = Console()


def print_header(title: str):
    """Print a formatted header."""
    console.print(f"\n{'=' * 80}")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"{'=' * 80}\n")


def demo_analysis():
    """Demonstrate text analysis features."""
    print_header("1. TEXT ANALYSIS DEMO")

    # Sample text with readability issues
    text = """
    The implementation of sophisticated algorithmic methodologies necessitates
    comprehensive understanding of computational complexity. Consequently, the
    optimization paradigm was utilized by researchers to facilitate enhancement
    of processing efficiency. The methodology was designed by the team to
    leverage cutting-edge frameworks.
    """

    console.print("[bold]Original Text:[/bold]")
    console.print(Panel(text.strip(), border_style="yellow"))

    # Analyze
    console.print("\n[bold]Analyzing readability metrics...[/bold]")
    analyzer = TextAnalyzer()
    result = analyzer.analyze(text)
    metrics = result.metrics

    # Display metrics
    table = Table(title="Readability Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Interpretation", style="yellow")

    table.add_row(
        "Flesch Reading Ease",
        f"{metrics.flesch_reading_ease:.1f}",
        "Very Difficult" if metrics.flesch_reading_ease < 30 else "Difficult"
    )
    table.add_row(
        "Flesch-Kincaid Grade",
        f"{metrics.flesch_kincaid_grade:.1f}",
        f"Grade {int(metrics.flesch_kincaid_grade)} level"
    )
    table.add_row(
        "Avg Sentence Length",
        f"{metrics.avg_sentence_length:.1f} words",
        "Too long" if metrics.avg_sentence_length > 22 else "Good"
    )
    table.add_row(
        "Passive Voice Ratio",
        f"{metrics.passive_ratio:.1%}",
        "High" if metrics.passive_ratio > 0.15 else "Good"
    )
    table.add_row(
        "Type-Token Ratio",
        f"{metrics.ttr:.3f}",
        "Good variety" if metrics.ttr >= 0.5 else "Low variety"
    )

    console.print(table)

    # Show passive sentences
    if result.passive_sentences:
        console.print(f"\n[bold red]Found {len(result.passive_sentences)} passive voice sentences:[/bold red]")
        for idx in result.passive_sentences:
            console.print(f"  • {result.sentences[idx]}")


def demo_rewriting():
    """Demonstrate text rewriting with improvements."""
    print_header("2. TEXT REWRITING DEMO")

    text = """
    The report was written by the research team. The methodology was utilized
    to facilitate analysis of the data. Subsequently, the findings were
    presented by the investigators to demonstrate the efficacy of the approach.
    """

    console.print("[bold]Original Text:[/bold]")
    console.print(Panel(text.strip(), border_style="yellow"))

    # Rewrite
    console.print("\n[bold]Rewriting for clarity...[/bold]")
    selector = TextSelector(
        target_avg_sentence_length=(14, 22),
        enable_llm=False,  # Deterministic mode only
    )
    result = selector.rewrite(text, tone="neutral", enable_disclosure=False)

    console.print("\n[bold green]Improved Text:[/bold green]")
    console.print(Panel(result.rewritten_text.strip(), border_style="green"))

    # Show improvements
    console.print("\n[bold]Improvements:[/bold]")
    improvement_table = Table(show_header=True)
    improvement_table.add_column("Metric", style="cyan")
    improvement_table.add_column("Before", style="yellow")
    improvement_table.add_column("After", style="green")
    improvement_table.add_column("Change", style="magenta")

    def format_change(before: float, after: float) -> str:
        delta = after - before
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "="
        return f"{arrow} {abs(delta):.1f}"

    improvement_table.add_row(
        "Flesch Score",
        f"{result.original_metrics.flesch_reading_ease:.1f}",
        f"{result.rewritten_metrics.flesch_reading_ease:.1f}",
        format_change(
            result.original_metrics.flesch_reading_ease,
            result.rewritten_metrics.flesch_reading_ease
        )
    )
    improvement_table.add_row(
        "Passive Voice",
        f"{result.original_metrics.passive_ratio:.1%}",
        f"{result.rewritten_metrics.passive_ratio:.1%}",
        format_change(
            result.original_metrics.passive_ratio * 100,
            result.rewritten_metrics.passive_ratio * 100
        )
    )
    improvement_table.add_row(
        "Avg Sentence",
        f"{result.original_metrics.avg_sentence_length:.1f}",
        f"{result.rewritten_metrics.avg_sentence_length:.1f}",
        format_change(
            result.original_metrics.avg_sentence_length,
            result.rewritten_metrics.avg_sentence_length
        )
    )

    console.print(improvement_table)

    # Show change operations
    console.print(f"\n[bold]Applied {len(result.change_operations)} transformations:[/bold]")
    for i, op in enumerate(result.change_operations, 1):
        console.print(
            f"  {i}. [cyan]{op.pass_name}[/cyan]: {op.reason} "
            f"(confidence: {op.confidence:.0%})"
        )

    # Show quality metrics
    console.print(f"\n[bold]Quality Guardrails:[/bold]")
    console.print(f"  • Semantic Similarity: [green]{result.overall_similarity:.1%}[/green] (≥92% required)")
    console.print(f"  • Change Ratio: [green]{result.total_change_ratio:.1%}[/green] (≤30% allowed)")


def demo_similarity():
    """Demonstrate semantic similarity checking."""
    print_header("3. SEMANTIC SIMILARITY DEMO")

    checker = SimilarityChecker()

    # Test cases
    test_cases = [
        (
            "The quick brown fox jumps over the lazy dog.",
            "A fast brown fox leaps over a lazy dog.",
            "High similarity (paraphrase)"
        ),
        (
            "Machine learning improves predictive accuracy.",
            "Artificial intelligence enhances forecast precision.",
            "Moderate similarity (related concepts)"
        ),
        (
            "The weather is sunny today.",
            "Quantum computing uses qubits for computation.",
            "Low similarity (unrelated topics)"
        ),
    ]

    for text1, text2, description in test_cases:
        similarity = checker.compute_similarity(text1, text2)

        console.print(f"\n[bold]{description}[/bold]")
        console.print(f"  Text 1: [yellow]{text1}[/yellow]")
        console.print(f"  Text 2: [yellow]{text2}[/yellow]")

        # Color based on similarity
        color = "green" if similarity >= 0.7 else "yellow" if similarity >= 0.4 else "red"
        console.print(f"  Similarity: [{color}]{similarity:.1%}[/{color}]")


def demo_jargon_simplification():
    """Demonstrate jargon to plain language conversion."""
    print_header("4. JARGON SIMPLIFICATION DEMO")

    from clearcraft.rewriters.jargon_plain import JargonSimplifier

    text = """
    Utilize this methodology to facilitate optimization of the paradigm.
    Subsequently, leverage the framework to implement cutting-edge solutions.
    """

    console.print("[bold]Text with Jargon:[/bold]")
    console.print(Panel(text.strip(), border_style="yellow"))

    simplifier = JargonSimplifier()
    simplified, replacements = simplifier.process(text)

    console.print("\n[bold green]Simplified Text:[/bold green]")
    console.print(Panel(simplified.strip(), border_style="green"))

    if replacements:
        console.print(f"\n[bold]Replaced {len(replacements)} jargon terms:[/bold]")
        for repl in replacements:
            console.print(
                f"  • [yellow]{repl.original_word}[/yellow] → "
                f"[green]{repl.replacement}[/green] "
                f"(confidence: {repl.confidence:.0%})"
            )


def demo_citation_preservation():
    """Demonstrate citation and formatting preservation."""
    print_header("5. CITATION PRESERVATION DEMO")

    text = """
    Recent studies (Smith et al., 2020) have shown that [1] text simplification
    improves comprehension. As noted by researchers [2], the methodology utilizes
    advanced algorithms. See also: https://example.com/paper for more details.

    ```python
    def example():
        return "This code should not be modified"
    ```
    """

    console.print("[bold]Text with Citations and Code:[/bold]")
    console.print(Panel(text.strip(), border_style="yellow"))

    selector = TextSelector(enable_llm=False)
    result = selector.rewrite(text, enable_disclosure=False)

    console.print("\n[bold green]After Rewriting:[/bold green]")
    console.print(Panel(result.rewritten_text.strip(), border_style="green"))

    # Verify preservation
    console.print("\n[bold]Verification:[/bold]")
    checks = [
        ("(Smith et al., 2020)" in result.rewritten_text, "Academic citation preserved"),
        ("[1]" in result.rewritten_text, "Reference [1] preserved"),
        ("[2]" in result.rewritten_text, "Reference [2] preserved"),
        ("https://example.com/paper" in result.rewritten_text, "URL preserved"),
        ("```python" in result.rewritten_text, "Code block preserved"),
        ("def example()" in result.rewritten_text, "Code content preserved"),
    ]

    for passed, description in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"  {status} {description}")


def main():
    """Run all demos."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]ClearCraft Demo[/bold cyan]\n"
        "Demonstrating ethical text clarity enhancement",
        border_style="cyan"
    ))

    try:
        demo_analysis()
        input("\nPress Enter to continue to rewriting demo...")

        demo_rewriting()
        input("\nPress Enter to continue to similarity demo...")

        demo_similarity()
        input("\nPress Enter to continue to jargon simplification demo...")

        demo_jargon_simplification()
        input("\nPress Enter to continue to citation preservation demo...")

        demo_citation_preservation()

        print_header("DEMO COMPLETE")
        console.print("[bold green]✓ All demos completed successfully![/bold green]\n")
        console.print("Next steps:")
        console.print("  • Try the web interface: [cyan]clearcraft server[/cyan]")
        console.print("  • Analyze your own text: [cyan]clearcraft analyze --file yourfile.txt[/cyan]")
        console.print("  • Rewrite text: [cyan]clearcraft rewrite --file input.txt --output output.txt[/cyan]")
        console.print("\nFor more information, see README.md and USAGE.md\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

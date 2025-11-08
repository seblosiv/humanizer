"""
Command-line interface for ClearCraft using Typer.

Provides analyze and rewrite commands with rich output.
"""

import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from clearcraft.config import settings
from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector
from clearcraft.exceptions import ClearCraftError, DisallowedIntentError

app = typer.Typer(
    name="clearcraft",
    help="Production-grade text clarity and readability enhancement tool",
    add_completion=False,
)

console = Console()


@app.command()
def analyze(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to analyze"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to analyze"),
):
    """
    Analyze text for readability metrics.

    Provide either --text or --file.
    """
    # Get text
    if text is None and file is None:
        console.print("[red]Error: Must provide either --text or --file[/red]")
        raise typer.Exit(1)

    if text and file:
        console.print("[red]Error: Provide only one of --text or --file[/red]")
        raise typer.Exit(1)

    if file:
        try:
            text = file.read_text()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)

    # Analyze
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Analyzing text...", total=None)

            analyzer = TextAnalyzer()
            result = analyzer.analyze(text)

        # Display results
        metrics = result.metrics

        # Create metrics table
        table = Table(title="Readability Metrics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Interpretation", style="yellow")

        # Flesch Reading Ease
        flesch_interp = (
            "Very Easy" if metrics.flesch_reading_ease >= 80
            else "Easy" if metrics.flesch_reading_ease >= 70
            else "Fairly Easy" if metrics.flesch_reading_ease >= 60
            else "Standard" if metrics.flesch_reading_ease >= 50
            else "Fairly Difficult" if metrics.flesch_reading_ease >= 30
            else "Difficult"
        )
        table.add_row(
            "Flesch Reading Ease",
            f"{metrics.flesch_reading_ease:.1f}",
            flesch_interp,
        )

        # Flesch-Kincaid Grade
        table.add_row(
            "Flesch-Kincaid Grade",
            f"{metrics.flesch_kincaid_grade:.1f}",
            f"Grade {int(metrics.flesch_kincaid_grade)} level",
        )

        # Gunning Fog
        table.add_row(
            "Gunning Fog Index",
            f"{metrics.gunning_fog:.1f}",
            f"{int(metrics.gunning_fog)} years of education",
        )

        # Sentence stats
        table.add_row(
            "Avg Sentence Length",
            f"{metrics.avg_sentence_length:.1f} words",
            "Good" if 14 <= metrics.avg_sentence_length <= 22 else "Could improve",
        )

        # Lexical diversity
        table.add_row(
            "Type-Token Ratio",
            f"{metrics.ttr:.3f}",
            "Good" if metrics.ttr >= 0.5 else "Low variety",
        )

        if metrics.mtld:
            table.add_row(
                "MTLD",
                f"{metrics.mtld:.1f}",
                "Good" if metrics.mtld >= 60 else "Low diversity",
            )

        # Voice and style
        passive_status = "High" if metrics.passive_ratio > 0.15 else "Good"
        table.add_row(
            "Passive Voice Ratio",
            f"{metrics.passive_ratio:.1%}",
            passive_status,
        )

        repetition_status = "High" if metrics.repetition_ratio > 0.10 else "Good"
        table.add_row(
            "Repetition Ratio",
            f"{metrics.repetition_ratio:.1%}",
            repetition_status,
        )

        console.print(table)

        # Summary stats
        console.print(f"\n[bold]Total words:[/bold] {metrics.total_words}")
        console.print(f"[bold]Unique words:[/bold] {metrics.unique_words}")
        console.print(f"[bold]Sentences:[/bold] {metrics.sentence_count}")

    except ClearCraftError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def rewrite(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text to rewrite"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to rewrite"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    tone: str = typer.Option("neutral", "--tone", help="Tone: neutral, academic, conversational"),
    min_length: int = typer.Option(14, "--min-length", help="Min avg sentence length"),
    max_length: int = typer.Option(22, "--max-length", help="Max avg sentence length"),
    enable_llm: bool = typer.Option(False, "--llm", help="Enable LLM pass (requires API key)"),
    no_disclosure: bool = typer.Option(False, "--no-disclosure", help="Disable disclosure message"),
):
    """
    Rewrite text for improved clarity.

    Provide either --text or --file.
    """
    # Get text
    if text is None and file is None:
        console.print("[red]Error: Must provide either --text or --file[/red]")
        raise typer.Exit(1)

    if text and file:
        console.print("[red]Error: Provide only one of --text or --file[/red]")
        raise typer.Exit(1)

    if file:
        try:
            text = file.read_text()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)

    # Rewrite
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Rewriting text...", total=None)

            selector = TextSelector(
                target_avg_sentence_length=(min_length, max_length),
                enable_llm=enable_llm,
            )

            result = selector.rewrite(
                text=text,
                tone=tone,
                enable_disclosure=not no_disclosure,
            )

        # Display results
        console.print("\n[bold green]Rewrite Complete![/bold green]\n")

        # Show metrics comparison
        table = Table(title="Metrics Comparison", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Change", style="magenta")

        def format_change(before: float, after: float) -> str:
            delta = after - before
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "="
            return f"{arrow} {abs(delta):.1f}"

        table.add_row(
            "Flesch Reading Ease",
            f"{result.original_metrics.flesch_reading_ease:.1f}",
            f"{result.rewritten_metrics.flesch_reading_ease:.1f}",
            format_change(
                result.original_metrics.flesch_reading_ease,
                result.rewritten_metrics.flesch_reading_ease,
            ),
        )

        table.add_row(
            "Avg Sentence Length",
            f"{result.original_metrics.avg_sentence_length:.1f}",
            f"{result.rewritten_metrics.avg_sentence_length:.1f}",
            format_change(
                result.original_metrics.avg_sentence_length,
                result.rewritten_metrics.avg_sentence_length,
            ),
        )

        table.add_row(
            "Passive Voice",
            f"{result.original_metrics.passive_ratio:.1%}",
            f"{result.rewritten_metrics.passive_ratio:.1%}",
            format_change(
                result.original_metrics.passive_ratio * 100,
                result.rewritten_metrics.passive_ratio * 100,
            ),
        )

        console.print(table)

        # Show quality metrics
        console.print(f"\n[bold]Semantic Similarity:[/bold] {result.overall_similarity:.1%}")
        console.print(f"[bold]Change Ratio:[/bold] {result.total_change_ratio:.1%}")

        # Show rewritten text
        console.print("\n" + "=" * 80)
        console.print(Panel(result.rewritten_text, title="[bold]Rewritten Text[/bold]", border_style="green"))

        # Save to file if requested
        if output:
            try:
                output.write_text(result.rewritten_text)
                console.print(f"\n[green]Saved to {output}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving file: {e}[/red]")

    except DisallowedIntentError as e:
        console.print(f"[red]Disallowed Intent: {e}[/red]")
        raise typer.Exit(1)
    except ClearCraftError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", "--host", help="Server host"),
    port: int = typer.Option(8000, "--port", help="Server port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
):
    """
    Run the ClearCraft web server.
    """
    import uvicorn

    console.print(f"[green]Starting ClearCraft server on {host}:{port}[/green]")

    uvicorn.run(
        "clearcraft.server:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def version():
    """Show version information."""
    from clearcraft import __version__

    console.print(f"[bold]ClearCraft[/bold] version {__version__}")
    console.print(f"DeepInfra LLM: {'Enabled' if settings.is_deepinfra_enabled else 'Disabled'}")


if __name__ == "__main__":
    app()

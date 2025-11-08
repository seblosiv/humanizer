#!/usr/bin/env python3
"""
ClearCraft Performance Benchmark

Tests performance of text analysis and rewriting operations.
"""

import time
import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector

console = Console()


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""

    operation: str
    text_length: int
    duration_seconds: float
    throughput_chars_per_sec: float
    success: bool
    error: str = ""


def generate_test_text(length: int) -> str:
    """Generate test text of specified length."""
    base_text = (
        "The implementation of sophisticated algorithmic methodologies necessitates "
        "comprehensive understanding of computational complexity. Subsequently, the "
        "optimization paradigm was utilized by researchers to facilitate enhancement "
        "of processing efficiency metrics. "
    )

    # Repeat to reach desired length
    repetitions = (length // len(base_text)) + 1
    return (base_text * repetitions)[:length]


def benchmark_analysis(text_lengths: List[int]) -> List[BenchmarkResult]:
    """
    Benchmark text analysis performance.

    Args:
        text_lengths: List of text lengths to test.

    Returns:
        List of benchmark results.
    """
    results = []
    analyzer = TextAnalyzer()

    for length in text_lengths:
        text = generate_test_text(length)

        try:
            start_time = time.time()
            analyzer.analyze(text)
            duration = time.time() - start_time

            throughput = length / duration if duration > 0 else 0

            results.append(
                BenchmarkResult(
                    operation="analyze",
                    text_length=length,
                    duration_seconds=duration,
                    throughput_chars_per_sec=throughput,
                    success=True,
                )
            )

        except Exception as e:
            results.append(
                BenchmarkResult(
                    operation="analyze",
                    text_length=length,
                    duration_seconds=0.0,
                    throughput_chars_per_sec=0.0,
                    success=False,
                    error=str(e),
                )
            )

    return results


def benchmark_rewriting(text_lengths: List[int]) -> List[BenchmarkResult]:
    """
    Benchmark text rewriting performance.

    Args:
        text_lengths: List of text lengths to test.

    Returns:
        List of benchmark results.
    """
    results = []
    selector = TextSelector(enable_llm=False)  # Deterministic only

    for length in text_lengths:
        text = generate_test_text(length)

        try:
            start_time = time.time()
            selector.rewrite(text, enable_disclosure=False)
            duration = time.time() - start_time

            throughput = length / duration if duration > 0 else 0

            results.append(
                BenchmarkResult(
                    operation="rewrite",
                    text_length=length,
                    duration_seconds=duration,
                    throughput_chars_per_sec=throughput,
                    success=True,
                )
            )

        except Exception as e:
            results.append(
                BenchmarkResult(
                    operation="rewrite",
                    text_length=length,
                    duration_seconds=0.0,
                    throughput_chars_per_sec=0.0,
                    success=False,
                    error=str(e),
                )
            )

    return results


def display_results(results: List[BenchmarkResult]) -> None:
    """
    Display benchmark results in a table.

    Args:
        results: List of benchmark results.
    """
    table = Table(title="Performance Benchmark Results", show_header=True)
    table.add_column("Operation", style="cyan")
    table.add_column("Text Length", style="yellow", justify="right")
    table.add_column("Duration (s)", style="green", justify="right")
    table.add_column("Throughput (chars/s)", style="magenta", justify="right")
    table.add_column("Status", style="blue")

    for result in results:
        status = "[green]✓ Success[/green]" if result.success else f"[red]✗ {result.error}[/red]"

        table.add_row(
            result.operation,
            f"{result.text_length:,}",
            f"{result.duration_seconds:.3f}",
            f"{result.throughput_chars_per_sec:,.0f}",
            status,
        )

    console.print(table)


def calculate_stats(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """
    Calculate statistics from benchmark results.

    Args:
        results: List of benchmark results.

    Returns:
        Dictionary with statistics.
    """
    successful_results = [r for r in results if r.success]

    if not successful_results:
        return {
            "total_tests": len(results),
            "successful": 0,
            "failed": len(results),
            "avg_duration": 0.0,
            "avg_throughput": 0.0,
        }

    durations = [r.duration_seconds for r in successful_results]
    throughputs = [r.throughput_chars_per_sec for r in successful_results]

    return {
        "total_tests": len(results),
        "successful": len(successful_results),
        "failed": len(results) - len(successful_results),
        "avg_duration": sum(durations) / len(durations),
        "min_duration": min(durations),
        "max_duration": max(durations),
        "avg_throughput": sum(throughputs) / len(throughputs),
        "min_throughput": min(throughputs),
        "max_throughput": max(throughputs),
    }


def main():
    """Run performance benchmarks."""
    console.print("\n[bold cyan]ClearCraft Performance Benchmark[/bold cyan]\n")

    # Test configurations
    text_lengths = [100, 500, 1000, 5000, 10000, 25000]

    console.print("[yellow]Testing text lengths:[/yellow]", ", ".join(f"{l:,}" for l in text_lengths))
    console.print()

    all_results = []

    # Benchmark analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]Benchmarking analysis...",
            total=len(text_lengths),
        )

        for length in text_lengths:
            results = benchmark_analysis([length])
            all_results.extend(results)
            progress.advance(task)

    console.print("[green]✓ Analysis benchmarks complete[/green]\n")

    # Benchmark rewriting
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]Benchmarking rewriting...",
            total=len(text_lengths),
        )

        for length in text_lengths:
            results = benchmark_rewriting([length])
            all_results.extend(results)
            progress.advance(task)

    console.print("[green]✓ Rewriting benchmarks complete[/green]\n")

    # Display results
    display_results(all_results)

    # Calculate and display statistics
    console.print("\n[bold]Summary Statistics:[/bold]\n")

    analysis_results = [r for r in all_results if r.operation == "analyze"]
    rewrite_results = [r for r in all_results if r.operation == "rewrite"]

    analysis_stats = calculate_stats(analysis_results)
    rewrite_stats = calculate_stats(rewrite_results)

    console.print(f"[cyan]Analysis:[/cyan]")
    console.print(f"  Success Rate: {analysis_stats['successful']}/{analysis_stats['total_tests']}")
    console.print(f"  Avg Duration: {analysis_stats['avg_duration']:.3f}s")
    console.print(f"  Avg Throughput: {analysis_stats['avg_throughput']:,.0f} chars/s")

    console.print(f"\n[magenta]Rewriting:[/magenta]")
    console.print(f"  Success Rate: {rewrite_stats['successful']}/{rewrite_stats['total_tests']}")
    console.print(f"  Avg Duration: {rewrite_stats['avg_duration']:.3f}s")
    console.print(f"  Avg Throughput: {rewrite_stats['avg_throughput']:,.0f} chars/s")

    # Performance assessment
    console.print("\n[bold]Performance Assessment:[/bold]\n")

    if analysis_stats['avg_duration'] < 1.0:
        console.print("[green]✓ Analysis performance: Excellent (<1s average)[/green]")
    elif analysis_stats['avg_duration'] < 3.0:
        console.print("[yellow]⚠ Analysis performance: Good (1-3s average)[/yellow]")
    else:
        console.print("[red]✗ Analysis performance: Needs improvement (>3s average)[/red]")

    if rewrite_stats['avg_duration'] < 5.0:
        console.print("[green]✓ Rewriting performance: Excellent (<5s average)[/green]")
    elif rewrite_stats['avg_duration'] < 10.0:
        console.print("[yellow]⚠ Rewriting performance: Good (5-10s average)[/yellow]")
    else:
        console.print("[red]✗ Rewriting performance: Needs improvement (>10s average)[/red]")

    console.print("\n[dim]Note: LLM mode disabled for benchmarking (deterministic only)[/dim]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Benchmark interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()

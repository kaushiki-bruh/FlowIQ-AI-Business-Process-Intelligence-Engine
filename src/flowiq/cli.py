"""
cli.py

Why it exists:
    The doc explicitly says "no frontend required, CLI or simple API
    is sufficient." This is that CLI -- the single entry point a user
    (or an interviewer) runs to see the whole pipeline work.

What problem it solves:
    Gives a runnable demo: `python main.py --report bottlenecks`
    instead of requiring someone to read source code to see output.

Inputs:
    --report flag: which analysis to run.
    --insight flag: also generate an LLM summary (requires insights.py
    and an API key set in .env -- optional, SQL output works without it).

Outputs:
    Printed table of SQL results, optionally followed by an AI summary.
"""

import argparse

from flowiq.analytics import (
    get_completion_stats,
    get_department_throughput,
    get_sla_compliance,
    get_stage_bottlenecks,
)

REPORTS = {
    "bottlenecks": get_stage_bottlenecks,
    "sla": get_sla_compliance,
    "throughput": get_department_throughput,
    "completion": get_completion_stats,
}


def print_report(rows: list[dict]) -> None:
    """Print a list of dict rows as a simple aligned table."""
    if not rows:
        print("No data returned.")
        return
    columns = list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) for c in columns}

    header = " | ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for row in rows:
        print(" | ".join(str(row[c]).ljust(widths[c]) for c in columns))


def main():
    parser = argparse.ArgumentParser(description="FlowIQ -- workflow analytics CLI")
    parser.add_argument(
        "--report",
        choices=list(REPORTS.keys()),
        required=True,
        help="Which analysis to run",
    )
    parser.add_argument(
        "--insight",
        action="store_true",
        help="Also generate an LLM business-recommendation summary (requires API key in .env)",
    )
    args = parser.parse_args()

    rows = REPORTS[args.report]()
    print_report(rows)

    if args.insight:
        from flowiq.insights import summarize  # imported lazily so SQL-only use never needs an API key
        print()
        print("AI Insight:")
        print(summarize(args.report, rows))


if __name__ == "__main__":
    main()

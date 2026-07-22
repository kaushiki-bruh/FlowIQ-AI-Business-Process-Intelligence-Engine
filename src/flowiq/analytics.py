"""
analytics.py

Why it exists:
    This is the only module allowed to run SQL analytical queries. It
    reads from the views defined in sql/03_analytics_views.sql -- never
    raw tables directly -- so every number the rest of the app sees has
    already been through one correct, reviewable SQL query.

What problem it solves:
    Keeps "what does the data say" (SQL, exact) separate from
    "how do we explain it" (LLM, insights.py) -- the LLM should never
    be doing arithmetic.

Inputs:
    None from the caller -- each function opens its own connection via
    db.get_connection().

Outputs:
    Plain Python data structures (list of dicts) -- no SQL leaks past
    this module.
"""

from flowiq.db import get_connection


def _query_to_dicts(sql: str) -> list[dict]:
    """Run a query and return rows as a list of dicts (column name -> value)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_stage_bottlenecks() -> list[dict]:
    """Return the single worst (rank 1) stage per workflow type."""
    return _query_to_dicts("""
        SELECT workflow_name, stage_name, stage_order,
               event_count, avg_duration_hours
        FROM v_stage_bottlenecks
        WHERE bottleneck_rank = 1
        ORDER BY avg_duration_hours DESC;
    """)


def get_sla_compliance() -> list[dict]:
    """Return SLA breach rate per workflow type, worst first."""
    return _query_to_dicts("""
        SELECT workflow_name, completed_instances, breached_count, breach_pct
        FROM v_sla_compliance_summary
        ORDER BY breach_pct DESC;
    """)


def get_department_throughput() -> list[dict]:
    """Return departments ranked by total events handled."""
    return _query_to_dicts("""
        SELECT department_name, events_handled, active_employees, avg_handling_hours
        FROM v_department_throughput
        ORDER BY events_handled DESC;
    """)


def get_completion_stats() -> list[dict]:
    """Return volume, status breakdown, and avg/median completion time per workflow type."""
    return _query_to_dicts("""
        SELECT workflow_name, total_instances, completed_count, delayed_count,
               cancelled_count, in_progress_count,
               avg_completion_hours, median_completion_hours
        FROM v_completion_stats
        ORDER BY avg_completion_hours DESC;
    """)

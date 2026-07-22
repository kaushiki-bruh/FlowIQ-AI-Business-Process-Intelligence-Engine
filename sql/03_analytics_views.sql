-- 03_analytics_views.sql
--
-- Analytical layer for FlowIQ. Each view answers one specific business
-- question from the project spec. These are the ONLY things
-- src/flowiq/analytics.py is allowed to query -- never raw tables --
-- so every number that eventually reaches the LLM has already passed
-- through one reviewable, correct SQL query.
--
-- Run after 01_schema.sql and 02_load_data.sql.


-- ============================================================================
-- v_stage_bottlenecks
-- Business question: "Which workflow stage causes the biggest delay?"
-- Technique: window function (RANK) partitioned per workflow type, so each
-- workflow type gets its own ranking of its own stages, not a global one.
-- ============================================================================
CREATE OR REPLACE VIEW v_stage_bottlenecks AS
SELECT
    wt.workflow_type_id,
    wt.workflow_name,
    ws.stage_id,
    ws.stage_name,
    ws.stage_order,
    COUNT(we.event_id) AS event_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (we.exited_at - we.entered_at)) / 3600)::numeric, 2) AS avg_duration_hours,
    RANK() OVER (
        PARTITION BY wt.workflow_type_id
        ORDER BY AVG(EXTRACT(EPOCH FROM (we.exited_at - we.entered_at))) DESC
    ) AS bottleneck_rank
FROM workflow_events we
JOIN workflow_stages ws ON we.stage_id = ws.stage_id
JOIN workflow_types wt ON ws.workflow_type_id = wt.workflow_type_id
WHERE we.exited_at IS NOT NULL
GROUP BY wt.workflow_type_id, wt.workflow_name, ws.stage_id, ws.stage_name, ws.stage_order;

-- Usage: SELECT * FROM v_stage_bottlenecks WHERE bottleneck_rank = 1;
--   -> the single worst stage per workflow type


-- ============================================================================
-- v_sla_compliance / v_sla_compliance_summary
-- Business question: "Which workflows violate SLA?"
-- Technique: CTE to compute actual duration once, CASE to bucket
-- on-time vs breached, FILTER to aggregate the bucketed result.
-- ============================================================================
CREATE OR REPLACE VIEW v_sla_compliance AS
WITH instance_duration AS (
    SELECT
        wi.workflow_instance_id,
        wi.workflow_type_id,
        EXTRACT(EPOCH FROM (wi.completed_at - wi.created_at)) / 3600 AS actual_hours,
        s.max_duration_hours
    FROM workflow_instances wi
    JOIN sla s ON wi.workflow_type_id = s.workflow_type_id
    WHERE wi.completed_at IS NOT NULL   -- only finished instances have a real duration
)
SELECT
    workflow_instance_id,
    workflow_type_id,
    ROUND(actual_hours::numeric, 2) AS actual_hours,
    max_duration_hours,
    CASE WHEN actual_hours > max_duration_hours THEN 'Breached' ELSE 'On Time' END AS sla_status
FROM instance_duration;

CREATE OR REPLACE VIEW v_sla_compliance_summary AS
SELECT
    wt.workflow_name,
    COUNT(*) AS completed_instances,
    COUNT(*) FILTER (WHERE v.sla_status = 'Breached') AS breached_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE v.sla_status = 'Breached') / COUNT(*), 1) AS breach_pct
FROM v_sla_compliance v
JOIN workflow_types wt ON v.workflow_type_id = wt.workflow_type_id
GROUP BY wt.workflow_name
ORDER BY breach_pct DESC;

-- Usage: SELECT * FROM v_sla_compliance_summary;
--   -> one row per workflow type, ranked worst breach rate first


-- ============================================================================
-- v_department_throughput
-- Business question: "Which department processes the most requests?"
-- Technique: GROUP BY / HAVING, joining events -> employees -> departments.
-- ============================================================================
CREATE OR REPLACE VIEW v_department_throughput AS
SELECT
    d.department_id,
    d.department_name,
    COUNT(we.event_id) AS events_handled,
    COUNT(DISTINCT e.employee_id) AS active_employees,
    ROUND(AVG(EXTRACT(EPOCH FROM (we.exited_at - we.entered_at)) / 3600)::numeric, 2) AS avg_handling_hours
FROM workflow_events we
JOIN employees e ON we.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE we.exited_at IS NOT NULL
GROUP BY d.department_id, d.department_name
HAVING COUNT(we.event_id) > 0
ORDER BY events_handled DESC;

-- Usage: SELECT * FROM v_department_throughput;
--   -> departments ranked by total events handled


-- ============================================================================
-- v_completion_stats
-- Business question: "What is the average completion time?" (overall and
-- per workflow type, broken down by outcome)
-- Technique: FILTER clause per status bucket, PERCENTILE_CONT for median
-- alongside AVG -- shows the mean isn't being skewed by outliers.
-- ============================================================================
CREATE OR REPLACE VIEW v_completion_stats AS
SELECT
    wt.workflow_type_id,
    wt.workflow_name,
    COUNT(*) AS total_instances,
    COUNT(*) FILTER (WHERE wi.status = 'Completed')  AS completed_count,
    COUNT(*) FILTER (WHERE wi.status = 'Delayed')     AS delayed_count,
    COUNT(*) FILTER (WHERE wi.status = 'Cancelled')   AS cancelled_count,
    COUNT(*) FILTER (WHERE wi.status = 'In Progress') AS in_progress_count,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (wi.completed_at - wi.created_at)) / 3600)
            FILTER (WHERE wi.completed_at IS NOT NULL)::numeric, 2
    ) AS avg_completion_hours,
    ROUND(
        (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (wi.completed_at - wi.created_at)) / 3600)
            FILTER (WHERE wi.completed_at IS NOT NULL))::numeric, 2
    ) AS median_completion_hours
FROM workflow_instances wi
JOIN workflow_types wt ON wi.workflow_type_id = wt.workflow_type_id
GROUP BY wt.workflow_type_id, wt.workflow_name
ORDER BY avg_completion_hours DESC;

-- Usage: SELECT * FROM v_completion_stats;
--   -> one row per workflow type: volume, status breakdown, avg + median hours

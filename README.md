# FlowIQ — AI Workflow Intelligence Platform

## Project Overview
FlowIQ analyzes operational business workflows (purchase orders, invoice
approvals, employee onboarding, IT service requests, customer complaint
resolution) to identify bottlenecks, measure SLA compliance, and generate
plain-language business recommendations.

Workflow data → SQL analytics → LLM summary. The LLM never replaces SQL —
it explains what SQL already found.

## Architecture
```
CSV data --> PostgreSQL (normalized schema) --> SQL analytical views
                                                      |
                                                      v
                                             Python reads views
                                                      |
                                                      v
                                          LangChain + LLM turns numbers
                                          into a business recommendation
                                                      |
                                                      v
                                                    output
```

## Folder Structure
```
flowiq/
├── data/
│   └── generate_dataset.py     # synthetic dataset generator
├── datasets/                   # generated CSVs (gitignored)
├── sql/
│   ├── 01_schema.sql           # table definitions
│   ├── 02_load_data.sql        # \copy load script
│   └── 03_analytics_views.sql  # bottleneck / SLA / throughput views
├── src/flowiq/
│   ├── db.py                   # database connection helper
│   ├── analytics.py            # runs SQL views, returns results
│   ├── insights.py             # LangChain summarization layer
│   └── cli.py                  # command-line entry point
├── main.py
├── requirements.txt
└── .env.example
```

## Database Design
Star-schema-style: `workflow_events` is the fact table (one row per
stage transition); `departments`, `employees`, `workflow_types`,
`workflow_stages`, and `sla` are reference/dimension tables around it.
See `sql/01_schema.sql` for full DDL with constraints and indexes.

## Installation
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your DB credentials and LLM API key
python data/generate_dataset.py
psql -h <host> -U <user> -d <db> -f sql/01_schema.sql
psql -h <host> -U <user> -d <db> -f sql/02_load_data.sql
psql -h <host> -U <user> -d <db> -f sql/03_analytics_views.sql
```

## Sample Output
```
$ python main.py --report bottlenecks
workflow_name                 | stage_name          | stage_order | event_count | avg_duration_hours
----------------------------------------------------------------------------------------------------
Invoice Approval               | Finance Review      | 3           | 283         | 18.30
Customer Complaint Resolution  | Complaint Logged    | 1           | 280         | 16.61
IT Service Request             | Ticket Closed       | 6           | 243         | 15.20
Employee Onboarding            | Offer Accepted      | 1           | 311         | 15.19
Purchase Order Processing      | Budget Verification | 3           | 280         | 12.62
```
```
$ python main.py --report bottlenecks --insight
...(table as above)...

AI Insight:
Finance Review is the single largest bottleneck across all workflow
types, averaging 18.3 hours per instance. Consider adding a secondary
approver or a defined auto-approval threshold for low-value invoices
to reduce dependency on a single reviewer.
```
(`--insight` requires an LLM API key in `.env` — see Installation)

## Business Value
Turns raw operational event logs into specific, ranked recommendations —
answering questions like which stage causes the most delay, which
workflows breach SLA, and which department carries the most load —
without requiring a BI tool or manual spreadsheet analysis.

## Future Improvements
- Materialized views / partitioning if event volume grows significantly
- Scheduled batch refresh (cron) instead of manual reruns
- Optional FastAPI wrapper if a callable API is needed beyond the CLI
- EC2 (or RDS-backed) deployment once the local pipeline is stable

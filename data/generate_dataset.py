#!/usr/bin/env python3
"""
generate_dataset.py

Generates a complete synthetic workflow-management dataset consisting of
7 related CSV files (departments, employees, workflow_types, workflow_stages,
sla, workflow_instances, workflow_events) into a local "datasets" folder.

Only uses: pandas, random, csv, pathlib, datetime
"""

import random
import csv
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

random.seed(42)

OUTPUT_DIR = Path("datasets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def random_datetime(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between start and end."""
    delta = end - start
    total_seconds = int(delta.total_seconds())
    if total_seconds <= 0:
        return start
    random_seconds = random.randint(0, total_seconds)
    return start + timedelta(seconds=random_seconds)


# ---------------------------------------------------------------------------
# 1. departments.csv
# ---------------------------------------------------------------------------

DEPARTMENT_NAMES = [
    "Procurement",
    "Finance",
    "Warehouse",
    "Operations",
    "Quality Assurance",
    "Human Resources",
    "Customer Support",
    "IT Services",
]


def generate_departments():
    rows = []
    base_created = datetime(2023, 1, 1)
    for idx, name in enumerate(DEPARTMENT_NAMES, start=1):
        created_at = base_created + timedelta(days=random.randint(0, 60))
        rows.append({
            "department_id": idx,
            "department_name": name,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rows


# ---------------------------------------------------------------------------
# 2. employees.csv
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Ananya", "Diya", "Ira", "Myra", "Saanvi", "Aadhya",
    "Kiara", "Navya", "Riya", "Priya", "Rahul", "Amit", "Sanjay", "Vikram",
    "Neha", "Pooja", "Kavya", "Meera", "Rajesh", "Suresh", "Anil", "Deepak",
    "Sunita", "Kavita", "Manoj", "Vinod", "Alok", "Nikhil", "Tanvi", "Isha",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Mehta", "Patel", "Reddy", "Nair", "Iyer",
    "Kulkarni", "Deshmukh", "Joshi", "Rao", "Chatterjee", "Bose", "Das",
    "Mukherjee", "Kapoor", "Chopra", "Malhotra", "Bhatia", "Agarwal", "Singh",
    "Yadav", "Pandey", "Mishra", "Trivedi", "Shah", "Bhatt", "Rana", "Chauhan",
]


def generate_employees(num_employees: int, department_ids: list[int]):
    rows = []
    base_created = datetime(2023, 2, 1)
    used_emails = set()

    for idx in range(1, num_employees + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"

        email_base = f"{first.lower()}.{last.lower()}"
        email = f"{email_base}@company.com"
        suffix = 1
        while email in used_emails:
            suffix += 1
            email = f"{email_base}{suffix}@company.com"
        used_emails.add(email)

        department_id = random.choice(department_ids)
        created_at = base_created + timedelta(days=random.randint(0, 300))

        rows.append({
            "employee_id": idx,
            "employee_name": full_name,
            "email": email,
            "department_id": department_id,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rows


# ---------------------------------------------------------------------------
# 3. workflow_types.csv
# ---------------------------------------------------------------------------

WORKFLOW_TYPE_NAMES = [
    "Purchase Order Processing",
    "Invoice Approval",
    "Employee Onboarding",
    "IT Service Request",
    "Customer Complaint Resolution",
]


def generate_workflow_types():
    rows = []
    base_created = datetime(2023, 1, 15)
    for idx, name in enumerate(WORKFLOW_TYPE_NAMES, start=1):
        created_at = base_created + timedelta(days=random.randint(0, 30))
        rows.append({
            "workflow_type_id": idx,
            "workflow_type_name": name,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rows


# ---------------------------------------------------------------------------
# 4. workflow_stages.csv
# ---------------------------------------------------------------------------

STAGE_DEFINITIONS = {
    "Purchase Order Processing": [
        "PO Created",
        "Manager Approval",
        "Budget Verification",
        "Vendor Confirmation",
        "Goods Receipt",
        "PO Closed",
    ],
    "Invoice Approval": [
        "Invoice Received",
        "Data Entry Verification",
        "Finance Review",
        "Manager Approval",
        "Payment Processed",
    ],
    "Employee Onboarding": [
        "Offer Accepted",
        "Documentation Collection",
        "IT Account Setup",
        "Orientation Scheduled",
        "Department Induction",
        "Onboarding Completed",
    ],
    "IT Service Request": [
        "Ticket Raised",
        "Ticket Triaged",
        "Assigned to Technician",
        "In Progress",
        "Resolution Verification",
        "Ticket Closed",
    ],
    "Customer Complaint Resolution": [
        "Complaint Logged",
        "Initial Assessment",
        "Investigation",
        "Resolution Proposed",
        "Customer Confirmation",
    ],
}


def generate_workflow_stages(workflow_types: list[dict]):
    rows = []
    stage_id = 1
    stages_by_workflow_type = {}

    for wf in workflow_types:
        wf_id = wf["workflow_type_id"]
        wf_name = wf["workflow_type_name"]
        stage_names = STAGE_DEFINITIONS[wf_name]

        stage_ids_for_wf = []
        for order, stage_name in enumerate(stage_names, start=1):
            rows.append({
                "stage_id": stage_id,
                "workflow_type_id": wf_id,
                "stage_name": stage_name,
                "stage_order": order,
            })
            stage_ids_for_wf.append(stage_id)
            stage_id += 1

        stages_by_workflow_type[wf_id] = stage_ids_for_wf

    return rows, stages_by_workflow_type


# ---------------------------------------------------------------------------
# 5. sla.csv
# ---------------------------------------------------------------------------

SLA_HOURS_BY_WORKFLOW_TYPE = {
    "Purchase Order Processing": 72,
    "Invoice Approval": 48,
    "Employee Onboarding": 120,
    "IT Service Request": 24,
    "Customer Complaint Resolution": 96,
}


def generate_sla(workflow_types: list[dict]):
    rows = []
    for idx, wf in enumerate(workflow_types, start=1):
        wf_name = wf["workflow_type_name"]
        max_duration = SLA_HOURS_BY_WORKFLOW_TYPE[wf_name]
        rows.append({
            "sla_id": idx,
            "workflow_type_id": wf["workflow_type_id"],
            "max_duration_hours": max_duration,
        })
    return rows


# ---------------------------------------------------------------------------
# 6. workflow_instances.csv
# ---------------------------------------------------------------------------

REFERENCE_PREFIXES = {
    "Purchase Order Processing": "PO",
    "Invoice Approval": "INV",
    "Employee Onboarding": "ONB",
    "IT Service Request": "IT",
    "Customer Complaint Resolution": "CMP",
}

INSTANCE_STATUSES = ["Completed", "Delayed", "Cancelled", "In Progress"]
INSTANCE_STATUS_WEIGHTS = [0.60, 0.20, 0.05, 0.15]


def generate_workflow_instances(num_instances: int, workflow_types: list[dict]):
    rows = []
    ref_counters = {wf["workflow_type_id"]: 0 for wf in workflow_types}
    wf_type_ids = [wf["workflow_type_id"] for wf in workflow_types]
    wf_name_by_id = {wf["workflow_type_id"]: wf["workflow_type_name"] for wf in workflow_types}

    period_start = datetime(2026, 1, 1)
    period_end = datetime(2026, 7, 1)

    for idx in range(1, num_instances + 1):
        wf_type_id = random.choice(wf_type_ids)
        wf_name = wf_name_by_id[wf_type_id]
        prefix = REFERENCE_PREFIXES[wf_name]

        ref_counters[wf_type_id] += 1
        reference_number = f"{prefix}-2026-{ref_counters[wf_type_id]:06d}"

        created_at = random_datetime(period_start, period_end)

        status = random.choices(INSTANCE_STATUSES, weights=INSTANCE_STATUS_WEIGHTS, k=1)[0]

        if status in ("Completed", "Delayed"):
            # completion between a few hours and ~10 days later
            duration_hours = random.uniform(2, 240)
            completed_at = created_at + timedelta(hours=duration_hours)
            completed_at_str = completed_at.strftime("%Y-%m-%d %H:%M:%S")
        elif status == "Cancelled":
            duration_hours = random.uniform(1, 72)
            completed_at = created_at + timedelta(hours=duration_hours)
            completed_at_str = completed_at.strftime("%Y-%m-%d %H:%M:%S")
        else:  # In Progress
            completed_at_str = ""

        rows.append({
            "workflow_instance_id": idx,
            "workflow_type_id": wf_type_id,
            "reference_number": reference_number,
            "status": status,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": completed_at_str,
        })

    return rows


# ---------------------------------------------------------------------------
# 7. workflow_events.csv
# ---------------------------------------------------------------------------

EVENT_STATUS_CHOICES = ["Normal", "Delayed", "SLA Breach", "Escalated", "Cancelled"]
EVENT_STATUS_WEIGHTS = [0.70, 0.15, 0.08, 0.05, 0.02]

REMARKS_BY_EVENT_STATUS = {
    "Normal": [
        "Approved",
        "Completed successfully",
        "Processed as expected",
        "Verified and forwarded",
        "Reviewed and cleared",
        "Documentation confirmed",
        "Stock available, processed",
    ],
    "Delayed": [
        "Waiting for Finance",
        "Vendor delay",
        "Pending manager response",
        "Awaiting additional documents",
        "Delayed due to backlog",
        "Stock unavailable",
    ],
    "SLA Breach": [
        "SLA breached, needs urgent action",
        "Exceeded processing time",
        "Overdue - escalation required",
        "Missed target resolution time",
    ],
    "Escalated": [
        "Escalated to Manager",
        "Escalated to Department Head",
        "Escalated due to repeated delay",
        "Escalated for priority handling",
    ],
    "Cancelled": [
        "Cancelled by requester",
        "Cancelled due to duplicate entry",
        "Invoice mismatch",
        "Cancelled - vendor unresponsive",
    ],
}


def generate_workflow_events(
    workflow_instances: list[dict],
    stages_by_workflow_type: dict,
    employee_ids: list[int],
    target_min: int,
    target_max: int,
):
    rows = []
    event_id = 1

    # First pass: generate events strictly following each instance's stage
    # sequence, in chronological order.
    for instance in workflow_instances:
        wf_type_id = instance["workflow_type_id"]
        stage_ids = stages_by_workflow_type[wf_type_id]

        instance_created_at = datetime.strptime(instance["created_at"], "%Y-%m-%d %H:%M:%S")

        if instance["completed_at"]:
            instance_end_at = datetime.strptime(instance["completed_at"], "%Y-%m-%d %H:%M:%S")
        else:
            # In Progress: give it a plausible "so far" window
            instance_end_at = instance_created_at + timedelta(hours=random.uniform(2, 48))

        # If a workflow is "In Progress" or "Cancelled", it may not have
        # reached every stage yet.
        if instance["status"] == "In Progress":
            num_stages_reached = random.randint(1, len(stage_ids))
        elif instance["status"] == "Cancelled":
            num_stages_reached = random.randint(1, max(1, len(stage_ids) - 1))
        else:
            num_stages_reached = len(stage_ids)

        stage_ids_reached = stage_ids[:num_stages_reached]

        # Distribute time across the reached stages chronologically.
        total_span = (instance_end_at - instance_created_at).total_seconds()
        if total_span <= 0:
            total_span = 3600  # fallback: 1 hour

        num_segments = len(stage_ids_reached)
        # boundaries divide the total span into num_segments chronological chunks
        boundaries = sorted(
            random.uniform(0, total_span) for _ in range(num_segments - 1)
        ) if num_segments > 1 else []
        boundaries = [0] + boundaries + [total_span]

        for i, stage_id in enumerate(stage_ids_reached):
            segment_start = instance_created_at + timedelta(seconds=boundaries[i])
            segment_end = instance_created_at + timedelta(seconds=boundaries[i + 1])

            # Ensure entered_at < exited_at with at least a few minutes gap
            if segment_end <= segment_start:
                segment_end = segment_start + timedelta(minutes=random.randint(5, 30))

            entered_at = segment_start
            exited_at = segment_end

            # Determine event status. Last stage of a cancelled workflow is
            # forced to "Cancelled"; otherwise weighted random choice.
            if instance["status"] == "Cancelled" and i == num_segments - 1:
                event_status = "Cancelled"
            else:
                event_status = random.choices(
                    EVENT_STATUS_CHOICES, weights=EVENT_STATUS_WEIGHTS, k=1
                )[0]

            remarks = random.choice(REMARKS_BY_EVENT_STATUS[event_status])
            employee_id = random.choice(employee_ids)

            rows.append({
                "event_id": event_id,
                "workflow_instance_id": instance["workflow_instance_id"],
                "stage_id": stage_id,
                "employee_id": employee_id,
                "entered_at": entered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "exited_at": exited_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": event_status,
                "remarks": remarks,
            })
            event_id += 1

    # Second pass: top up (or trim) to land within the target event-count
    # range, while still respecting chronology / stage / instance validity.
    if len(rows) < target_min:
        needed = random.randint(target_min, target_max) - len(rows)
        needed = max(needed, 0)

        for _ in range(needed):
            instance = random.choice(workflow_instances)
            wf_type_id = instance["workflow_type_id"]
            stage_ids = stages_by_workflow_type[wf_type_id]
            stage_id = random.choice(stage_ids)

            instance_created_at = datetime.strptime(instance["created_at"], "%Y-%m-%d %H:%M:%S")
            if instance["completed_at"]:
                instance_end_at = datetime.strptime(instance["completed_at"], "%Y-%m-%d %H:%M:%S")
            else:
                instance_end_at = instance_created_at + timedelta(hours=random.uniform(2, 48))

            if instance_end_at <= instance_created_at:
                instance_end_at = instance_created_at + timedelta(hours=1)

            entered_at = random_datetime(instance_created_at, instance_end_at)
            max_gap = max(int((instance_end_at - entered_at).total_seconds()), 60)
            exited_at = entered_at + timedelta(seconds=random.randint(60, min(max_gap, 6 * 3600)))
            if exited_at > instance_end_at:
                exited_at = instance_end_at + timedelta(minutes=random.randint(1, 15))

            event_status = random.choices(
                EVENT_STATUS_CHOICES, weights=EVENT_STATUS_WEIGHTS, k=1
            )[0]
            remarks = random.choice(REMARKS_BY_EVENT_STATUS[event_status])
            employee_id = random.choice(employee_ids)

            rows.append({
                "event_id": event_id,
                "workflow_instance_id": instance["workflow_instance_id"],
                "stage_id": stage_id,
                "employee_id": employee_id,
                "entered_at": entered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "exited_at": exited_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": event_status,
                "remarks": remarks,
            })
            event_id += 1

    elif len(rows) > target_max:
        random.shuffle(rows)
        rows = rows[:target_max]
        # Re-sequence event_id after trimming
        for i, row in enumerate(rows, start=1):
            row["event_id"] = i

    return rows


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_csv(rows: list[dict], filename: str, fieldnames: list[str]):
    filepath = OUTPUT_DIR / filename
    df = pd.DataFrame(rows, columns=fieldnames)
    df.to_csv(filepath, index=False, quoting=csv.QUOTE_MINIMAL)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # 1. Departments
    departments = generate_departments()
    save_csv(
        departments,
        "departments.csv",
        ["department_id", "department_name", "created_at"],
    )
    department_ids = [d["department_id"] for d in departments]

    # 2. Employees
    employees = generate_employees(40, department_ids)
    save_csv(
        employees,
        "employees.csv",
        ["employee_id", "employee_name", "email", "department_id", "created_at"],
    )
    employee_ids = [e["employee_id"] for e in employees]

    # 3. Workflow types
    workflow_types = generate_workflow_types()
    save_csv(
        workflow_types,
        "workflow_types.csv",
        ["workflow_type_id", "workflow_type_name", "created_at"],
    )

    # 4. Workflow stages
    workflow_stages, stages_by_workflow_type = generate_workflow_stages(workflow_types)
    save_csv(
        workflow_stages,
        "workflow_stages.csv",
        ["stage_id", "workflow_type_id", "stage_name", "stage_order"],
    )

    # 5. SLA
    sla_rows = generate_sla(workflow_types)
    save_csv(
        sla_rows,
        "sla.csv",
        ["sla_id", "workflow_type_id", "max_duration_hours"],
    )

    # 6. Workflow instances
    workflow_instances = generate_workflow_instances(1000, workflow_types)
    save_csv(
        workflow_instances,
        "workflow_instances.csv",
        [
            "workflow_instance_id",
            "workflow_type_id",
            "reference_number",
            "status",
            "created_at",
            "completed_at",
        ],
    )

    # 7. Workflow events
    workflow_events = generate_workflow_events(
        workflow_instances,
        stages_by_workflow_type,
        employee_ids,
        target_min=7000,
        target_max=9000,
    )
    save_csv(
        workflow_events,
        "workflow_events.csv",
        [
            "event_id",
            "workflow_instance_id",
            "stage_id",
            "employee_id",
            "entered_at",
            "exited_at",
            "status",
            "remarks",
        ],
    )

    # 8. Merged dataset (single wide CSV combining all tables, one row
    #    per workflow event, with related instance/type/stage/employee/
    #    department/SLA data joined in)
    generate_merged_dataset()

    print("Dataset generation completed successfully.")


def generate_merged_dataset():
    """Join all 7 CSVs into one wide CSV, one row per workflow event."""
    dept = pd.read_csv(OUTPUT_DIR / "departments.csv")
    emp = pd.read_csv(OUTPUT_DIR / "employees.csv")
    wt = pd.read_csv(OUTPUT_DIR / "workflow_types.csv")
    ws = pd.read_csv(OUTPUT_DIR / "workflow_stages.csv")
    sla = pd.read_csv(OUTPUT_DIR / "sla.csv")
    wi = pd.read_csv(OUTPUT_DIR / "workflow_instances.csv")
    we = pd.read_csv(OUTPUT_DIR / "workflow_events.csv")

    we = we.rename(columns={"status": "event_status"})
    wi = wi.rename(columns={"status": "instance_status", "created_at": "instance_created_at"})
    emp = emp.rename(columns={"created_at": "employee_created_at"})
    dept = dept.rename(columns={"created_at": "department_created_at"})
    wt = wt.rename(columns={"created_at": "workflow_type_created_at"})

    merged = we.merge(wi, on="workflow_instance_id")
    merged = merged.merge(wt, on="workflow_type_id")
    merged = merged.merge(ws, on=["stage_id", "workflow_type_id"])
    merged = merged.merge(sla, on="workflow_type_id")
    merged = merged.merge(emp, on="employee_id")
    merged = merged.merge(dept, on="department_id")

    col_order = [
        "event_id", "workflow_instance_id", "reference_number",
        "workflow_type_id", "workflow_type_name",
        "stage_id", "stage_name", "stage_order",
        "employee_id", "employee_name", "email",
        "department_id", "department_name",
        "entered_at", "exited_at", "event_status", "remarks",
        "instance_status", "instance_created_at", "completed_at",
        "sla_id", "max_duration_hours",
        "workflow_type_created_at", "employee_created_at", "department_created_at",
    ]
    merged = merged[col_order]
    merged.to_csv(OUTPUT_DIR / "merged_dataset.csv", index=False, quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":
    main()


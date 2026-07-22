\copy departments (department_id, department_name, created_at) FROM 'datasets/departments.csv' WITH (FORMAT csv, HEADER true)

\copy workflow_types (workflow_type_id, workflow_name, created_at) FROM 'datasets/workflow_types.csv' WITH (FORMAT csv, HEADER true)

\copy employees (employee_id, employee_name, email, department_id, created_at) FROM 'datasets/employees.csv' WITH (FORMAT csv, HEADER true)

\copy workflow_stages (stage_id, workflow_type_id, stage_name, stage_order) FROM 'datasets/workflow_stages.csv' WITH (FORMAT csv, HEADER true)

\copy sla (sla_id, workflow_type_id, max_duration_hours) FROM 'datasets/sla.csv' WITH (FORMAT csv, HEADER true)

\copy workflow_instances (workflow_instance_id, workflow_type_id, reference_number, status, created_at, completed_at) FROM 'datasets/workflow_instances.csv' WITH (FORMAT csv, HEADER true, NULL '')

\copy workflow_events (event_id, workflow_instance_id, stage_id, employee_id, entered_at, exited_at, status, remarks) FROM 'datasets/workflow_events.csv' WITH (FORMAT csv, HEADER true)

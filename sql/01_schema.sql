-- 01_schema.sql
-- Table definitions for FlowIQ. Matches what's already running in your
-- database — kept here so the schema is version-controlled and
-- reproducible, not just something that exists only inside Postgres.

CREATE TABLE IF NOT EXISTS departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_types (
    workflow_type_id INT PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS workflow_stages (
    stage_id INT PRIMARY KEY,
    workflow_type_id INT NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    stage_order INT NOT NULL,
    FOREIGN KEY (workflow_type_id) REFERENCES workflow_types(workflow_type_id)
);

CREATE TABLE IF NOT EXISTS workflow_instances (
    workflow_instance_id INT PRIMARY KEY,
    workflow_type_id INT NOT NULL,
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (workflow_type_id) REFERENCES workflow_types(workflow_type_id)
);

CREATE TABLE IF NOT EXISTS workflow_events (
    event_id INT PRIMARY KEY,
    workflow_instance_id INT NOT NULL,
    stage_id INT NOT NULL,
    employee_id INT NOT NULL,
    entered_at TIMESTAMP NOT NULL,
    exited_at TIMESTAMP,
    status VARCHAR(30) NOT NULL,
    remarks TEXT,
    FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(workflow_instance_id),
    FOREIGN KEY (stage_id) REFERENCES workflow_stages(stage_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS sla (
    sla_id INT PRIMARY KEY,
    workflow_type_id INT UNIQUE NOT NULL,
    max_duration_hours INT NOT NULL,
    FOREIGN KEY (workflow_type_id) REFERENCES workflow_types(workflow_type_id)
);

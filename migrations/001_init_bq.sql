-- BigQuery migration for SAMDIAGNOSIS (run on BigQuery)
CREATE SCHEMA IF NOT EXISTS `samdiagnosis_data`;

CREATE TABLE IF NOT EXISTS `samdiagnosis_data.patients` (
  patient_id STRING,
  medical_record_number STRING,
  first_name STRING,
  last_name STRING,
  dob DATE,
  gender STRING,
  phone STRING,
  metadata STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS `samdiagnosis_data.reports` (
  report_id STRING,
  patient_id STRING,
  doctor_id STRING,
  visit_id STRING,
  report_type STRING,
  title STRING,
  content STRING,
  embedding ARRAY<FLOAT64>,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

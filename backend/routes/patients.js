const express = require('express');
const router = express.Router();
const bq = require('../db');
const { v4: uuidv4 } = require('uuid');

// Create patient
router.post('/', async (req, res) => {
  try {
    const { medical_record_number, first_name, last_name, dob, gender, phone, metadata } = req.body;
    const patient_id = uuidv4();
    const sql = `INSERT INTO \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.patients\` (patient_id, medical_record_number, first_name, last_name, dob, gender, phone, metadata) VALUES (@patient_id,@mrn,@fn,@ln,@dob,@gender,@phone,@metadata)`;
    await bq.query({ query: sql, params: { patient_id, mrn: medical_record_number, fn: first_name, ln: last_name, dob, gender, phone, metadata } });
    res.json({ ok: true, patient_id });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// List patients (simple)
router.get('/', async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.patients` + '` LIMIT 100';
    const [rows] = await bq.query({ query: sql });
    res.json({ ok: true, patients: rows });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// Get patient + reports
router.get('/:id', async (req, res) => {
  try {
    const pid = req.params.id;
    const psql = `SELECT * FROM \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.patients\` WHERE patient_id = @pid`;
    const rsql = `SELECT * FROM \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.reports\` WHERE patient_id = @pid ORDER BY created_at DESC`;
    const [pRows] = await bq.query({ query: psql, params: { pid } });
    if (pRows.length === 0) return res.status(404).json({ ok:false, error: 'Patient not found' });
    const [rRows] = await bq.query({ query: rsql, params: { pid } });
    res.json({ ok: true, patient: pRows[0], reports: rRows });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

module.exports = router;

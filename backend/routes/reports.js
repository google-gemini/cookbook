const express = require('express');
const router = express.Router();
const bq = require('../db');
const { generateText, generateEmbedding } = require('../vertexClient');
const { v4: uuidv4 } = require('uuid');

// Add report and request embedding generation asynchronously (simple flow: generate embedding inline — can be changed to background)
router.post('/', async (req, res) => {
  try {
    const { patient_id, doctor_id, visit_id=null, report_type='SOAP', title=null, content } = req.body;
    const report_id = uuidv4();
    const insertSql = `INSERT INTO \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.reports\` (report_id, patient_id, doctor_id, visit_id, report_type, title, content) VALUES (@report_id,@patient_id,@doctor_id,@visit_id,@report_type,@title,@content)`;
    await bq.query({ query: insertSql, params: { report_id, patient_id, doctor_id, visit_id, report_type, title, content } });

    // generate embedding and update record (you can move this to a background worker)
    try {
      const emb = await generateEmbedding(content);
      const updateSql = `UPDATE \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.reports\` SET embedding = @emb WHERE report_id = @report_id`;
      await bq.query({ query: updateSql, params: { emb, report_id } });
    } catch (e) {
      console.warn('Embedding failed: ', e.message);
    }

    res.json({ ok: true, report_id });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// Generate SOAP by AI for some patient summary
router.post('/generate-soap', async (req, res) => {
  try {
    const { patient_id, condition_summary } = req.body;
    const prompt = `Generate a concise SOAP medical progress note (Subjective, Objective, Assessment, Plan) for the following: ${condition_summary}. Keep it formal and without PHI.`;
    const generated = await generateText(prompt);
    res.json({ ok: true, generated });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok:false, error: e.message });
  }
});

// Simple semantic search: generate embedding for query, then search by computing distance in BigQuery (requires embedding column)
router.post('/semantic-search', async (req, res) => {
  try {
    const { query_text, topK=10 } = req.body;
    const qEmb = await generateEmbedding(query_text);
    const sql = `
      SELECT report_id, patient_id, title, content, ML.DISTANCE(embedding, @qEmb, 'COSINE') as distance
      FROM \`${process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT}.samdiagnosis_data.reports\`
      WHERE embedding IS NOT NULL
      ORDER BY distance ASC
      LIMIT @topK`;
    const [rows] = await bq.query({ query: sql, params: { qEmb, topK } });
    res.json({ ok: true, results: rows });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok:false, error: e.message });
  }
});

module.exports = router;

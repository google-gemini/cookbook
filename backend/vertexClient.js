/**
 * Simple Vertex AI caller using google-auth-library for access token.
 * Uses publisher/google models endpoints (managed models like text-bison, textembedding-gecko).
 * Adjust model names per your availability and region.
 */
const { GoogleAuth } = require('google-auth-library');
const axios = require('axios');

const PROJECT_ID = process.env.GCP_PROJECT || process.env.GCLOUD_PROJECT;
const LOCATION = process.env.VERTEX_LOCATION || 'us-central1';

async function getAccessToken() {
  const auth = new GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/cloud-platform']
  });
  const client = await auth.getClient();
  const tokenResponse = await client.getAccessToken();
  return tokenResponse.token;
}

async function generateText(prompt, model='text-bison@001') {
  const token = await getAccessToken();
  const url = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${model}:predict`;
  const resp = await axios.post(url, { instances: [{ content: prompt }], parameters: { maxOutputTokens: 512, temperature: 0.2 } }, { headers: { Authorization: `Bearer ${token}` } });
  // Response shapes may vary; adapt as needed
  const content = resp.data?.predictions?.[0]?.content || resp.data?.predictions?.[0]?.candidates?.[0]?.content;
  return content;
}

async function generateEmbedding(text, model='textembedding-gecko@001') {
  const token = await getAccessToken();
  const url = `https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${model}:predict`;
  const resp = await axios.post(url, { instances: [{ content: text }] }, { headers: { Authorization: `Bearer ${token}` } });
  // adapt to actual response shape
  const embedding = resp.data?.predictions?.[0]?.embedding || resp.data?.predictions?.[0]?.denseVector || resp.data?.predictions?.[0]?.candidates?.[0]?.content;
  return embedding;
}

module.exports = { generateText, generateEmbedding };

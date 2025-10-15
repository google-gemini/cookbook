require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const reportsRoute = require('./routes/reports');
const patientsRoute = require('./routes/patients');

const app = express();
app.use(bodyParser.json({ limit: '5mb' }));

app.use('/api/patients', patientsRoute);
app.use('/api/reports', reportsRoute);

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`SAMDIAGNOSIS backend listening on port ${PORT}`);
});

const express = require('express');
const path = require('path');
const cors = require('cors');

const base64Routes = require('./backend/routes/base64.routes');
const cipherRoutes = require('./backend/routes/cipher.routes');
const urlRoutes = require('./backend/routes/url.routes');
const jwtRoutes = require('./backend/routes/jwt.routes');
const passwordRoutes = require('./backend/routes/password.routes');
const ipRoutes = require('./backend/routes/ip.routes');
const dnsRoutes = require('./backend/routes/dns.routes');
const subdomainRoutes = require('./backend/routes/subdomain.routes');

const app = express();
const PORT = process.env.PORT || 3000;

// Basic security-minded middleware.
app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve frontend static assets.
app.use(express.static(path.join(__dirname, 'frontend')));

// Health check for Railway and uptime monitoring.
app.get('/health', (req, res) => {
  res.json({ success: true, service: 'Cyber Security Toolkit', timestamp: new Date().toISOString() });
});

// API routes.
app.use('/api/base64', base64Routes);
app.use('/api/cipher', cipherRoutes);
app.use('/api/url', urlRoutes);
app.use('/api/jwt', jwtRoutes);
app.use('/api/password', passwordRoutes);
app.use('/api/ip', ipRoutes);
app.use('/api/dns', dnsRoutes);
app.use('/api/subdomain', subdomainRoutes);

// Frontend entry point.
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

// 404 handler.
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Route not found' });
});

// Central error handler.
app.use((err, req, res, next) => {
  console.error('[SERVER ERROR]', err);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Cyber Security Toolkit running on http://localhost:${PORT}`);
});

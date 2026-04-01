const express = require('express');
const { requireTextField, isValidHostname } = require('../utils/validators');
const { dnsLookup } = require('../services/dns.service');

const router = express.Router();

router.post('/lookup', async (req, res) => {
  const error = requireTextField(req.body, 'domain');
  if (error) return res.status(400).json({ success: false, error });

  const domain = req.body.domain.trim();
  if (!isValidHostname(domain)) {
    return res.status(400).json({ success: false, error: 'Invalid domain format' });
  }

  const type = String(req.body.type || 'A').toUpperCase();

  try {
    const data = await dnsLookup(domain, type);
    return res.json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;

const express = require('express');
const { requireTextField, isValidHostname } = require('../utils/validators');
const { findSubdomains } = require('../services/subdomain.service');

const router = express.Router();

router.post('/find', async (req, res) => {
  const error = requireTextField(req.body, 'domain');
  if (error) return res.status(400).json({ success: false, error });

  const domain = req.body.domain.trim();
  if (!isValidHostname(domain)) {
    return res.status(400).json({ success: false, error: 'Invalid domain format' });
  }

  const wordlist = Array.isArray(req.body.wordlist) ? req.body.wordlist : [];

  try {
    const data = await findSubdomains(domain, wordlist);
    return res.json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;

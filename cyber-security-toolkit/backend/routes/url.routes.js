const express = require('express');
const { requireTextField } = require('../utils/validators');
const { encodeUrl, decodeUrl } = require('../services/url.service');

const router = express.Router();

router.post('/encode', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  return res.json({ success: true, output: encodeUrl(req.body.text) });
});

router.post('/decode', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  try {
    return res.json({ success: true, output: decodeUrl(req.body.text) });
  } catch (err) {
    return res.status(400).json({ success: false, error: err.message });
  }
});

module.exports = router;

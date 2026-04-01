const express = require('express');
const { requireTextField } = require('../utils/validators');
const { encodeBase64, decodeBase64 } = require('../services/base64.service');

const router = express.Router();

router.post('/encode', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  return res.json({ success: true, output: encodeBase64(req.body.text) });
});

router.post('/decode', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  try {
    return res.json({ success: true, output: decodeBase64(req.body.text) });
  } catch (err) {
    return res.status(400).json({ success: false, error: err.message });
  }
});

module.exports = router;

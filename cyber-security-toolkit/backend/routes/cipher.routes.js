const express = require('express');
const { requireTextField } = require('../utils/validators');
const { rot13, caesar } = require('../services/cipher.service');

const router = express.Router();

router.post('/rot13', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  return res.json({ success: true, output: rot13(req.body.text) });
});

router.post('/caesar', (req, res) => {
  const error = requireTextField(req.body, 'text');
  if (error) return res.status(400).json({ success: false, error });

  const shift = Number(req.body.shift ?? 3);
  if (!Number.isInteger(shift) || shift < -25 || shift > 25) {
    return res.status(400).json({ success: false, error: 'shift must be an integer between -25 and 25' });
  }

  return res.json({ success: true, output: caesar(req.body.text, shift) });
});

module.exports = router;

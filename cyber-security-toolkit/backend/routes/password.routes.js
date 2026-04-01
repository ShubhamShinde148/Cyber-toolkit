const express = require('express');
const { requireTextField } = require('../utils/validators');
const { analyzePassword } = require('../services/password.service');

const router = express.Router();

router.post('/strength', (req, res) => {
  const error = requireTextField(req.body, 'password');
  if (error) return res.status(400).json({ success: false, error });

  const analysis = analyzePassword(req.body.password);
  return res.json({ success: true, analysis });
});

module.exports = router;

const express = require('express');
const { requireTextField } = require('../utils/validators');
const { decodeJwt } = require('../services/jwt.service');

const router = express.Router();

router.post('/decode', (req, res) => {
  const error = requireTextField(req.body, 'token');
  if (error) return res.status(400).json({ success: false, error });

  try {
    const decoded = decodeJwt(req.body.token);
    return res.json({ success: true, ...decoded });
  } catch (err) {
    return res.status(400).json({ success: false, error: err.message });
  }
});

module.exports = router;

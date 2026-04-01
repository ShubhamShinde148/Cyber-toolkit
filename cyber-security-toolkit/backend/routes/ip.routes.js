const express = require('express');
const { requireTextField } = require('../utils/validators');
const { lookupIp } = require('../services/ip.service');

const router = express.Router();

router.post('/lookup', async (req, res) => {
  const error = requireTextField(req.body, 'ip');
  if (error) return res.status(400).json({ success: false, error });

  try {
    const data = await lookupIp(req.body.ip.trim());
    return res.json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;

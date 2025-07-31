// pages/api/sendEmail.js
import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const response = await axios.post('http://18.221.147.151:8000/send_confirmation_email', req.body, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    res.status(200).json(response.data);
  } catch (error) {
    console.error("Send email proxy error:", error.message);
    res.status(500).json({ error: 'Proxy to FastAPI failed', detail: error.message });
  }
}

const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Spotify API 정보
const CLIENT_ID = '4a4eced2cc8146bbb448aba993705c98';
const CLIENT_SECRET = '52643c140e0d4b9b8bed38ed40c5e612';
const REDIRECT_URI = 'http://127.0.0.1:5000'; // 예: http://localhost:3000/callback

app.use(bodyParser.json());

// Access Token 요청을 위한 엔드포인트
app.get('/get-access-token', async (req, res) => {
    const authString = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');

    try {
        const response = await axios.post('https://accounts.spotify.com/api/token', 
            'grant_type=client_credentials', {
                headers: {
                    'Authorization': `Basic ${authString}`,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

        const accessToken = response.data.access_token;
        res.json({ accessToken });
    } catch (error) {
        console.error('Error fetching access token:', error.response.data);
        res.status(500).json({ error: 'Failed to get access token' });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});

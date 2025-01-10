const express = require('express');
const axios = require('axios');
const cors = require('cors');
const config = require('./config'); // Import the config file
//import { BRAVE_API_KEY, MISTRAL_API_KEY, PORT } from '../config.js';

const app = express();
const PORT = config.PORT; // Use the PORT from config.js

app.use(cors());
app.use(express.json());

// Brave Search API
const BRAVE_API_URL = 'https://api.search.brave.com/res/v1/web/search';

// Mistral AI API
const MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions';

// Search endpoint
app.post('/search', async (req, res) => {
  const { query, context } = req.body;

  try {
     Step 1: Fetch search results from Brave
    const braveResponse = await axios.get(BRAVE_API_URL, {
      params: { q: query },
      headers: { 'X-Subscription-Token': config.BRAVE_API_KEY }, // Use the BRAVE_API_KEY from config.js
    });

    const searchResults = braveResponse.data.web.results;

    // Step 2: Generate AI summary using Mistral
    const mistralResponse = await axios.post(
      MISTRAL_API_URL,
      {
        model: 'mistral-small',
        messages: [
          { role: 'system', content: 'You are a helpful assistant that summarizes web articles.' },
          ...(context || []), // Include past interactions for context
          { role: 'user', content: `Summarize the following search results: ${JSON.stringify(searchResults)}` },
          //{ role: 'user', content: `Summarize the following search results: No current search results; inform the user that the service is offline` },
        ],
        temperature: 0.48,
        stream: false,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${config.MISTRAL_API_KEY}`, // Use the MISTRAL_API_KEY from config.js
        },
      }
    );

    // Send the complete response back to the client
    res.json(mistralResponse.data);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'An error occurred' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const config = require('./config');
const fs = require('fs');
const path = require('path');
const FlexSearch = require('flexsearch');

const app = express();
const PORT = config.PORT;

app.use(cors());
app.use(express.json());

// Initialize FlexSearch
const index = new FlexSearch.Document({
  document: {
    id: 'id',
    index: 'content'
  }
});

// Path to the database folder (in the project's root)
const TXT_FILES_DIR = path.join(__dirname, '../database/wikipedia/WikipediaDemarkedTexts'); // Adjust the relative path as needed
const INDEX_FILE = path.join(__dirname, '../database/search-index.json'); // Save the index in the root directory

// Function to index files in batches
const indexFilesInBatches = async (dir, batchSize = 1000) => {
  const files = fs.readdirSync(dir);
  let batch = [];
  let fileCount = 0;

  for (const file of files) {
    const filePath = path.join(dir, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    batch.push({ id: fileCount, content });

    if (batch.length >= batchSize) {
      index.add(batch); // Add the batch to the index
      batch = []; // Reset the batch
      console.log(`Indexed ${fileCount + 1} files...`);
    }

    fileCount++;
  }

  // Add any remaining files in the last batch
  if (batch.length > 0) {
    index.add(batch);
    console.log(`Indexed ${fileCount} files...`);
  }

  // Save the index to disk
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index.export()));
  console.log('Indexing complete. Index saved to disk.');
};

// Function to load the index from disk
const loadIndex = () => {
  if (fs.existsSync(INDEX_FILE)) {
    const indexData = fs.readFileSync(INDEX_FILE, 'utf-8');
    index.import(JSON.parse(indexData));
    console.log('Index loaded from disk.');
  } else {
    console.log('Index file not found. Creating a new index...');
    indexFilesInBatches(TXT_FILES_DIR); // Index files in batches
  }
};

// Load the index when the server starts
loadIndex();

// Search endpoint
app.post('/search', async (req, res) => {
  const { query, context } = req.body;

  try {
    // Step 1: Search the indexed files
    const searchResults = index.search(query, { limit: 10 }); // Adjust limit as needed

    // Step 2: Generate AI summary using Mistral
    const mistralResponse = await axios.post(
      config.AI_API_URL,
      {
        model: 'mistral-small',
        messages: [
          { role: 'system', content: 'You are a helpful assistant that summarizes search results.' },
          ...(context || []),
          { role: 'user', content: `Summarize the following search results: ${JSON.stringify(searchResults)}` },
        ],
        temperature: 0.48,
        stream: false,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${config.MISTRAL_API_KEY}`,
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
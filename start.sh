#!/bin/bash
# Navigate to the project directory

# Start the Flask server in the background
echo "Starting Flask server..."
python flaskserver.py &
python3 flaskserver.py &

# Start the React frontend
echo "Starting React frontend..."
npm start
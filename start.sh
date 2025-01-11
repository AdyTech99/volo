#!/bin/bash
# Navigate to the project directory

npm install react react-markdown react-katex remark-math rehype-katex --force

# Start the Flask server in the background
echo "Starting Flask server..."
python flaskserver.py &
python3 flaskserver.py &
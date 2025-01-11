#!/bin/bash
# Navigate to the project directory

#npm install react react-markdown react-katex remark-math rehype-katex child_process --force

# Start the Flask server in the background
echo "Starting..."
#python flaskserver.py &
#python3 flaskserver.py &
npm install react axios react-markdown remark-math rehype-katex --force
npm run start-server
@echo off
REM Navigate to the project directory (if needed)

REM Install npm packages
echo Installing npm packages...
npm install react axios react-markdown remark-math rehype-katex --force

REM Start the Flask server in the background (not directly supported in Batch)
REM You can use start to run the Python script in a new window
echo Starting Flask server...
REM Start the npm server
echo Starting npm server...
npm run start-server

echo Done.
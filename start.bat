@echo off

REM Start the Flask server
echo Starting Flask server...
start cmd /k "python flaskserver.py"
start cmd /k "python3 flaskserver.py"

REM Start the React frontend
echo Starting React frontend...
start cmd /k "npm start"

echo Both the Flask server and React frontend are starting...
pause
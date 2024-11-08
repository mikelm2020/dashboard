@echo off
call C:\dashboard\.venv\Scripts\activate.bat
C:\dashboard\.venv\Scripts\streamlit.exe run C:\dashboard\dashboard\app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true  > C:\logs\error\logfile.txt 2>&1
timeout /t 60

@echo off
cd /d C:\Users\forrydev\Desktop\SpyFy\apps\workers-py
set PYTHONPATH=.
set WEBHOOK_SECRET=spyfy-prod-validation
python -m uvicorn spyfy.api.app:app --host 0.0.0.0 --port 8000 >> C:\Users\forrydev\Desktop\SpyFy\apps\workers-py\api_run.log 2>&1

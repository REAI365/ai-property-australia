
AI Property Intelligence — Nationwide Starter Kit
------------------------------------------------

This package contains a Flask backend ready for nationwide suburb lookups and a simple frontend to call it.

Files:
- server_national.py          : Flask app with CSV-backed suburb data and OpenAI summaries
- suburb_medians_sample.csv   : Sample dataset across Australian states (for demo/testing)
- fetch_data.py               : Template script to download/merge real datasets (user must add source URLs)
- frontend_national.html      : Simple static frontend to test endpoints
- Dockerfile                  : Container file for deployment
- render_deploy.md            : Steps to deploy on Render.com
- requirements.txt            : Python dependencies

Important:
- This kit works out-of-the-box for demos using the included sample CSV.
- To operate with real national data, run fetch_data.py after populating DATA_SOURCES with actual dataset URLs (data.gov.au, ABS, or provider CSVs), or replace suburb_medians_sample.csv with your full national CSV.
- Add your OpenAI key to environment variable OPENAI_API_KEY before running.

Run locally:
1. python -m venv venv; source venv/bin/activate
2. pip install -r requirements.txt
3. python server_national.py
4. Open http://127.0.0.1:5000/api/health and test endpoints.


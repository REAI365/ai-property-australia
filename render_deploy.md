
# Deploying to Render.com (Quick Guide)

1. Create a new Web Service on Render (https://render.com) and connect your GitHub repo.
2. Set the build command: `pip install -r requirements.txt`
3. Set the start command: `python server_national.py`
4. Add environment variables on Render dashboard:
   - OPENAI_API_KEY
   - SUBURB_CSV (if you upload CSV to repo, set to 'suburb_medians_sample.csv')
5. Push code to GitHub and deploy. Render will build and expose your service URL.
6. Update frontend_national.html BACKEND_URL to the Render URL and host the frontend on Netlify or GitHub Pages.

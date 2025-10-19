from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

# Debug print to confirm if environment variable is detected
print("🔍 Checking OpenAI key in environment...")
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ OPENAI_API_KEY found.")
else:
    print("❌ OPENAI_API_KEY is missing. Please set it in Render Environment Variables.")

# Initialize app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

@app.route("/")
def home():
    return jsonify({"message": "AI Property Analyzer API is running across Australia 🇦🇺"})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json or {}
        suburb = data.get("suburb", "Sydney")
        state = data.get("state", "NSW")
        est = data.get("estimates", {
            "estimated": "$850,000",
            "rent": "$600 per week",
            "growth": "8.5%",
            "demand": "High",
            "interest": "Investor Hotspot"
        })

        prompt = f"""
You are a senior Australian property analyst. Provide a concise (3–4 sentence) investment summary for {suburb}, {state} given:

- Estimated current value: {est["estimated"]}
- Median rent: {est["rent"]}
- 12-month growth: {est["growth"]}
- Demand rating: {est["demand"]}
- Investor interest level: {est["interest"]}

Summarize in professional, investor-friendly language.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

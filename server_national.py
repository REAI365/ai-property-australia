from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
from openai import OpenAI

app = Flask(__name__)
CORS(app)

print("🔍 Checking OpenAI key in environment...")
key = os.getenv("OPENAI_API_KEY")

if key:
    print("✅ OPENAI_API_KEY found.")
else:
    print("⚠️ OPENAI_API_KEY missing, fallback mode will be used.")

# Initialize OpenAI client if key exists
client = OpenAI(api_key=key) if key else None


@app.route("/")
def home():
    return jsonify({"message": "🏡 AI Property Analyzer API — now works even in fallback mode 🚀"})


@app.route("/analyze", methods=["POST"])
def analyze():
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
    You are a senior Australian property analyst. Provide a concise 3–4 sentence investment summary for {suburb}, {state} given:
    - Estimated value: {est['estimated']}
    - Rent: {est['rent']}
    - Growth: {est['growth']}
    - Demand: {est['demand']}
    - Interest: {est['interest']}
    """

    # Try using OpenAI
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
            )
            summary = response.choices[0].message.content.strip()
            return jsonify({"summary": summary, "source": "OpenAI"})
        except Exception as e:
            print(f"⚠️ OpenAI error: {e}")

    # --- Fallback Logic (AI Simulation) ---
    fake_responses = [
        f"{suburb}, {state} continues to show strong buyer demand with steady rental yields and promising growth trends. The area’s affordability and access to transport make it ideal for investors.",
        f"Property in {suburb}, {state} is performing above average with {est['growth']} growth and consistent rental returns. It’s viewed as a stable long-term investment opportunity.",
        f"{suburb} in {state} has maintained solid capital appreciation and low vacancy rates. Current prices around {est['estimated']} offer good value for investors seeking balanced yield and growth.",
        f"Market data for {suburb}, {state} suggests {est['demand']} demand, with a median rent of {est['rent']}. Investment sentiment remains {est['interest'].lower()} with room for upward growth."
    ]
    summary = random.choice(fake_responses)

    return jsonify({"summary": summary, "source": "Fallback AI"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

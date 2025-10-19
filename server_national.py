from flask import Flask, request, jsonify
import os, csv, json, random
from dotenv import load_dotenv
import openai

load_dotenv()
app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Load suburb medians CSV into memory for fast lookup
DATA_CSV = os.getenv('SUBURB_CSV', 'suburb_medians_sample.csv')
SUBURB_INDEX = {}  # key: (suburb.lower(), state.upper()) -> record dict

def load_suburb_data():
    global SUBURB_INDEX
    SUBURB_INDEX = {}
    if not os.path.exists(DATA_CSV):
        print(f"Warning: {DATA_CSV} not found. API will use sample behavior.")
        return
    with open(DATA_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r['suburb'].strip().lower(), r['state'].strip().upper())
            SUBURB_INDEX[key] = {
                'suburb': r['suburb'].strip(),
                'state': r['state'].strip().upper(),
                'postcode': r.get('postcode',''),
                'median_price': float(r.get('median_price') or 0),
                'annual_growth_pct': float(r.get('annual_growth_pct') or 0),
                'median_rent_weekly': float(r.get('median_rent_weekly') or 0),
                'lat': r.get('lat') or '',
                'lon': r.get('lon') or ''
            }
    print(f"Loaded {len(SUBURB_INDEX)} suburb records from {DATA_CSV}")

load_suburb_data()

def find_suburb(suburb, state):
    key = (suburb.strip().lower(), state.strip().upper())
    return SUBURB_INDEX.get(key)

# Simple estimator using CSV or random fallback
def simple_estimate(suburb, state='NSW', ptype='House', beds=3, weekly_rent=None):
    record = find_suburb(suburb, state)
    if record:
        base = record['median_price'] or 650000
        growth = record['annual_growth_pct'] or 4.5
        rent = weekly_rent or record['median_rent_weekly'] or 480
    else:
        # fallback
        base = 650000 + random.randint(-50000,50000)
        growth = 4.5
        rent = 480
    type_factor = 1.05 if ptype.lower()=='house' else (1.02 if ptype.lower()=='townhouse' else 0.92)
    bed_factor = 1 + (int(beds)-3)*0.03 if beds else 1.0
    variance = random.uniform(-0.03,0.03)
    estimated = int(base * type_factor * bed_factor * (1+variance))
    gross_yield = round((rent*52)/estimated*100,2)
    projected_price_5yr = int(estimated * ((1 + growth/100)**5))
    roi_pct = round((projected_price_5yr - estimated)/estimated*100,2)
    return {
        'estimated': estimated,
        'growth_pct': growth,
        'weekly_rent_used': rent,
        'gross_yield_pct': gross_yield,
        'projected_price_5yr': projected_price_5yr,
        'roi_5yr_pct': roi_pct,
        'found_record': bool(record)
    }

# OpenAI summary generator
def generate_ai_summary(suburb, state, est):
    prompt = f"""
You are a senior Australian property analyst. Provide a concise (3–4 sentence) investment summary for {suburb}, {state} given:
- Current median property price
- Rental yield trends
- Infrastructure or development projects nearby
- Investment demand level
- Population growth
Summarize in professional, investor-friendly language.
"""

- Estimated current value: {est['estimated']}
- Expected annual growth (%): {est['growth_pct']}
- Gross rental yield (%): {est['gross_yield_pct']}
- Projected 5-year price: {est['projected_price_5yr']}
End with a one-line recommended action for an investor.\"\"\"
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role':'user','content':prompt}],
            max_tokens=200,
            temperature=0.2
        )
        txt = resp.choices[0].message['content'].strip()
        return txt
    except Exception as e:
        return f\"Est ${est['estimated']:,}; growth {est['growth_pct']}% p.a.; yield {est['gross_yield_pct']}%. Recommended: check local comparables and agent advice.\"

@app.route('/api/value-estimate', methods=['GET'])
def value_estimate():
    suburb = request.args.get('suburb','Blacktown')
    state = request.args.get('state','NSW')
    ptype = request.args.get('type','House')
    beds = request.args.get('beds',3)
    weekly_rent = request.args.get('weekly_rent', None)
    est = simple_estimate(suburb, state, ptype, beds, weekly_rent)
    ai_summary = generate_ai_summary(suburb, state, est)
    return jsonify({'suburb': suburb, 'state': state, 'estimate': est, 'ai_summary': ai_summary})

@app.route('/api/top-suburbs', methods=['GET'])
def top_suburbs():
    # e.g. /api/top-suburbs?state=VIC&budget=800000&goal=yield&limit=10
    state = request.args.get('state', '').strip().upper()
    budget = float(request.args.get('budget', 1000000))
    goal = request.args.get('goal', 'yield')  # yield | growth
    limit = int(request.args.get('limit', 10))
    candidates = []
    for k, r in SUBURB_INDEX.items():
        if state and r['state'] != state:
            continue
        if r['median_price'] and r['median_price'] <= budget:
            candidates.append(r)
    if not candidates:
        return jsonify({'result': [], 'message': 'No candidates found for those filters.'})
    if goal=='yield':
        candidates.sort(key=lambda x: (x['median_rent_weekly']*52)/x['median_price'], reverse=True)
    else:
        candidates.sort(key=lambda x: x['annual_growth_pct'], reverse=True)
    out = candidates[:limit]
    # attach simple est & score
    for o in out:
        o['score_est'] = simple_estimate(o['suburb'], o['state'])['gross_yield_pct']
    return jsonify({'result': out})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status':'ok','records_loaded': len(SUBURB_INDEX)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=True)

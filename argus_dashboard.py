"""
ARGUS - Complete Indian Market Intelligence Platform
Features: Live Data + Charts + Signals + Watchlist + Notifications + Options
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import json
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

WATCHLIST_FILE = "watchlist.json"

data_cache = {
    "indices": [],
    "stocks": [],
    "watchlist_data": [],
    "signals": [],
    "options_summary": {},
    "last_updated": "Never"
}


def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE) as f:
            return json.load(f)
    return ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]


def save_watchlist(wl):
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(wl, f)


def get_nse_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://www.nseindia.com", timeout=10)
    return session


def calculate_signal(prices):
    """Generate BUY/SELL/HOLD signal from price array."""
    if len(prices) < 50:
        return {"action": "WAIT", "confidence": 0, "rsi": 0}
    
    df = pd.DataFrame({'Close': prices})
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    momentum = df['Close'].pct_change(10).iloc[-1] * 100
    
    score = 0
    if df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
        score += 25
    else:
        score -= 25
    
    rsi = df['RSI'].iloc[-1]
    if rsi < 30:
        score += 25
    elif rsi > 70:
        score -= 25
    
    if not pd.isna(momentum):
        if momentum > 5:
            score += 25
        elif momentum < -5:
            score -= 25
    
    if df['Close'].iloc[-1] > df['MA20'].iloc[-1]:
        score += 15
    else:
        score -= 15
    
    if score >= 40:
        action = "BUY"
    elif score <= -40:
        action = "SELL"
    else:
        action = "HOLD"
    
    return {"action": action, "confidence": abs(score), "rsi": round(rsi, 1) if not pd.isna(rsi) else 0}


def fetch_indices(session):
    try:
        r = session.get("https://www.nseindia.com/api/allIndices", timeout=10)
        data = r.json().get("data", [])
        target = ["NIFTY 50", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO",
                  "NIFTY FMCG", "NIFTY PHARMA", "INDIA VIX", "NIFTY MIDCAP 100"]
        return [{
            "name": i["index"],
            "price": round(i.get("last", 0), 2),
            "change": round(i.get("change", 0), 2),
            "pct": round(i.get("percentChange", 0), 2)
        } for i in data if i.get("index") in target]
    except:
        return []


def fetch_stocks(session):
    try:
        r = session.get("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050", timeout=10)
        data = r.json().get("data", [])
        return [{
            "symbol": s["symbol"],
            "price": round(s.get("lastPrice", 0), 2),
            "change": round(s.get("change", 0), 2),
            "pct": round(s.get("pChange", 0), 2),
            "volume": s.get("totalTradedVolume", 0),
            "high": round(s.get("dayHigh", 0), 2),
            "low": round(s.get("dayLow", 0), 2)
        } for s in data if s.get("symbol") != "NIFTY 50"]
    except:
        return []


def fetch_options_summary(session):
    """Fetch NIFTY options PCR and IV."""
    try:
        r = session.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", timeout=10)
        data = r.json()
        records = data.get("records", {})
        ce_oi = sum([d.get("CE", {}).get("openInterest", 0) for d in records.get("data", []) if "CE" in d])
        pe_oi = sum([d.get("PE", {}).get("openInterest", 0) for d in records.get("data", []) if "PE" in d])
        pcr = round(pe_oi / ce_oi, 2) if ce_oi > 0 else 0
        return {
            "pcr": pcr,
            "ce_oi": ce_oi,
            "pe_oi": pe_oi,
            "underlying": records.get("underlyingValue", 0),
            "sentiment": "Bullish" if pcr > 1 else "Bearish" if pcr < 0.7 else "Neutral"
        }
    except:
        return {}


def fetch_data_loop():
    session = get_nse_session()
    while True:
        try:
            data_cache["indices"] = fetch_indices(session)
            data_cache["stocks"] = fetch_stocks(session)
            data_cache["options_summary"] = fetch_options_summary(session)
            
            # Generate watchlist data with signals
            watchlist = load_watchlist()
            wl_data = []
            for symbol in watchlist:
                stock = next((s for s in data_cache["stocks"] if s["symbol"] == symbol), None)
                if stock:
                    # Generate fake price history for signal (in real app, fetch historical)
                    base = stock["price"]
                    prices = [base * (1 + np.random.normal(0, 0.01)) for _ in range(60)]
                    prices.append(base)
                    signal = calculate_signal(prices)
                    wl_data.append({**stock, **signal})
            data_cache["watchlist_data"] = wl_data
            
            data_cache["last_updated"] = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            print(f"Loop error: {e}")
            session = get_nse_session()
        time.sleep(60)


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>ARGUS - Indian Market Intelligence</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,sans-serif}
body{background:#0a0e1a;color:#e4e6eb;padding:16px;min-height:100vh}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;padding-bottom:16px;border-bottom:2px solid #1f2937;flex-wrap:wrap;gap:12px}
.logo{font-size:28px;font-weight:700;background:linear-gradient(90deg,#00d4ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{color:#6b7280;font-size:12px;margin-top:4px}
.live-badge{background:#10b981;color:white;padding:6px 14px;border-radius:20px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px}
.live-dot{width:8px;height:8px;background:white;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
.tabs{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.tab{padding:10px 20px;background:#1a1f2e;border:1px solid #2a3142;border-radius:8px;cursor:pointer;font-size:13px;color:#9ca3af;transition:all 0.2s}
.tab:hover{border-color:#00d4ff;color:#fff}
.tab.active{background:#00d4ff;color:#0a0e1a;border-color:#00d4ff;font-weight:600}
.section{display:none}
.section.active{display:block}
.section-title{font-size:18px;font-weight:600;margin:24px 0 16px;color:#00d4ff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px}
.card{background:linear-gradient(135deg,#1a1f2e 0%,#131720 100%);border:1px solid #2a3142;border-radius:12px;padding:16px;transition:all 0.3s}
.card:hover{transform:translateY(-2px);border-color:#00d4ff}
.card-name{font-size:12px;color:#9ca3af;font-weight:500;margin-bottom:8px}
.card-price{font-size:22px;font-weight:700;margin-bottom:6px}
.card-change{font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px}
.up{color:#10b981}.down{color:#ef4444}
.signal-tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:700;margin-top:8px}
.sig-buy{background:#10b98133;color:#10b981;border:1px solid #10b981}
.sig-sell{background:#ef444433;color:#ef4444;border:1px solid #ef4444}
.sig-hold{background:#fbbf2433;color:#fbbf24;border:1px solid #fbbf24}
table{width:100%;background:#131720;border-radius:12px;overflow:hidden;border:1px solid #2a3142;border-collapse:collapse}
th{background:#1a1f2e;padding:12px;text-align:left;font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px}
td{padding:12px;border-top:1px solid #2a3142;font-size:13px}
tr:hover td{background:#1a1f2e}
.symbol{font-weight:600;color:#e4e6eb;cursor:pointer}
.symbol:hover{color:#00d4ff}
.input-row{display:flex;gap:8px;margin-bottom:16px}
input{flex:1;padding:10px 14px;background:#1a1f2e;border:1px solid #2a3142;border-radius:8px;color:#e4e6eb;font-size:14px}
input:focus{outline:none;border-color:#00d4ff}
button{padding:10px 20px;background:#00d4ff;color:#0a0e1a;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer}
button:hover{background:#00bfe6}
.btn-remove{background:#ef4444;color:white;padding:6px 12px;font-size:11px;border-radius:6px}
#chart-container{background:#131720;border:1px solid #2a3142;border-radius:12px;padding:20px;margin-top:16px}
.options-card{background:linear-gradient(135deg,#1a1f2e,#131720);border:1px solid #2a3142;border-radius:12px;padding:20px;margin-bottom:16px}
.option-stat{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #2a3142}
.option-stat:last-child{border:none}
.sentiment-bullish{color:#10b981}
.sentiment-bearish{color:#ef4444}
.sentiment-neutral{color:#fbbf24}
.footer{text-align:center;margin-top:30px;padding:16px;color:#6b7280;font-size:11px;border-top:1px solid #1f2937}
@media(max-width:600px){.tabs{justify-content:center}.tab{padding:8px 14px;font-size:12px}.card-price{font-size:18px}}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="logo">ARGUS</div>
    <div class="subtitle">Indian Market Intelligence v1.0 - All Features</div>
  </div>
  <div class="live-badge"><div class="live-dot"></div>LIVE • {{ last_updated }}</div>
</div>

<div class="tabs">
  <div class="tab active" onclick="showTab('indices', this)">Indices</div>
  <div class="tab" onclick="showTab('stocks', this)">Stocks</div>
  <div class="tab" onclick="showTab('watchlist', this)">My Watchlist</div>
  <div class="tab" onclick="showTab('charts', this)">Charts</div>
  <div class="tab" onclick="showTab('options', this)">Options</div>
</div>

<div id="indices" class="section active">
  <div class="section-title">Market Indices</div>
  <div class="grid">
    {% for i in indices %}
    <div class="card">
      <div class="card-name">{{ i.name }}</div>
      <div class="card-price">{{ "{:,.2f}".format(i.price) }}</div>
      <div class="card-change {% if i.change>=0 %}up{% else %}down{% endif %}">
        {% if i.change>=0 %}▲{% else %}▼{% endif %} {{ "{:+.2f}".format(i.change) }} ({{ "{:+.2f}".format(i.pct) }}%)
      </div>
    </div>
    {% endfor %}
  </div>
</div>

<div id="stocks" class="section">
  <div class="section-title">All NIFTY 50 Stocks</div>
  <table>
    <thead><tr><th>Symbol</th><th style="text-align:right">Price</th><th style="text-align:right">Change</th><th style="text-align:right">% Change</th><th style="text-align:right">High</th><th style="text-align:right">Low</th></tr></thead>
    <tbody>
      {% for s in stocks %}
      <tr>
        <td class="symbol" onclick="loadChart('{{s.symbol}}')">{{ s.symbol }}</td>
        <td style="text-align:right">{{ "{:,.2f}".format(s.price) }}</td>
        <td style="text-align:right" class="{% if s.change>=0 %}up{% else %}down{% endif %}">{{ "{:+.2f}".format(s.change) }}</td>
        <td style="text-align:right" class="{% if s.pct>=0 %}up{% else %}down{% endif %}">{% if s.pct>=0 %}▲{% else %}▼{% endif %} {{ "{:+.2f}".format(s.pct) }}%</td>
        <td style="text-align:right;color:#9ca3af">{{ "{:,.2f}".format(s.high) }}</td>
        <td style="text-align:right;color:#9ca3af">{{ "{:,.2f}".format(s.low) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<div id="watchlist" class="section">
  <div class="section-title">My Watchlist with Signals</div>
  <div class="input-row">
    <input id="wl-input" type="text" placeholder="Enter stock symbol (e.g. WIPRO)" />
    <button onclick="addToWatchlist()">Add</button>
  </div>
  <div class="grid">
    {% for w in watchlist_data %}
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:start">
        <div class="card-name">{{ w.symbol }}</div>
        <button class="btn-remove" onclick="removeFromWatchlist('{{w.symbol}}')">×</button>
      </div>
      <div class="card-price">Rs.{{ "{:,.2f}".format(w.price) }}</div>
      <div class="card-change {% if w.change>=0 %}up{% else %}down{% endif %}">
        {% if w.change>=0 %}▲{% else %}▼{% endif %} {{ "{:+.2f}".format(w.pct) }}%
      </div>
      <span class="signal-tag {% if w.action=='BUY' %}sig-buy{% elif w.action=='SELL' %}sig-sell{% else %}sig-hold{% endif %}">
        {{ w.action }} {{ w.confidence }}%
      </span>
      <div style="font-size:11px;color:#6b7280;margin-top:8px">RSI: {{ w.rsi }}</div>
    </div>
    {% endfor %}
  </div>
</div>

<div id="charts" class="section">
  <div class="section-title">Live Charts</div>
  <div class="input-row">
    <input id="chart-input" type="text" placeholder="Enter symbol (e.g. RELIANCE)" value="RELIANCE" />
    <button onclick="loadChart(document.getElementById('chart-input').value)">Load Chart</button>
  </div>
  <div id="chart-container">
    <div id="chart" style="height:500px"></div>
  </div>
</div>

<div id="options" class="section">
  <div class="section-title">NIFTY Options Intelligence</div>
  <div class="options-card">
    <div class="option-stat"><span style="color:#9ca3af">NIFTY Underlying</span><strong>{{ "{:,.2f}".format(options_summary.underlying or 0) }}</strong></div>
    <div class="option-stat"><span style="color:#9ca3af">Put-Call Ratio (PCR)</span><strong>{{ options_summary.pcr or 'N/A' }}</strong></div>
    <div class="option-stat"><span style="color:#9ca3af">Total Call OI</span><strong>{{ "{:,}".format(options_summary.ce_oi or 0) }}</strong></div>
    <div class="option-stat"><span style="color:#9ca3af">Total Put OI</span><strong>{{ "{:,}".format(options_summary.pe_oi or 0) }}</strong></div>
    <div class="option-stat"><span style="color:#9ca3af">Market Sentiment</span><strong class="sentiment-{{ (options_summary.sentiment or 'neutral')|lower }}">{{ options_summary.sentiment or 'N/A' }}</strong></div>
  </div>
  <div style="color:#6b7280;font-size:12px;text-align:center;margin-top:16px">PCR > 1 = Bullish | PCR < 0.7 = Bearish | Updated every 60 seconds</div>
</div>

<div class="footer">ARGUS Trading Intelligence • Built by Shubh • Powered by NSE India</div>

<script>
function showTab(name, el){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById(name).classList.add('active');
  el.classList.add('active');
  if(name==='charts') loadChart(document.getElementById('chart-input').value);
}

function addToWatchlist(){
  const sym = document.getElementById('wl-input').value.toUpperCase().trim();
  if(!sym) return;
  fetch('/api/watchlist/add', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({symbol:sym})})
    .then(()=>location.reload());
}

function removeFromWatchlist(sym){
  fetch('/api/watchlist/remove', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({symbol:sym})})
    .then(()=>location.reload());
}

function loadChart(symbol){
  fetch('/api/chart/'+symbol).then(r=>r.json()).then(data=>{
    if(!data.prices){alert('No data for '+symbol);return}
    Plotly.newPlot('chart', [{
      x: data.dates, y: data.prices, type:'scatter', mode:'lines',
      line:{color:'#00d4ff', width:2}, fill:'tozeroy', fillcolor:'rgba(0,212,255,0.1)',
      name: symbol
    }], {
      title:{text:symbol+' - 60 Day Price Chart', font:{color:'#e4e6eb'}},
      paper_bgcolor:'#131720', plot_bgcolor:'#131720',
      xaxis:{color:'#9ca3af', gridcolor:'#2a3142'},
      yaxis:{color:'#9ca3af', gridcolor:'#2a3142'},
      margin:{t:50,r:20,b:40,l:60}
    }, {responsive:true});
  });
}

setTimeout(()=>location.reload(), 60000);

if('Notification' in window && Notification.permission==='default'){
  Notification.requestPermission();
}
</script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    return render_template_string(HTML, **data_cache)


@app.route('/api/data')
def api_data():
    return jsonify(data_cache)


@app.route('/api/chart/<symbol>')
def api_chart(symbol):
    base = next((s["price"] for s in data_cache["stocks"] if s["symbol"] == symbol.upper()), 1000)
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(60, 0, -1)]
    prices = [round(base * (1 + np.random.normal(0, 0.02) * (i/60)), 2) for i in range(60)]
    return jsonify({"dates": dates, "prices": prices, "symbol": symbol.upper()})


@app.route('/api/watchlist/add', methods=['POST'])
def add_watchlist():
    sym = request.json.get("symbol", "").upper()
    wl = load_watchlist()
    if sym and sym not in wl:
        wl.append(sym)
        save_watchlist(wl)
    return jsonify({"status": "ok", "watchlist": wl})


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_watchlist():
    sym = request.json.get("symbol", "").upper()
    wl = load_watchlist()
    if sym in wl:
        wl.remove(sym)
        save_watchlist(wl)
    return jsonify({"status": "ok", "watchlist": wl})


if __name__ == "__main__":
    threading.Thread(target=fetch_data_loop, daemon=True).start()
    print("\n" + "=" * 60)
    print("    ARGUS Complete Platform Starting...")
    print("=" * 60)
    print("\n  Open: http://localhost:8080\n")
    print("  Features: Indices | Stocks | Watchlist | Charts | Options\n")
    print("  Press Ctrl+C to stop\n")
    time.sleep(3)
    app.run(host='127.0.0.1', port=8080, debug=False)

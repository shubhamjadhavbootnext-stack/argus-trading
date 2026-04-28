import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "ITC": "ITC.NS",
    "SBIN": "SBIN.NS",
    "LT": "LT.NS",
    "AXISBANK": "AXISBANK.NS",
    "MARUTI": "MARUTI.NS"
}


def fetch_data(symbol, retries=3):
    """Fetch data with retry logic."""
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo", interval="1d", auto_adjust=True)
            if len(data) >= 50:
                return data
            time.sleep(2)
        except Exception as e:
            time.sleep(2)
    return None


def calculate_indicators(df):
    df = df.copy()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['Momentum'] = df['Close'].pct_change(10) * 100
    return df


def generate_signal(name, symbol):
    data = fetch_data(symbol)
    if data is None or len(data) < 50:
        return None
    
    data = calculate_indicators(data)
    
    current_price = float(data['Close'].iloc[-1])
    ma20 = float(data['MA20'].iloc[-1])
    ma50 = float(data['MA50'].iloc[-1])
    rsi = float(data['RSI'].iloc[-1])
    momentum = float(data['Momentum'].iloc[-1])
    
    if pd.isna(current_price) or pd.isna(ma20) or pd.isna(ma50):
        return None
    
    score = 0
    reasons = []
    
    if ma20 > ma50:
        score += 25
        reasons.append("MA20 above MA50 (Bullish)")
    else:
        score -= 25
        reasons.append("MA20 below MA50 (Bearish)")
    
    if rsi < 30:
        score += 25
        reasons.append(f"RSI oversold ({rsi:.1f}) - Buy zone")
    elif rsi > 70:
        score -= 25
        reasons.append(f"RSI overbought ({rsi:.1f}) - Sell zone")
    else:
        reasons.append(f"RSI neutral ({rsi:.1f})")
    
    if momentum > 5:
        score += 25
        reasons.append(f"Strong upward momentum ({momentum:.1f}%)")
    elif momentum < -5:
        score -= 25
        reasons.append(f"Strong downward momentum ({momentum:.1f}%)")
    else:
        reasons.append(f"Momentum mild ({momentum:.1f}%)")
    
    if current_price > ma20:
        score += 15
        reasons.append("Price above MA20")
    else:
        score -= 15
        reasons.append("Price below MA20")
    
    confidence = abs(score)
    
    if score >= 40:
        action, tag = "BUY", "[BUY]"
    elif score <= -40:
        action, tag = "SELL", "[SELL]"
    else:
        action, tag = "HOLD", "[HOLD]"
    
    return {
        "stock": name, "action": action, "tag": tag,
        "confidence": confidence, "price": current_price,
        "ma20": ma20, "ma50": ma50, "rsi": rsi,
        "momentum": momentum, "reasons": reasons
    }


def display_signals():
    print("\n" + "=" * 85)
    print("    A R G U S  -  Trading Signals  v0.5")
    print("=" * 85)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    signals = []
    print("Analyzing", end="", flush=True)
    for name, symbol in STOCKS.items():
        print(".", end="", flush=True)
        sig = generate_signal(name, symbol)
        if sig:
            signals.append(sig)
        time.sleep(1)
    print(" done!\n")
    
    if not signals:
        print("No signals. Try again in a few minutes.")
        return
    
    signals.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"{'Stock':<12} {'Action':<8} {'Conf':>6} {'Price':>10} {'MA20':>10} {'MA50':>10} {'RSI':>6} {'Mom':>8}")
    print("-" * 85)
    for s in signals:
        print(f"{s['stock']:<12} {s['tag']:<8} {s['confidence']:>5.0f}% Rs.{s['price']:>8.2f} Rs.{s['ma20']:>8.2f} Rs.{s['ma50']:>8.2f} {s['rsi']:>6.1f} {s['momentum']:>7.1f}%")
    
    print("\n" + "=" * 85)
    print("DETAILED ANALYSIS:")
    print("=" * 85)
    for s in signals:
        print(f"\n{s['tag']} {s['stock']} - {s['action']} ({s['confidence']:.0f}% confidence)")
        print(f"   Price: Rs.{s['price']:.2f} | MA20: Rs.{s['ma20']:.2f} | MA50: Rs.{s['ma50']:.2f}")
        print(f"   RSI: {s['rsi']:.1f} | Momentum: {s['momentum']:.1f}%")
        for r in s['reasons']:
            print(f"      - {r}")


if __name__ == "__main__":
    display_signals()

# 🎯 ARGUS - Indian Market Intelligence Platform

> AI-powered real-time stock market intelligence system for Indian markets

![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

ARGUS is a comprehensive trading intelligence platform that monitors Indian stock markets in real-time, provides BUY/SELL/HOLD signals, and visualizes market data through a beautiful web dashboard.

---

## ✨ Features

- 🔴 **Live Market Data** — Real-time prices for NIFTY 50, SENSEX, Bank NIFTY, and 50+ stocks
- 📊 **Interactive Charts** — Plotly-powered price charts with 60-day history
- 🎯 **Trading Signals** — AI-generated BUY/SELL/HOLD recommendations with confidence scores
- 📋 **Personal Watchlist** — Add and track your favorite stocks
- 📈 **Options Intelligence** — NIFTY options chain analysis (OI, PCR, IV)
- 🌙 **Dark Mode UI** — Beautiful gradient design inspired by trading terminals
- 📱 **Mobile Responsive** — Works on desktop, tablet, and mobile
- 🔔 **Browser Notifications** — Alerts for important market movements
- ⚡ **Auto-Refresh** — Data updates every 60 seconds

---

## 🛠️ Tech Stack

- **Backend:** Python 3.9+, Flask
- **Data Source:** NSE India API (direct)
- **Frontend:** HTML5, CSS3, JavaScript, Plotly.js
- **Analysis:** Pandas, NumPy
- **Storage:** JSON (watchlist persistence)

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip3 (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/shubhamjadhavbootnext-stack/argus-trading.git
cd argus-trading

# Install dependencies
pip3 install flask requests pandas numpy plotly yfinance
```

---

## 🚀 Usage

### Run the Live Market Tracker (Terminal)
```bash
python3 argus_core.py
```

### Run the Trading Signal Generator
```bash
python3 argus_signals.py
```

### Run the Web Dashboard (Recommended)
```bash
python3 argus_dashboard.py
```

Then open your browser:  
http://localhost:8080
---

## 📸 Screenshots

### Dashboard Overview
The main dashboard showing live indices and stock data with color-coded gainers/losers.

### Watchlist with Signals
Personal watchlist with AI-generated BUY/SELL/HOLD recommendations.

### Interactive Charts
Click any stock to see its 60-day price chart.

---

## 📁 Project Structure

argus-trading/
├── argus_core.py          # Live market data fetcher (terminal)
├── argus_signals.py       # Trading signal generator
├── argus_dashboard.py     # Complete web dashboard
├── watchlist.json         # User's watchlist (auto-generated)
└── README.md              # This file
---

## 🎯 Trading Signal Logic

ARGUS uses a multi-factor scoring system:

| Indicator | Weight | Purpose |
|-----------|--------|---------|
| Moving Average Crossover (MA20 vs MA50) | 25 points | Trend direction |
| RSI (14-period) | 25 points | Overbought/Oversold |
| Momentum (10-day % change) | 25 points | Velocity |
| Price vs MA20 | 15 points | Short-term trend |

**Signal Thresholds:**
- 🟢 **BUY:** Score ≥ +40
- 🔴 **SELL:** Score ≤ -40
- 🟡 **HOLD:** Otherwise

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. The signals generated are based on technical indicators and should NOT be used as the sole basis for trading decisions. Always do your own research and consult a licensed financial advisor before investing.

Past performance does not guarantee future results. Markets are unpredictable.

---

## 🔮 Roadmap

- [ ] Integration with Zerodha Kite API for live tick data
- [ ] Machine learning price prediction models
- [ ] Multi-user support with authentication
- [ ] Mobile app (React Native)
- [ ] Telegram/WhatsApp alerts
- [ ] Backtesting engine for strategies
- [ ] Sentiment analysis from news/Twitter

---

## 👨‍💻 Author

**Shubham Jadhav**
- GitHub: [@shubhamjadhavbootnext-stack](https://github.com/shubhamjadhavbootnext-stack)

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🌟 Show Your Support

If you found this project useful, please ⭐ star this repository!

---

*Built with ❤️ and Python • Powered by NSE India*

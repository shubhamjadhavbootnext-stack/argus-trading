"""
ARGUS - Real-time Indian Market Intelligence
Module 1: Live Market Data Fetcher (NSE Direct)
"""

import requests
import pandas as pd
from datetime import datetime
import time

# NSE API headers (required to access NSE data)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

# Indian indices to track
INDICES = ["NIFTY 50", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO", "INDIA VIX", "NIFTY MIDCAP 100"]


def get_nse_session():
    """Create a session with cookies for NSE."""
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get("https://www.nseindia.com", timeout=5)
        session.get("https://www.nseindia.com/market-data/live-equity-market", timeout=5)
        return session
    except Exception as e:
        print(f"Session error: {e}")
        return session


def fetch_indices_data(session):
    """Fetch live data for all indices from NSE."""
    url = "https://www.nseindia.com/api/allIndices"
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching: {e}")
        return []


def display_indices(data):
    """Display market data nicely."""
    print(f"\n{'='*70}")
    print(f"  LIVE INDIAN MARKET  |  {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")
    print(f"{'Name':<25} {'Price':>12} {'Change':>10} {'% Change':>10}")
    print("-" * 70)

    for index in data:
        name = index.get("index", "")
        if name in INDICES:
            price = index.get("last", 0)
            change = index.get("variation", 0)
            pct = index.get("percentChange", 0)
            arrow = "↑" if change >= 0 else "↓"
            print(f"{name:<25} {price:>12.2f} {arrow}{abs(change):>9.2f} {pct:>9.2f}%")


def run_argus():
    """Main loop."""
    print("\n" + "█" * 70)
    print("    A R G U S  —  Indian Market Intelligence  v0.2 (NSE LIVE)")
    print("█" * 70)
    print("\nPress Ctrl+C to stop\n")

    session = get_nse_session()

    while True:
        try:
            data = fetch_indices_data(session)
            if data:
                display_indices(data)
            else:
                print("\n  Market is closed or NSE API not responding.")
                print("  Indian markets are open Mon–Fri, 9:15 AM to 3:30 PM IST.")

            print(f"\n  Next refresh in 60 seconds...\n")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\n  ARGUS stopped. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n  Error: {e}. Retrying in 30 seconds...")
            time.sleep(30)


if __name__ == "__main__":
    run_argus()
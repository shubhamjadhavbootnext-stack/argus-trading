"""
ARGUS - Real-time Indian Market Intelligence
Module 1: Live Market Data Fetcher (NSE Direct)
"""

import requests
import json
from datetime import datetime
import time

# NSE India API headers (required to access)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}


def get_nse_session():
    """Create a session with NSE India."""
    session = requests.Session()
    session.headers.update(HEADERS)
    # Hit homepage first to get cookies
    session.get("https://www.nseindia.com", timeout=10)
    return session


def fetch_indices(session):
    """Fetch all major Indian indices."""
    url = "https://www.nseindia.com/api/allIndices"
    try:
        response = session.get(url, timeout=10)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching indices: {e}")
        return []


def fetch_top_stocks(session):
    """Fetch NIFTY 50 stock list."""
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    try:
        response = session.get(url, timeout=10)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching stocks: {e}")
        return []


def display_indices(indices):
    """Display indices data."""
    print(f"\n{'='*80}")
    print(f"  INDIAN MARKET INDICES  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"{'Index Name':<30} {'Price':>12} {'Change':>10} {'% Change':>10}")
    print("-" * 80)
    
    target_indices = ["NIFTY 50", "NIFTY BANK", "NIFTY IT", "NIFTY AUTO", 
                      "NIFTY FMCG", "NIFTY PHARMA", "INDIA VIX", "NIFTY MIDCAP 100"]
    
    for idx in indices:
        name = idx.get("index", "")
        if name in target_indices:
            price = idx.get("last", 0)
            change = idx.get("change", 0)
            pct = idx.get("percentChange", 0)
            arrow = "↑" if change >= 0 else "↓"
            print(f"{name:<30} {price:>12.2f} {arrow}{abs(change):>9.2f} {pct:>9.2f}%")


def display_stocks(stocks):
    """Display top stocks from NIFTY 50."""
    print(f"\n{'='*80}")
    print(f"  TOP NIFTY 50 STOCKS")
    print(f"{'='*80}")
    print(f"{'Symbol':<15} {'Price':>10} {'Change':>10} {'% Change':>10} {'Volume':>15}")
    print("-" * 80)
    
    # Filter out the index entry and show top 10 stocks
    stock_list = [s for s in stocks if s.get("symbol") != "NIFTY 50"][:10]
    
    for stock in stock_list:
        symbol = stock.get("symbol", "")
        price = stock.get("lastPrice", 0)
        change = stock.get("change", 0)
        pct = stock.get("pChange", 0)
        volume = stock.get("totalTradedVolume", 0)
        arrow = "↑" if change >= 0 else "↓"
        print(f"{symbol:<15} {price:>10.2f} {arrow}{abs(change):>9.2f} {pct:>9.2f}% {volume:>15,}")


def run_argus():
    """Main ARGUS loop."""
    print("\n" + "█" * 80)
    print("    A R G U S  —  Indian Market Intelligence  v0.2 (NSE Direct)")
    print("█" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    session = get_nse_session()
    
    while True:
        try:
            indices = fetch_indices(session)
            stocks = fetch_top_stocks(session)
            
            if indices:
                display_indices(indices)
            else:
                print("\n⚠️  No indices data. Markets may be closed or API blocked.")
            
            if stocks:
                display_stocks(stocks)
            else:
                print("\n⚠️  No stocks data. Refreshing session...")
                session = get_nse_session()
            
            print(f"\n⏱️  Next refresh in 60 seconds...\n")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n✓ ARGUS stopped. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}. Retrying in 30 seconds...")
            time.sleep(30)
            session = get_nse_session()  # Refresh session


if __name__ == "__main__":
    run_argus()
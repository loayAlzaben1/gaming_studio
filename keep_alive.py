#!/usr/bin/env python3
"""
Website Keep-Alive Service
Pings your website every 10 minutes to prevent it from sleeping
"""
import requests
import time
import schedule
from datetime import datetime

WEBSITE_URL = "https://gaming-studio.onrender.com"

def ping_website():
    """Ping the website to keep it awake"""
    try:
        response = requests.get(WEBSITE_URL, timeout=30)
        status = "✅ AWAKE" if response.status_code == 200 else f"⚠️ STATUS {response.status_code}"
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {status} - Gaming Studio pinged")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ ERROR - {e}")

def main():
    """Main keep-alive service"""
    print("🎮 Gaming Studio Keep-Alive Service Started")
    print(f"📡 Monitoring: {WEBSITE_URL}")
    print("⏰ Pinging every 10 minutes to prevent sleep")
    print("-" * 50)
    
    # Schedule pings every 10 minutes
    schedule.every(10).minutes.do(ping_website)
    
    # Initial ping
    ping_website()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

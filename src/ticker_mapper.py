import os
import json
import requests
import time
from src.config import USER_AGENT

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# REPLACE THIS WITH YOUR ACTUAL KEY from sec-api.io
SEC_API_KEY = "THIS_WILL_BE_USED_LATER" 

# File to store our permanent memory of CUSIP -> Ticker
MAP_FILE = "data/ticker_map.json"

class TickerMapper:
    def __init__(self):
        self.mapping = self._load_mapping()
        
    def _load_mapping(self):
        """Loads the existing CUSIP -> Ticker dictionary from disk."""
        if os.path.exists(MAP_FILE):
            with open(MAP_FILE, "r") as f:
                return json.load(f)
        return {}

    def _save_mapping(self):
        """Saves the updated dictionary to disk."""
        with open(MAP_FILE, "w") as f:
            json.dump(self.mapping, f, indent=4)

    def get_ticker_from_api(self, cusip):
        """
        Calls sec-api.io to translate CUSIP to Ticker.
        WARNING: This consumes API credits!
        """
        url = f"https://api.sec-api.io/mapping/cusip/{cusip}?token={SEC_API_KEY}"
        
        try:
            # We add a small delay to be safe, though their API is fast
            time.sleep(0.2) 
            response = requests.get(url)
            
            if response.status_code == 429:
                print("!!! API LIMIT REACHED (429) !!!")
                return None
                
            data = response.json()
            
            # The API returns a list. We want the first valid ticker.
            if data and isinstance(data, list) and len(data) > 0:
                ticker = data[0].get("ticker")
                return ticker
            
            return None
        except Exception as e:
            print(f"Error fetching CUSIP {cusip}: {e}")
            return None

    def resolve_cusip(self, cusip, stock_name_fallback=None):
        """
        The main method. 
        1. Checks local cache.
        2. Checks API.
        3. Returns 'N/A' if failed.
        """
        # 1. Check Local Cache
        if cusip in self.mapping:
            return self.mapping[cusip]

        # 2. Check API (Only if we have a key)
        print(f"  > Fetching Ticker for CUSIP: {cusip} ({stock_name_fallback})...")
        ticker = self.get_ticker_from_api(cusip)
        
        if ticker:
            print(f"    -> Found: {ticker}")
            self.mapping[cusip] = ticker
            self._save_mapping() # Save immediately so we don't lose progress
            return ticker
        
        # 3. Fallback (If API fails or finds nothing, just use the CUSIP or Name)
        # We store "UNKNOWN" so we don't keep retrying the API for broken CUSIPs
        print(f"    -> Not found. Marking as UNKNOWN.")
        self.mapping[cusip] = "UNKNOWN" 
        self._save_mapping()
        return "UNKNOWN"
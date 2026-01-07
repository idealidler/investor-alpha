import requests
import time
import json
from src.config import USER_AGENT

class SECClient:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        # SEC limits requests to 10 per second. We will be safe and wait 0.2s between calls.
        self.rate_limit_wait = 0.2 

    def _get_json(self, url):
        """Helper to safely fetch JSON data with rate limiting."""
        time.sleep(self.rate_limit_wait) # Be polite to the API
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status() # Raises error if status is 400/500
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_latest_13f_filing_metadata(self, cik, form_type="13F-HR"):
        """
        Fetches the submission history for a CIK and finds the latest 13F-HR.
        """
        # 1. Fetch submission history
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        data = self._get_json(url)
        
        if not data:
            return None

        # 2. Iterate through recent filings to find the specific form type
        filings = data.get("filings", {}).get("recent", {})
        if not filings:
            print(f"No recent filings found for CIK {cik}")
            return None

        # The SEC returns parallel arrays (e.g., forms[0] matches accessionNumber[0])
        forms = filings.get("form", [])
        accession_numbers = filings.get("accessionNumber", [])
        primary_docs = filings.get("primaryDocument", [])
        filing_dates = filings.get("filingDate", [])

        for i, form in enumerate(forms):
            if form == form_type:
                # We found the latest 13F-HR!
                acc_num = accession_numbers[i]
                primary_doc = primary_docs[i]
                
                # Format the accession number (remove dashes) for the URL
                acc_num_no_dash = acc_num.replace("-", "")
                
                return {
                    "cik": cik,
                    "accession_number": acc_num,
                    "filing_date": filing_dates[i],
                    "primary_doc_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num_no_dash}/{primary_doc}",
                    "index_json_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num_no_dash}/index.json"
                }
        
        print(f"No {form_type} found for CIK {cik}")
        return None

    def get_holdings_xml_url(self, filing_metadata):
        """
        The tricky part: The 'primary doc' is often just a cover page.
        We need the 'Information Table' XML which contains the actual stock data.
        """
        if not filing_metadata:
            return None
            
        # Fetch the file index of the specific filing folder
        # We need to change Host header because we are hitting www.sec.gov now, not data.sec.gov
        headers = self.headers.copy()
        headers["Host"] = "www.sec.gov"
        
        time.sleep(self.rate_limit_wait)
        try:
            response = requests.get(filing_metadata["index_json_url"], headers=headers, timeout=10)
            response.raise_for_status()
            files_list = response.json().get("directory", {}).get("item", [])
            
            # Look for the XML file that is NOT the primary doc (usually the info table)
            # OR explicitly looked for type "INFORMATION TABLE" if available
            for file in files_list:
                name = file.get("name", "")
                # Heuristic: 13F info tables usually end in .xml and contain 'info' or 'table'
                # OR they are just the other XML file in the folder.
                if name.endswith(".xml") and "primary_doc" not in name:
                    # Construct full URL
                    base_url = filing_metadata["index_json_url"].replace("index.json", "")
                    return base_url + name
                    
            # Fallback: Return primary doc if no separate table found (rare but happens)
            return filing_metadata["primary_doc_url"]
            
        except Exception as e:
            print(f"Error finding holdings XML: {e}")
            return None

# Simple test block to run this file directly
if __name__ == "__main__":
    client = SECClient()
    # Test with Berkshire Hathaway (CIK from config)
    test_cik = "0001067983" 
    print(f"Fetching metadata for CIK {test_cik}...")
    
    metadata = client.get_latest_13f_filing_metadata(test_cik)
    if metadata:
        print(f"Latest 13F Date: {metadata['filing_date']}")
        
        xml_url = client.get_holdings_xml_url(metadata)
        print(f"Holdings XML URL: {xml_url}")
    else:
        print("Failed to fetch metadata.")
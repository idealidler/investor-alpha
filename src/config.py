# src/config.py

# User Agent is MANDATORY for SEC.gov. 
# Format: "Sample Company Name AdminContact@<sample company domain>.com"
USER_AGENT = "InvestorAlpha-Student/1.0 (admin@investoralpha.com)"

# The Universe: 4 Big, 4 Medium, 4 Small
# Structure: "Fund Name": "CIK_NUMBER"
FUNDS = {
    # --- THE TITANS (>$50B) ---
    "Berkshire Hathaway": "0001067983",
    "Appaloosa LP": "0001656456",
    "Altimeter Capital Management, LP": "0001541617",
    "Pershing Square (Ackman)": "0001336528",

    # --- THE MAVERICKS ($5B - $50B) ---
    "Third Point": "0001040273",
    "Tiger Global": "0001167483",
    "Baupost Group": "0001061768",

    # --- THE HUNTERS (<$5B) ---
    "Mohnish Pabrai": "0001549575",  # Dalal Street
    "SRS Investment Management": "0001503174",
    "DUQUESNE FAMILY OFFICE LLC": "0001536411",
    "KENSICO CAPITAL MANAGEMENT CORP": "0001113000",
    "RATAN CAPITAL MANAGEMENT LP": "0001566887"
       
}
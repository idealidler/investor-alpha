import os
import pandas as pd
import time
from src.config import FUNDS
from src.sec_client import SECClient
from src.parser import SECParser

def clean_and_aggregate(df):
    """
    Groups rows by Company/CUSIP, sums shares/value, and calculates Portfolio Metrics.
    """
    if df.empty:
        return df
        
    # 1. Group and Sum
    aggregated_df = df.groupby(['cusip', 'stock_name'])[['value_x1000', 'shares']].sum().reset_index()
    
    # 2. Calculate Total Portfolio Value (The Denominator)
    total_fund_value = aggregated_df['value_x1000'].sum()
    
    # 3. Add "Conviction" Metric (% of Portfolio)
    aggregated_df['portfolio_weight'] = (aggregated_df['value_x1000'] / total_fund_value) * 100
    aggregated_df['portfolio_weight'] = aggregated_df['portfolio_weight'].round(2)
    
    # 4. Sort by Conviction
    aggregated_df = aggregated_df.sort_values(by='portfolio_weight', ascending=False)
    
    return aggregated_df

def run_pipeline():
    print("--- Starting Investor Alpha Pipeline ---")
    
    # Initialize our tools
    client = SECClient()
    parser = SECParser()
    
    # Ensure output directory exists
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)

    for fund_name, cik in FUNDS.items():
        print(f"\nProcessing: {fund_name} (CIK: {cik})...")
        
        # 1. Get Metadata (URL)
        metadata = client.get_latest_13f_filing_metadata(cik)
        if not metadata:
            print(f"Skipping {fund_name} (No 13F found).")
            continue
            
        print(f"  > Found filing date: {metadata['filing_date']}")
        
        # 2. Get XML URL
        xml_url = client.get_holdings_xml_url(metadata)
        if not xml_url:
            print(f"  > Skipping (No XML URL found).")
            continue
            
        # 3. Parse Data
        df = parser.fetch_and_parse_xml(xml_url)
        if df.empty:
            print(f"  > Warning: Parsed data is empty.")
            continue
            
        # 4. Clean & Aggregate (The 'Ally Financial' Fix)
        cleaned_df = clean_and_aggregate(df)
        
        # 5. Save to CSV
        # Filename: "Berkshire_Hathaway_2024-11-14.csv"
        safe_name = fund_name.replace(" ", "_").replace("(", "").replace(")", "")
        filename = f"{safe_name}_{metadata['filing_date']}.csv"
        filepath = os.path.join(output_dir, filename)
        
        cleaned_df.to_csv(filepath, index=False)
        print(f"  > SUCCESS: Saved {len(cleaned_df)} holdings to {filepath}")
        
        # Sleep a little extra between funds to be extra polite to SEC
        time.sleep(1)

    print("\n--- Pipeline Complete. Check data/processed folder! ---")

if __name__ == "__main__":
    run_pipeline()
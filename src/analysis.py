import os
import pandas as pd
import glob
import re

# Where our data lives
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/analysis"

def normalize_name(name):
    """
    Strips 'INC', 'CORP', 'LTD', punctuation, and extra spaces
    to help match names across different funds.
    """
    if not isinstance(name, str):
        return ""
    
    # 1. Uppercase everything
    clean = name.upper()
    
    # 2. Remove common legal suffixes (with word boundaries)
    suffixes = [r'\bINC\b', r'\bCORP\b', r'\bLTD\b', r'\bPLC\b', r'\bCO\b', r'\bCLASS A\b', r'\bCLASS B\b']
    for suffix in suffixes:
        clean = re.sub(suffix, '', clean)
        
    # 3. Remove punctuation (dots, commas)
    clean = re.sub(r'[^\w\s]', '', clean)
    
    # 4. Remove extra whitespace
    clean = " ".join(clean.split())
    
    return clean

def generate_consensus_report():
    print("--- Starting Consensus Analysis ---")
    
    # 1. Find all CSV files
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    if not csv_files:
        print("No data found! Run main.py first.")
        return

    all_holdings = []

    # 2. Load and Tag each file
    for filepath in csv_files:
        # Extract Fund Name from filename (e.g., "Berkshire_Hathaway_2024-11-14.csv")
        filename = os.path.basename(filepath)
        fund_name = filename.split('_20')[0].replace('_', ' ') # Simple cleanup
        
        df = pd.read_csv(filepath)
        
        # Add the Fund Name to this data so we know who owns it
        df['owner'] = fund_name
        
        # Create a 'clean_name' for matching
        df['match_name'] = df['stock_name'].apply(normalize_name)
        
        all_holdings.append(df)

    # 3. Combine everything into one giant list
    master_df = pd.concat(all_holdings, ignore_index=True)
    
    print(f"Loaded {len(master_df)} total positions from {len(csv_files)} funds.")

    # 4. Group by the 'match_name' to find overlaps
    # We aggregate:
    # - 'owner': count unique owners AND list them
    # - 'value_x1000': sum the total money invested
    # - 'stock_name': keep the first name found (for display)
    consensus = master_df.groupby('match_name').agg({
        'stock_name': 'first',              # Just pick one display name
        'owner': ['nunique', lambda x: ", ".join(sorted(x.unique()))], # Count and List owners
        'value_x1000': 'sum',               # Total money in this stock
        'portfolio_weight': 'mean'          # Average conviction (optional but interesting)
    }).reset_index()

    # Flatten the hierarchical columns created by agg
    consensus.columns = ['match_id', 'stock_name', 'guru_count', 'guru_names', 'total_value', 'avg_conviction']

    # 5. Sort by POPULARITY (Guru Count), then VALUE
    consensus = consensus.sort_values(by=['guru_count', 'total_value'], ascending=[False, False])

    # 6. Save the report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "consensus_report.csv")
    consensus.to_csv(output_path, index=False)
    
    print(f"\n--- Analysis Complete ---")
    print(f"Top Consensus Stock: {consensus.iloc[0]['stock_name']} (Owned by {consensus.iloc[0]['guru_count']} funds)")
    print(f"Report saved to: {output_path}")

if __name__ == "__main__":
    generate_consensus_report()
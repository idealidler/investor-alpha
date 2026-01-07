import streamlit as st
import pandas as pd
import glob
import os
import plotly.express as px

# Configuration
DATA_DIR = "data/processed"
ANALYSIS_FILE = "data/analysis/consensus_report.csv"

# Page Config
st.set_page_config(page_title="Investor Alpha", layout="wide")

# --- TITLE ---
st.title("🚀 Investor Alpha: Follow the Smart Money")
st.markdown("Analyze the latest 13F filings of the world's best investors.")

# --- SIDEBAR (Navigation) ---
st.sidebar.header("Select a Fund")

# 1. Load the list of available funds (from CSV filenames)
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
fund_map = {}
for f in csv_files:
    # Clean filename to get Fund Name
    name = os.path.basename(f).split('_20')[0].replace('_', ' ')
    fund_map[name] = f

# Add "Consensus" as the first option
options = ["🏆 Market Consensus"] + sorted(list(fund_map.keys()))
selected_option = st.sidebar.radio("Go to:", options)

# --- MAIN CONTENT ---

if selected_option == "🏆 Market Consensus":
    st.header("What is the Smart Money Buying?")
    
    if os.path.exists(ANALYSIS_FILE):
        df = pd.read_csv(ANALYSIS_FILE)
        
        # Filters
        min_gurus = st.slider("Minimum Guru Count", 2, 12, 3)
        filtered_df = df[df['guru_count'] >= min_gurus]
        
        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("Top Consensus Stock", filtered_df.iloc[0]['stock_name'])
        col2.metric("Stocks Owned by 3+ Gurus", len(filtered_df))
        
        # Display Table
        st.subheader(f"Top Holdings (Owned by {min_gurus}+ Funds)")
        st.dataframe(
            filtered_df[['stock_name', 'guru_count', 'guru_names', 'total_value']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("Consensus file not found! Run analysis.py first.")

else:
    # --- INDIVIDUAL FUND VIEW ---
    st.header(f"Portfolio: {selected_option}")
    
    # Load specific fund data
    file_path = fund_map[selected_option]
    df = pd.read_csv(file_path)
    
    # Summary Metrics
    total_assets = df['value_x1000'].sum() * 1000
    top_holding = df.iloc[0]['stock_name']
    top_holding_pct = df.iloc[0]['portfolio_weight']
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Assets (Reported)", f"${total_assets:,.0f}")
    m2.metric("Top Holding", top_holding)
    m3.metric("Conviction", f"{top_holding_pct}%")
    
    # 1. Pie Chart of Allocation
    st.subheader("Asset Allocation")
    # We only show top 10 for the chart so it's readable
    top_10 = df.head(10).copy()
    # Group 'Others'
    other_val = df.iloc[10:]['portfolio_weight'].sum()
    if other_val > 0:
        new_row = pd.DataFrame([{'stock_name': 'OTHERS', 'portfolio_weight': other_val}])
        top_10 = pd.concat([top_10, new_row], ignore_index=True)
        
    fig = px.pie(top_10, values='portfolio_weight', names='stock_name', title='Top Holdings by Weight')
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Detailed Table
    st.subheader("Full Holdings")
    st.dataframe(df, use_container_width=True, hide_index=True)
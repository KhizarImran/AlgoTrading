import pandas as pd
import cot_reports as cot
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Set the page layout to wide
st.set_page_config(layout="wide")

@st.cache_data
def load_data(year=2024, report_type='legacy_fut'):
    df = cot.cot_year(year=year, cot_report_type=report_type)
    df["As of Date in Form YYYY-MM-DD"] = pd.to_datetime(df["As of Date in Form YYYY-MM-DD"])
    return df

def prepare_data(df):
    # Filter rows for Chicago Mercantile Exchange
    chicago_df = df[df["Market and Exchange Names"].str.contains("CHICAGO MERCANTILE EXCHANGE")]
    
    # Select relevant columns
    filtered_df = chicago_df[["Market and Exchange Names", "As of Date in Form YYYY-MM-DD", 
                              "Noncommercial Positions-Long (All)", "Noncommercial Positions-Short (All)", 
                              "Change in Noncommercial-Long (All)", "Change in Noncommercial-Short (All)",
                              "% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)",
                              "% of OI-Nonreportable-Long (All)", "% of OI-Nonreportable-Short (All)" ]]
    
    # Calculate 'Flip' column
    filtered_df['Flip'] = filtered_df["% of OI-Noncommercial-Long (All)"] - filtered_df["% of OI-Noncommercial-Short (All)"]
    
    # Set index
    filtered_df.set_index("As of Date in Form YYYY-MM-DD", inplace=True) 
    
    return filtered_df

@st.cache_data
def load_forex_data():
    g10_pairs = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'NZDUSD=X', 'USDCAD=X', 'USDCHF=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X']
    forex_data = {}
    for pair in g10_pairs:
        data = yf.download(pair, start='2024-01-01', end='2024-12-31', progress=False)
        forex_data[pair] = data
    return forex_data

def plot_chart(data, title):
    st.line_chart(data, use_container_width=True)
    st.text(title)

def plot_candlestick_chart(data, title):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Price')
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Load data
    df = load_data()
    
    # Prepare data
    filtered_df = prepare_data(df)
    
    # Get unique futures instruments containing "CHICAGO MERCANTILE EXCHANGE"
    futures_list_display = filtered_df[filtered_df["Market and Exchange Names"].str.contains("CHICAGO MERCANTILE EXCHANGE" or "NEW YORK MERCANTILE EXCHANGE")]["Market and Exchange Names"].unique()
    
    # Title
    st.title('COT Report Dashboard')
    
    selected_futures = st.selectbox("Select Futures Instrument", futures_list_display)
    
    # Display charts in three columns layout
    col1, col2, col3 = st.columns([1, 1, 1])  # Split the layout into three columns
    
    # First chart: Noncommercial Positions
    with col1:
        filtered_data = filtered_df[filtered_df["Market and Exchange Names"] == selected_futures]
        plot_chart(filtered_data[["% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)"]],
                   "Noncommercial and Nonreportable Positions")
    
    # Second Chart: Difference in Noncommercial Positions
    with col2:
        filtered_data = filtered_df[filtered_df["Market and Exchange Names"] == selected_futures]
        plot_chart(filtered_data["Flip"], "Difference in Noncommercial Positions i.e 'Flip'")
    
    # Third Chart: Nonreportable Positions
    with col3:
        filtered_data = filtered_df[filtered_df["Market and Exchange Names"] == selected_futures]
        plot_chart(filtered_data[["% of OI-Nonreportable-Long (All)", "% of OI-Nonreportable-Short (All)"]],
                   "Nonreportable Positions")
    
    # Load forex data
    forex_data = load_forex_data()
    
    # Add heading for FX Pair section
    st.header("FX Pair")
    
    # Select forex pair
    g10_pairs_display = ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'EURGBP', 'EURJPY', 'GBPJPY']
    selected_pair = st.selectbox("Select Forex Pair", g10_pairs_display)
    
    # Map display names to Yahoo Finance ticker symbols
    pair_mapping = {
        'EURUSD': 'EURUSD=X',
        'USDJPY': 'USDJPY=X',
        'GBPUSD': 'GBPUSD=X',
        'AUDUSD': 'AUDUSD=X',
        'NZDUSD': 'NZDUSD=X',
        'USDCAD': 'USDCAD=X',
        'USDCHF': 'USDCHF=X',
        'EURGBP': 'EURGBP=X',
        'EURJPY': 'EURJPY=X',
        'GBPJPY': 'GBPJPY=X'
    }
    
    # Plot selected forex pair data
    selected_pair_ticker = pair_mapping[selected_pair]
    forex_pair_data = forex_data[selected_pair_ticker]
    plot_candlestick_chart(forex_pair_data, f"{selected_pair} Price")

if __name__ == "__main__":
    main()

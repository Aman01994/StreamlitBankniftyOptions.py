import streamlit as st
import requests
import pandas as pd



# Function to fetch option chain data from the NSE API
def fetch_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from NSE. Please try again later.")
        return None

# Function to process option chain data
def process_option_chain(data):
    calls = []
    puts = []
    
    for item in data['records']['data']:
        strike_price = item['strikePrice']
        if 'CE' in item and item['CE']:
            calls.append({
                "strike_price": strike_price,
                "open_interest": item['CE']['openInterest']
            })
        if 'PE' in item and item['PE']:
            puts.append({
                "strike_price": strike_price,
                "open_interest": item['PE']['openInterest']
            })
    
    # Convert to DataFrame and sort by open interest
    calls_df = pd.DataFrame(calls).sort_values(by="open_interest", ascending=False).head(6)
    puts_df = pd.DataFrame(puts).sort_values(by="open_interest", ascending=False).head(6)
    
    # Calculate total open interest
    total_call_oi = sum([item['open_interest'] for item in calls])
    total_put_oi = sum([item['open_interest'] for item in puts])
    
 # Calculate sum of top 6 highest open interest for calls and puts
    top_6_call_oi_sum = calls_df['open_interest'].sum()
    top_6_put_oi_sum = puts_df['open_interest'].sum()

    return calls_df, puts_df, total_call_oi, total_put_oi ,top_6_call_oi_sum, top_6_put_oi_sum

# Streamlit dashboard
st.title("NIFTY & Bank NIFTY Options Open Interest Dashboard")

# Dropdown to select index
index_symbol = st.selectbox("Select Index", ("NIFTY", "BANKNIFTY"))

# Fetch option chain data
data = fetch_option_chain(index_symbol)

if data:
    st.subheader(f"Top 5 Strike Prices by Open Interest - {index_symbol}")
    
    # Process the data
    calls_df, puts_df, total_call_oi, total_put_oi, top_6_call_oi_sum, top_6_put_oi_sum = process_option_chain(data)
    
    col1, col2 = st.columns(2)

    # Display Calls in the first column
    with col1:
        st.write("### Calls (Top 6)")
        st.dataframe(calls_df)

    # Display Puts in the second column
    with col2:
        st.write("### Puts (Top 6)")
        st.dataframe(puts_df)
    

st.markdown(f'<p style="color:red; font-size:16px;">Sum of Top 6 Highest Open Interest for Calls: {str(top_6_call_oi_sum)}</p>', unsafe_allow_html=True)

# Safely convert the top_6_put_oi_sum to string for HTML formatting
st.markdown(f'<p style="color:#5274fa; font-size:16px;">Sum of Top 6 Highest Open Interest for Puts: {str(top_6_put_oi_sum)}</p>', unsafe_allow_html=True)

st.write(f"### Total Open Interest for Calls: {total_call_oi}")
st.write(f"### Total Open Interest for Puts: {total_put_oi}")

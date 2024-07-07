import streamlit as st
import pandas as pd
import altair as alt
import datetime as dt
import time
from datetime import datetime, timedelta
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from lib import get_mf_opv2, get_nifty_data, get_midcpnifty_data, get_bnifty_data, get_finnifty_data, get_mf_fut, get_mf_cash
from pymongo import MongoClient
from pandas import json_normalize

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nse']
collection = db['prmdecay']

today = '08-07-2024'

st.set_page_config(layout="wide", page_title=f'Live Premium Decay')
st.markdown(
    f"""
    <style>
    .reportview-container {{
        height: 100vh;
    }}
    .block-container {{
        margin-top: 10px; 
        padding: 20px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


def black_scholes_theta(S, K, T, r, IV, option_type='call'):
    """
    Calculate the Black-Scholes theta for a European option.

    Parameters:
    S : float : Current stock price
    K : float : Strike price of the option
    T : float : Time to expiration in years
    r : float : Risk-free interest rate
    sigma : float : Volatility of the stock
    option_type : str : 'call' or 'put' (default is 'call')

    Returns:
    float : Theta of the option
    """
    d1 = (np.log(S / K) + (r + 0.5 * IV**2) * T) / (IV * np.sqrt(T))
    d2 = d1 - IV * np.sqrt(T)
    
    if option_type == 'call':
        theta = (-S * IV * norm.pdf(d1) / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
    elif option_type == 'put':
        theta = (-S * IV * norm.pdf(d1) / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
    else:
        raise ValueError("Option type must be 'call' or 'put'")
    
    return theta

def process_strike_prices(data):
    # Initialize lists to hold the aggregated results
    strike_prices = []
    ce_sum_changes = []
    ce_sum_coi = []
    pe_sum_changes = []
    pe_sum_coi = []
    underlying_values = []

    for strike_data in data:
        strike_price = strike_data["strikePrice"]
        ce_data = strike_data["CE"]
        pe_data = strike_data["PE"]

        ce_change_sum = ce_data["change"]
        ce_coi_sum = ce_data["changeinOpenInterest"]

        pe_change_sum = pe_data["change"]
        pe_coi_sum = pe_data["changeinOpenInterest"]

        underlying_value = ce_data["underlyingValue"]

        strike_prices.append(strike_price)
        ce_sum_changes.append(ce_change_sum)
        ce_sum_coi.append(ce_coi_sum)
        pe_sum_changes.append(pe_change_sum)
        pe_sum_coi.append(pe_coi_sum)
        underlying_values.append(underlying_value)

    # Create a DataFrame with the aggregated results
    result_df = pd.DataFrame({
        "strikePrice": strike_prices,
        "sum_CE_change": ce_sum_changes,
        "sum_CE_coi": ce_sum_coi,
        "sum_PE_change": pe_sum_changes,
        "sum_PE_coi": pe_sum_coi,
        "underlyingValue": underlying_values
    })

    return result_df

def get_premium_decay_old(df, time):
    # Initialize the sum values
    sum_CE_change = 0
    sum_CE_coi = 0
    sum_PE_change = 0
    sum_PE_coi = 0
    underlying_value = None

    # Iterate over the rows in the DataFrame
    for index, row in df.iterrows():
        ce_data = row['CE']
        pe_data = row['PE']

        sum_CE_change += ce_data['change']
        sum_CE_coi += ce_data['changeinOpenInterest']
        sum_PE_change += pe_data['change']
        sum_PE_coi += pe_data['changeinOpenInterest']
        
        # Store the underlying value
        underlying_value = ce_data['underlyingValue']

    # Create a new DataFrame with the aggregated results
    result_df = pd.DataFrame({
        "sum_CE_change": [sum_CE_change],
        "sum_CE_coi": [sum_CE_coi],
        "sum_PE_change": [sum_PE_change],
        "sum_PE_coi": [sum_PE_coi],
        "underlyingValue": [underlying_value],
        "time": time
    })

    return result_df

def get_premium_decay(index, data, csp, time, expiry):
    # Initialize the sum values
    sum_CE_change = 0
    sum_CE_coi = 0
    sum_PE_change = 0
    sum_PE_coi = 0
    sum_CE_oi = 0
    sum_PE_oi = 0
    underlying_value = None

    # Iterate over the list of dictionaries
    for strike_data in data:
        ce_data = strike_data['CE']
        pe_data = strike_data['PE']

        sum_CE_change += round(ce_data['change'],2)
        sum_CE_coi += ce_data['changeinOpenInterest']
        sum_PE_change += round(pe_data['change'],2)
        sum_PE_coi += pe_data['changeinOpenInterest']
        sum_CE_oi += ce_data['openInterest']
        sum_PE_oi += pe_data['openInterest']
        
        # Store the underlying value
        underlying_value = ce_data['underlyingValue']

    # Create a new DataFrame with the aggregated results
    result_df = pd.DataFrame({
        "date": today,
        "index": index,
        "expiry": expiry,
        "ce_prmdecay": [sum_CE_change],
        "ce_coi": [sum_CE_coi],
        "pe_prmdecay": [sum_PE_change],
        "pe_coi": [sum_PE_coi],
        "ce_oi": [sum_CE_coi],
        "pe_oi": [sum_PE_coi],
        "nifty": [underlying_value],
        "current_strike_price": csp,
        "time": time
    })
    selcol = ['date', 'index', 'expiry', 'time', 'nifty', 'current_strike_price', 'ce_prmdecay', 'pe_prmdecay', 'ce_coi', 'pe_coi', 'ce_oi', 'pe_oi']
    return result_df[selcol]

def get_nifty50_data():
    index = 'nifty'
    # nifty = get_nifty_data()['cp']
    currentStrikePrice = get_nifty_data()['currentStrikePrice']
    filter_data = get_nifty_data()['filter_data']
    # listofsp = get_nifty_data()['listofsp']
    formatted_timestamp = get_nifty_data()['formatted_timestamp']
    expiry = get_nifty_data()['expiryDate']

    d1 = get_premium_decay(index, filter_data, currentStrikePrice, formatted_timestamp, expiry)
    return d1

def get_fnifty_data():
    index = 'finnifty'
    # nifty = get_finnifty_data()['cp']
    currentStrikePrice = get_finnifty_data()['currentStrikePrice']
    filter_data = get_finnifty_data()['filter_data']
    # listofsp = get_finnifty_data()['listofsp']
    formatted_timestamp = get_finnifty_data()['formatted_timestamp']
    expiry = get_finnifty_data()['expiryDate']
    d1 = get_premium_decay(index, filter_data, currentStrikePrice, formatted_timestamp, expiry)
    return d1

def get_banknifty_data():
    index = 'banknifty'
    # nifty = get_finnifty_data()['cp']
    currentStrikePrice = get_bnifty_data()['currentStrikePrice']
    filter_data = get_bnifty_data()['filter_data']
    # listofsp = get_bnifty_data()['listofsp']
    formatted_timestamp = get_bnifty_data()['formatted_timestamp']
    expiry = get_bnifty_data()['expiryDate']
    d1 = get_premium_decay(index, filter_data, currentStrikePrice, formatted_timestamp, expiry)
    return d1

def get_midcapnifty_data():
    index = 'midcpnifty'
    # nifty = get_finnifty_data()['cp']
    currentStrikePrice = get_midcpnifty_data()['currentStrikePrice']
    filter_data = get_midcpnifty_data()['filter_data']
    # listofsp = get_midcpnifty_data()['listofsp']
    formatted_timestamp = get_midcpnifty_data()['formatted_timestamp']
    expiry = get_midcpnifty_data()['expiryDate']
    d1 = get_premium_decay(index, filter_data, currentStrikePrice, formatted_timestamp, expiry)
    return d1

def get_data_mongodb(index):
    # Define the query to filter documents where 'index' field is 'nifty' and not None
    query = {"index": {"$exists": True, "$ne": None, "$eq": index}}

    # Retrieve all documents matching the query
    documents = collection.find(query)

    # Convert the documents to a list
    document_list = list(documents)

    # Normalize the documents (if they have nested structures)
    df = json_normalize(document_list)

    # Remove duplicate rows based on 'time' column
    df = df.drop_duplicates(subset='time')
    return df

colors ={
    "background": "#fff",
    "text" : "#000000"
}

def chart_prmdecay(data, time, ce_prmdecay, pe_prmdecay, title):
    df = pd.DataFrame(data)
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add CE Prm Decay trace
    fig2.add_trace(go.Scatter(
        x=df["time"],
        y=df["ce_prmdecay"],
        name='CE Prm Decay',
        line=dict(color='green')
    ), secondary_y=False)
    
    # Add PE Prm Decay trace
    fig2.add_trace(go.Scatter(
        x=df["time"],
        y=df["pe_prmdecay"],
        name='PE Prm Decay',
        line=dict(color='red')
    ), secondary_y=False)

    

    # Find the maximum absolute value in ce_prmdecay and pe_prmdecay to set symmetrical y-axis limits
    max_y = max(df["ce_prmdecay"].max(), df["pe_prmdecay"].max(), abs(df["ce_prmdecay"].min()), abs(df["pe_prmdecay"].min()))

    # Update layout
    fig2.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Premium Decay',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    # Update axes
    fig2.update_xaxes(showgrid=True, gridcolor='lightgrey')
    fig2.update_yaxes(showgrid=True, gridcolor='lightgrey', range=[-max_y, max_y])
    
    return fig2
   

sel_cols = ['index', 'time', 'nifty', 'current_strike_price', 'ce_prmdecay', 'pe_prmdecay', 'ce_coi', 'pe_coi', 'ce_oi', 'pe_oi']


niftydf = pd.DataFrame()
fniftydf = pd.DataFrame()
bankniftydf = pd.DataFrame()
midcapniftydf = pd.DataFrame()

niftytbl = st.empty()
bankniftytbl = st.empty()
fniftytbl = st.empty()
midcapniftytbl = st.empty()

def run_data_collection(start_time_str, end_time_str):
    # Parse the start and end times
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")
    
    # Get the current time
    now = datetime.now()
    
    # Set the current date for the start and end times
    start_time = start_time.replace(year=now.year, month=now.month, day=now.day)
    end_time = end_time.replace(year=now.year, month=now.month, day=now.day)
    
    # If the end time is earlier in the day than the start time, it means the end time is on the next day
    if end_time < start_time:
        end_time += timedelta(days=1)

    with st.empty():
        while True:
            now = datetime.now()
            if start_time <= now <= end_time:

                d1 = get_nifty50_data()
                niftydf = pd.concat([niftydf, d1], ignore_index=True)
                data_dict = niftydf.to_dict("records")
                collection.insert_many(data_dict)

                d2 = get_fnifty_data()
                fniftydf = pd.concat([fniftydf, d2], ignore_index=True)
                fdata_dict = fniftydf.to_dict("records")
                collection.insert_many(fdata_dict)

                d3 = get_banknifty_data()
                bankniftydf = pd.concat([bankniftydf, d3], ignore_index=True)
                bank_data_dict = bankniftydf.to_dict("records")
                collection.insert_many(bank_data_dict)

                d4 = get_midcapnifty_data()
                midcapniftydf = pd.concat([midcapniftydf, d4], ignore_index=True)
                mid_data_dict = midcapniftydf.to_dict("records")
                collection.insert_many(mid_data_dict)

                with niftytbl:
                    niftydata = get_data_mongodb('nifty')[sel_cols]
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Nifty Prm Decay Chart')
                    niftytbl.plotly_chart(chart, use_container_width=True)

                with bankniftytbl:
                    bankniftydata = get_data_mongodb('banknifty')[sel_cols]
                    chart = chart_prmdecay(bankniftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Bank Nifty Prm Decay Chart')
                    bankniftytbl.plotly_chart(chart, use_container_width=True)

                with fniftytbl:
                    fniftydata = get_data_mongodb('finnifty')[sel_cols]
                    chart = chart_prmdecay(fniftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Fin Nifty Prm Decay Chart')
                    fniftytbl.plotly_chart(chart, use_container_width=True)

                with midcapniftytbl:
                    midcpniftydata = get_data_mongodb('midcpnifty')[sel_cols]
                    chart = chart_prmdecay(midcpniftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Midcap Nifty Prm Decay Chart')
                    midcapniftytbl.plotly_chart(chart, use_container_width=True)
                
                # Sleep for 1 minute
                time.sleep(60)
            else:
                # Sleep for 1 second to prevent a tight loop when waiting to start
                time.sleep(1)


run_data_collection("9:15", "3:30")
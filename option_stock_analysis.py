import time
from datetime import datetime, timedelta
from lib import get_stock_data
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from pymongo import MongoClient
from pandas import json_normalize

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nse']
collection = db['premdecay']

today = '08-07-2024'

st.set_page_config(layout="wide", page_title=f'Live Stock Premium Decay Charts')
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

today = '08-07-2024'



def get_premium_decay(symbol, index, data, csp, time, expiry):
    # Initialize the sum values
    sum_CE_change = 0
    sum_CE_coi = 0
    sum_PE_change = 0
    sum_PE_coi = 0
    sum_CE_oi = 0
    sum_PE_oi = 0
    underlying_value = None
    # print(data)
    # Iterate over the list of dictionaries
    # for strike_data in data:
    #     ce_data = strike_data['CE']
    #     pe_data = strike_data['PE']

    #     sum_CE_change += round(ce_data['change'],2)
    #     sum_CE_coi += ce_data['changeinOpenInterest']
    #     sum_PE_change += round(pe_data['change'],2)
    #     sum_PE_coi += pe_data['changeinOpenInterest']
    #     sum_CE_oi += ce_data['openInterest']
    #     sum_PE_oi += pe_data['openInterest']
        
    #     # Store the underlying value
    #     underlying_value = ce_data['underlyingValue']
    for strike_data in data:
        if 'CE' in strike_data:
            ce_data = strike_data['CE']
            sum_CE_change += round(ce_data['change'], 2)
            sum_CE_coi += ce_data['changeinOpenInterest']
            sum_CE_oi += ce_data['openInterest']
            underlying_value = ce_data['underlyingValue']
        if 'PE' in strike_data:
            pe_data = strike_data['PE']
            sum_PE_change += round(pe_data['change'], 2)
            sum_PE_coi += pe_data['changeinOpenInterest']
            sum_PE_oi += pe_data['openInterest']
            # Store the underlying value (assuming it's the same for both CE and PE if they exist)
            if 'CE' not in strike_data:
                underlying_value = pe_data['underlyingValue']
                
    # Create a new DataFrame with the aggregated results
    result_df = pd.DataFrame({
        "symbol": symbol,
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
    selcol = ['date', 'symbol', 'index', 'expiry', 'time', 'nifty', 'current_strike_price', 'ce_prmdecay', 'pe_prmdecay', 'ce_coi', 'pe_coi', 'ce_oi', 'pe_oi']
    return result_df[selcol]

def market_time():
    # Parse the start and end times
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("23:50", "%H:%M")
    
    # Get the current time
    now = datetime.now()
    
    # Set the current date for the start and end times
    start_time = start_time.replace(year=now.year, month=now.month, day=now.day)
    end_time = end_time.replace(year=now.year, month=now.month, day=now.day)
    
    # If the end time is earlier in the day than the start time, it means the end time is on the next day
    if end_time < start_time:
        end_time += timedelta(days=1)

    # Keep printing until the current time exceeds the end time
    while now < end_time:
        now = datetime.now()
        if start_time <= now <= end_time:
            print("hello python")
            time.sleep(60)  # Sleep for 60 seconds
        else:
            time.sleep(1)  # Sleep for 1 second to prevent tight loop when waiting to start

def get__data(lotsize, multiplier, stock):
    index = 'EQ'
    symbol = stock
    currentStrikePrice = get_stock_data(lotsize, multiplier, stock)['currentStrikePrice']
    filter_data = get_stock_data(lotsize, multiplier, stock)['filter_data']
    formatted_timestamp = get_stock_data(lotsize, multiplier, stock)['formatted_timestamp']
    expiry = get_stock_data(lotsize, multiplier, stock)['expiryDate']
    d1 = get_premium_decay(symbol, index, filter_data, currentStrikePrice, formatted_timestamp, expiry)
    return d1

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
   

# CANBK, CONCOR, LAURUSLABS, NMDC, VEDL
def get_data_mongodb(stock):
    # Define the query to filter documents where 'index' field is 'nifty' and not None
    # query = {"symbol": {"$exists": True, "$ne": None, "$eq": stock}}
    query = {
        "symbol": {"$exists": True, "$ne": None, "$eq": stock},
        "date": today  # Adjust the date format according to your data
    }

    # Retrieve all documents matching the query
    documents = collection.find(query)

    # Convert the documents to a list
    document_list = list(documents)

    # Normalize the documents (if they have nested structures)
    df = json_normalize(document_list)

    # Remove duplicate rows based on 'time' column
    df = df.drop_duplicates(subset='time')
    return df

col1, col2 = st.columns(2)
with col1:
    df2tbl = st.empty()

with col2:
    df4tbl = st.empty() 

df1tbl = st.empty()
df3tbl = st.empty()
df5tbl = st.empty()

sel_cols = ['symbol', 'index', 'time', 'nifty', 'current_strike_price', 'ce_prmdecay', 'pe_prmdecay', 'ce_coi', 'pe_coi', 'ce_oi', 'pe_oi']

def run_data_collection(start_time_str, end_time_str):
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    df4 = pd.DataFrame()
    df5 = pd.DataFrame()
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

                d1 = get__data(1, 10, "CANBK")
                df1 = pd.concat([df1, d1], ignore_index=True)
                data_dict1 = df1.to_dict("records")
                collection.insert_many(data_dict1)

                d2 = get__data(10, 10, "CONCOR")
                df2 = pd.concat([df2, d2], ignore_index=True)
                data_dict2 = df2.to_dict("records")
                collection.insert_many(data_dict2)

                d3 = get__data(5, 10, "LAURUSLABS")
                df3 = pd.concat([df3, d3], ignore_index=True)
                data_dict3 = df3.to_dict("records")
                collection.insert_many(data_dict3)

                d4 = get__data(5, 8, "NMDC")
                df4 = pd.concat([df4, d4], ignore_index=True)
                data_dict4 = df4.to_dict("records")
                collection.insert_many(data_dict4)

                d5 = get__data(10, 8, "VEDL")
                df5 = pd.concat([df5, d5], ignore_index=True)
                data_dict5 = df5.to_dict("records")
                collection.insert_many(data_dict5)

                with df1tbl:
                    niftydata = get_data_mongodb('CANBK')[sel_cols]
                    niftydata = get_data_mongodb('CANBK')
                    st.write(niftydata)
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Prm Decay Chart - CANBANK')
                    df1tbl.plotly_chart(chart, use_container_width=True)

                with df2tbl:
                    niftydata = get_data_mongodb('CONCOR')[sel_cols]
                    st.write(niftydata)
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Prm Decay Chart - CONCOR')
                    df2tbl.plotly_chart(chart, use_container_width=True)
                
                with df3tbl:
                    niftydata = get_data_mongodb('LAURUSLABS')[sel_cols]
                    st.write(niftydata)
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Prm Decay Chart - LAURASLABS')
                    df3tbl.plotly_chart(chart, use_container_width=True)

                with df4tbl:
                    niftydata = get_data_mongodb('NMDC')[sel_cols]
                    st.write(niftydata)
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Prm Decay Chart - NMDC')
                    df4tbl.plotly_chart(chart, use_container_width=True)

                with df5tbl:
                    niftydata = get_data_mongodb('VEDL')[sel_cols]
                    st.write(niftydata)
                    chart = chart_prmdecay(niftydata, 'time', 'ce_prmdecay', 'pe_prmdecay',  title=f'Prm Decay Chart - VEDL')
                    df5tbl.plotly_chart(chart, use_container_width=True)

                # Sleep for 1 minute
                time.sleep(60)
            else:
                # Sleep for 1 second to prevent a tight loop when waiting to start
                time.sleep(1)
            
# lotsize, multiplier and stock
# data = get__data(50, 4, "RELIANCE")
# # data = get_stock_data(50, 4, "RELIANCE")
# st.write((data))

run_data_collection("9:15", "3:30")
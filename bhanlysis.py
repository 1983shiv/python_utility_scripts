import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import plotly.express as px

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['nse']
collection = db['stocks']

st.set_page_config(layout="wide", page_title=f'Bhav Analysis')
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


def get_percentage(data, o_col1, o_col2, i_col):
    # Ensure we're working with a copy to avoid SettingWithCopyWarning
    data = data.copy()
    # if len(group) < 3:
    #         return False
    # group[o_col1] = group[i_col].diff(-1)
    # group[o_col2] = group[i_col].diff(-2)
    
    result = []
    for symbol, group in data.groupby('symbol'):
        if len(group) >= 3:
            group = group.head(3)  # Ensure only the last 3 entries are considered
            current_date_data = group.iloc[0].copy()
            
            # Calculate changes and percentages
            c2 = group.iloc[0][i_col] - group.iloc[1][i_col]
            c1 = group.iloc[1][i_col] - group.iloc[2][i_col]
            
            current_date_data['c2'] = c2
            current_date_data['c1'] = c1
            
            # Calculate percentages and assign using .loc
            current_date_data.loc[o_col1] = int((c1 / group.iloc[2][i_col]) * 100)
            current_date_data.loc[o_col2] = int((c2 / group.iloc[1][i_col]) * 100)
            result.append(current_date_data)
    return result

def positive_changes(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        return group.iloc[0]['change'] > 0 and group.iloc[1]['change'] > 0 and group.iloc[2]['change'] > 0

def positive_tv(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        return group.iloc[0]['tv_perc'] > 0 and group.iloc[1]['tv_perc'] > 0

def positive_dq(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        return group.iloc[0]['dq_perc'] > 0 and group.iloc[1]['dq_perc'] > 0

def positive_nt(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        return group.iloc[0]['nt_perc'] > 0 and group.iloc[1]['nt_perc'] > 0

def negative_changes(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for negative changes
        return group.iloc[0]['change'] < 0 and group.iloc[1]['change'] < 0 and group.iloc[2]['change'] < 0

def negative_tv(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for negative changes
        return group.iloc[0]['tv_perc'] < 0 and group.iloc[1]['tv_perc'] < 0

def negative_dq(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for negative changes
        return group.iloc[0]['dq_perc'] < 0 and group.iloc[1]['dq_perc'] < 0

def negative_nt(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for negative changes
        return group.iloc[0]['nt_perc'] < 0 and group.iloc[1]['nt_perc'] < 0


def positive_filter_symbols(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    fg3 = fg2.groupby('symbol').filter(positive_dq)
    fg4 = fg3.groupby('symbol').filter(positive_nt)
    result_df = pd.DataFrame(fg4)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def negative_filter_symbols(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    fg2 = fg1.groupby('symbol').filter(negative_tv)
    fg3 = fg2.groupby('symbol').filter(negative_dq)
    fg4 = fg3.groupby('symbol').filter(negative_nt)
    result_df = pd.DataFrame(fg4)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

# Function to fetch data from MongoDB and convert it to DataFrame
def fetch_data(dt=None):
    if dt is None:
        data = list(collection.find())
    else :        
        # query = {"date": {"$eq": pd.to_datetime(dt)}}
        # data = list(collection.find(query))
        end_date = pd.to_datetime(dt)        
        # Fetch last two available trading dates
        query = {"date": {"$lte": end_date}}
        df = pd.DataFrame(list(collection.find(query)))
        dates = df["date"].sort_values(ascending=False).unique()[:3]
        query2 = {"date": {"$gte": pd.to_datetime(dates[2]), "$lte": pd.to_datetime(dates[0])}}
        data = (list(collection.find(query2)))
    # Construct the query
    processed_data = []
    for entry in data:
        flat_entry = {
            "symbol": entry["symbol"],
            "date": entry["date"],
            "change": (entry["close_price"] - entry["prev_close"]),
            "prev_close": entry["prev_close"],
            "open_price": entry["open_price"],
            "high_price": entry["high_price"],
            "low_price": entry["low_price"],
            "last_price": entry["last_price"],
            "close_price": entry["close_price"],
            "ttl_trd_qnty": entry["ttl_trd_qnty"],
            "turnover_lacs": entry["turnover_lacs"],
            "no_of_trades": entry["no_of_trades"],
            "deliv_qty": entry["deliv_qty"],
            "deliv_per": entry["deliv_per"],
            "daily": entry["daily"],
            "yearly": entry["yearly"]
        }
        processed_data.append(flat_entry)
    df = pd.DataFrame(processed_data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Ensure date is in datetime format
    return df


# Load data into DataFrame
df = fetch_data()

# Streamlit app
st.title("Stock Data Visualization")


dates = df["date"].unique()[2:]
option = st.selectbox(
    "Dates",
    sorted(dates, reverse=True))

df2 = fetch_data(option)
df2['tv_diff'] = df2.groupby('symbol')['turnover_lacs'].diff()
df2['nt_diff'] = df2.groupby('symbol')['no_of_trades'].diff()
df2['dq_diff'] = df2.groupby('symbol')['deliv_qty'].diff()

df2['tv_perc'] = (df2['tv_diff']/df2.groupby('symbol')['turnover_lacs'].shift(1))*100
df2['nt_perc'] = (df2['nt_diff']/df2.groupby('symbol')['no_of_trades'].shift(1))*100
df2['dq_perc'] = (df2['dq_diff']/df2.groupby('symbol')['deliv_qty'].shift(1))*100

selcol = ['symbol', 'change', 'last_price', 'tv_perc', 'nt_perc', 'dq_perc']
col1, col2 = st.columns(2)
with col1:
    st.title("Positive / Buy ")
    st.write(positive_filter_symbols(df2, option)['symbol'].count())
    st.write(positive_filter_symbols(df2, option)[selcol])
with col2:
    st.title("Negative / Sell")
    st.write(negative_filter_symbols(df2, option)['symbol'].count())
    st.write(negative_filter_symbols(df2, option)[selcol])
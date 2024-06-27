import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import plotly.express as px
import altair as alt

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['nse']
collection = db['stocks']
detail_collection = db['stock_info']

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

if "buy_symbol" not in st.session_state:
        st.session_state.buy_symbol = ''

if "sell_symbol" not in st.session_state:
        st.session_state.sell_symbol = ''

if "sel_date" not in st.session_state:
        st.session_state.date = ''

if "buy_symbols" not in st.session_state:
    st.session_state.buy_symbols = [] 

if "sell_symbols" not in st.session_state:
    st.session_state.sell_symbols = []

if "fno_buy_symbols" not in st.session_state:
    st.session_state.fno_buy_symbols = [] 

if "fno_sell_symbols" not in st.session_state:
    st.session_state.fno_sell_symbols = []    


def calculate_average_metrics(df, wndw):
    # Calculate average Total Traded Quantity (TTQ) over the last 30 days
    df['Average_TTQ'] = df['ttl_trd_qnty'].rolling(window=wndw, min_periods=1).mean()
    
    # Calculate standard deviation of TTQ over the last 30 days
    df['Std_Dev_TTQ'] = df['ttl_trd_qnty'].rolling(window=wndw, min_periods=1).std()
    
    # Calculate average Close Price over the last 30 days
    df['Average_Close_Price'] = df['close_price'].rolling(window=wndw, min_periods=1).mean()
    
    # Calculate average Delivery Percentage over the last 30 days
    df['Average_Delivery_Pct'] = df['deliv_per'].rolling(window=wndw, min_periods=1).mean()
    
    # Calculate average Daily IV over the last 30 days
    df['Average_Daily_IV'] = df['iv_daily'].rolling(window=wndw, min_periods=1).mean()
    
    return df


def chat_ltp_tv(data, x, y1, r1, title="Bar Chart"):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m-%d')
    line_y1 = (
        alt.Chart(df, title=f'{title}')
        .mark_line(color="blue", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r1)],
        )
    )

    bar_y3 = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=x,
            y=(r1),
            tooltip=[str(x), str(y1), str(r1)],
        )
    )

    chart = (bar_y3 + line_y1).resolve_scale(y="independent").configure_axis(labelFontSize=8)
    return chart


def chart_eq_mf_v3(data, x, y1, r1, y3, y4, vol_clr, title="Bar Chart"):
    data1 = pd.DataFrame(data)
    if st.session_state.chart_duration is None or st.session_state.chart_duration == '':
        df = data1
    else:
        df = data1[-(st.session_state.chart_duration):]

    line_y1 = (
        alt.Chart(df, title=f'{title}')
        .mark_line(color="blue", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r1), str(y4), str(y3)],
        )
    )

    line_y3 = (
        alt.Chart(df)
        .mark_line(color="#C71585", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y3, axis=alt.Axis(title=str(y3)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r1), str(y4), str(y3)],
        )
    )

    bar_y3 = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=x,
            y=(r1),
            color=alt.Color(vol_clr),
            tooltip=[str(x), str(y1), str(r1), str(y4), str(y3)],
        )
    )

    bar_y4 = (
        alt.Chart(df)
        .mark_bar(color='#ccc', strokeWidth=2)
        .encode(
            x=x,
            y=(y4),
            tooltip=[str(x), str(y1), str(r1), str(y4), str(y3)],
        )
    )

    chart = (bar_y4 + bar_y3 + line_y1 + line_y3).resolve_scale(y="independent").configure_axis(labelFontSize=8)
    return chart


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
        return group.iloc[0]['change'] > 0 and group.iloc[1]['change'] > 0

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
        print(f"symbol : {group.iloc[0]['symbol']} 0: {group.iloc[0]['dq_perc']}, 1: {group.iloc[1]['dq_perc']} and 2: {group.iloc[2]['dq_perc']}")
        return group.iloc[0]['dq_perc'] > 0 and group.iloc[1]['dq_perc'] > 0

def positive_nt(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        return group.iloc[0]['nt_perc'] > 0 and group.iloc[1]['nt_perc'] > 0

def positive_coi(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        if "coi" in group:
            return group.iloc[0]['coi'] > 0 and group.iloc[1]['coi'] > 0


def negative_changes(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for negative changes
        return group.iloc[0]['change'] < 0 and group.iloc[1]['change'] < 0

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

def negative_coi(group):
        if len(group) < 3:
            return False
        # Ensure only the last 3 entries are considered
        group = group.head(3).copy()               
        # Return the condition for positive changes
        if "coi" in group:
            return group.iloc[0]['coi'] < 0 and group.iloc[1]['coi'] < 0


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

def fno_positive_filter_symbols(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    fg3 = fg2.groupby('symbol').filter(positive_nt)
    fg4 = fg3.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(positive_coi)
    # positive_coi
    
    result_df = pd.DataFrame(fg5)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_positive_wo_nt(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    # fg3 = fg2.groupby('symbol').filter(positive_nt)
    fg4 = fg2.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(positive_coi)
    # positive_coi
    
    result_df = pd.DataFrame(fg5)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_positive_wo_tv(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    # fg3 = fg2.groupby('symbol').filter(positive_nt)
    # fg4 = fg2.groupby('symbol').filter(positive_dq)
    fg5 = fg2.groupby('symbol').filter(positive_coi)
    # positive_coi
    
    result_df = pd.DataFrame(fg5)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_positive_wo_dq(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    # fg2 = fg1.groupby('symbol').filter(positive_tv)
    # fg3 = fg2.groupby('symbol').filter(positive_nt)
    fg4 = fg1.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(positive_coi)
    # positive_coi
    
    result_df = pd.DataFrame(fg5)  
    
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_positive_wo_tv_dq(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(positive_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    # fg3 = fg2.groupby('symbol').filter(positive_nt)
    fg4 = fg2.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(positive_coi)
    # positive_coi
    
    result_df = pd.DataFrame(fg5)  
    
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

def fno_negative_filter_symbols(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    fg2 = fg1.groupby('symbol').filter(negative_tv)
    fg3 = fg2.groupby('symbol').filter(negative_nt)
    fg4 = fg3.groupby('symbol').filter(negative_dq)
    fg5 = fg4.groupby('symbol').filter(negative_coi)
    result_df = pd.DataFrame(fg5)  
    
    # negative_coi
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_negative_filter_symbols_two(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    fg2 = fg1.groupby('symbol').filter(negative_tv)
    # fg3 = fg2.groupby('symbol').filter(negative_nt)
    fg4 = fg2.groupby('symbol').filter(negative_dq)
    fg5 = fg4.groupby('symbol').filter(negative_coi)
    result_df = pd.DataFrame(fg5)  
    
    # negative_coi
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_negative_deliv(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    # fg2 = fg1.groupby('symbol').filter(negative_tv)
    # fg3 = fg2.groupby('symbol').filter(negative_nt)
    fg4 = fg1.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(negative_coi)
    result_df = pd.DataFrame(fg5)  
    
    # negative_coi
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df

def fno_negative_tv(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    # fg2 = fg1.groupby('symbol').filter(negative_tv)
    # fg3 = fg2.groupby('symbol').filter(negative_nt)
    fg4 = fg1.groupby('symbol').filter(positive_tv)
    fg5 = fg4.groupby('symbol').filter(negative_coi)
    result_df = pd.DataFrame(fg5)  
    
    # negative_coi
    if option:
        result_df = result_df[result_df['date'] == pd.to_datetime(option)]
    result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')
    return result_df


def fno_negative_tv_dq(data, option=None):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])    
    # Sort data by symbol and date
    df = df.sort_values(by=['symbol', 'date'], ascending=[True, False])
    # Apply the filter and get the matching symbols
    fg1 = df.groupby('symbol').filter(negative_changes)
    fg2 = fg1.groupby('symbol').filter(positive_tv)
    # fg3 = fg2.groupby('symbol').filter(positive_dq)
    fg4 = fg2.groupby('symbol').filter(positive_dq)
    fg5 = fg4.groupby('symbol').filter(negative_coi)
    result_df = pd.DataFrame(fg5)  
    
    # negative_coi
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
        if "coi" in entry and "oi" in entry:
            flat_entry = {
                "symbol": entry["symbol"],
                "date": entry["date"],
                "change": (entry["close_price"] - entry["prev_close"]),
                "chg_per": round((((entry["close_price"] - entry["prev_close"])/entry["prev_close"])*100),1),
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
                "iv_daily": entry["iv_daily"],
                "iv_yearly": entry["iv_yearly"],
                "coi": entry["coi"],
                "oi": entry["oi"],
            }
            processed_data.append(flat_entry)
        else:
            flat_entry = {
                "symbol": entry["symbol"],
                "date": entry["date"],
                "change": (entry["close_price"] - entry["prev_close"]),
                "chg_per": round((((entry["close_price"] - entry["prev_close"])/entry["prev_close"])*100),1),
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
                "iv_daily": entry["iv_daily"],
                "iv_yearly": entry["iv_yearly"]
            }
            processed_data.append(flat_entry)
    
    df = pd.DataFrame(processed_data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Ensure date is in datetime format
    return df

def fetch_data2(dt=None):
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

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Ensure date is in datetime format
    return df

def fetch_details(symbol=None):
    if symbol is None:
        data = list(collection.find())
    else :        
        query = {"symbol": symbol}
        data = pd.DataFrame(list(collection.find(query)))
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')  # Ensure date is in datetime format
    return df

def fetch_info(symbol=None):
    if symbol is None:
        data = list(detail_collection.find())
    else :        
        query = {"symbol": symbol}
        data = (list(detail_collection.find(query)))
    # df = pd.DataFrame(data)
    return data

def get_symbols_data(symbols=[]):
    data = []
    for symbol in symbols:
        get_data = fetch_info(symbol)
        data.extend(get_data)
    return pd.DataFrame(data)

def prepared_data(df2):    
    df2['change'] = df2["close_price"] - df2["prev_close"]
    df2['chg_per'] = round((((df2["close_price"] - df2["prev_close"])/df2["prev_close"])*100),1)
    df2['tv_diff'] = df2.groupby('symbol')['turnover_lacs'].diff()
    df2['nt_diff'] = df2.groupby('symbol')['no_of_trades'].diff()
    df2['dq_diff'] = df2.groupby('symbol')['deliv_qty'].diff()

    df2['tv_perc'] = (df2['tv_diff']/df2.groupby('symbol')['turnover_lacs'].shift(1))*100
    df2['nt_perc'] = (df2['nt_diff']/df2.groupby('symbol')['no_of_trades'].shift(1))*100
    df2['dq_perc'] = (df2['dq_diff']/df2.groupby('symbol')['deliv_qty'].shift(1))*100
    return df2

columns_to_display = ['symbol', 'chg_per', 'last_price', 'book_value', 'intrinsic_value', 'mcap', 'debt', 'int_coverage', 'debt_to_equity', 'promoter_holding', 'change_in_prom_hold', 'fii_holding', 'change_in_fii_holding', 'dii_holding', 'change_in_dii_holding', 'high_52week', 'low_52week']

summery,positive, negative, all = st.tabs(['Summery', 'Buy', 'Sell', 'All'])


df = fetch_data2()
# df['change'] = df["close_price"] - df["prev_close"]
# df['chg_per'] = round((((df["close_price"] - df["prev_close"])/df["prev_close"])*100),1)
# st.write(df)

with summery:
    dates = df["date"].unique()[2:]
    st.session_state.sel_date = st.selectbox(
        "Dates",
        sorted(dates, reverse=True))
    dataframe = fetch_data2(st.session_state.sel_date)
    df2 = prepared_data(dataframe)
    df2['chg_oi'] = round((df2['coi'] / (df2['coi'] + df2['oi'])) * 100, 1)
    selcol = ['symbol', 'chg_per', 'last_price', 'tv_perc', 'nt_perc', 'dq_perc']
    fnocol = ['symbol', 'chg_per', 'last_price', 'chg_oi', 'coi', 'oi', 'tv_perc', 'nt_perc', 'dq_perc']
    col1, col2 = st.columns(2)
    with col1:
        st.title("FnO Positive / Buy ")
        st.session_state.fno_buy_symbols = fno_positive_filter_symbols(df2, st.session_state.sel_date)['symbol']
        st.write(fno_positive_filter_symbols(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_positive_filter_symbols(df2, st.session_state.sel_date)[fnocol])

        st.subheader("FnO Positive / Buy (Traded Volue/Delivery Qty) ")
        st.write(fno_positive_wo_tv_dq(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_positive_wo_tv_dq(df2, st.session_state.sel_date)[fnocol])

        st.subheader("FnO Positive / Buy (Traded Volue)")
        st.write(fno_positive_wo_tv(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_positive_wo_tv(df2, st.session_state.sel_date)[fnocol])

        st.subheader("FnO Positive / Buy (Delivery wise)")
        st.write(fno_positive_wo_dq(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_positive_wo_dq(df2, st.session_state.sel_date)[fnocol])
        # fno_positive_wo_nt | fno_positive_wo_tv_dq
    with col2:
        st.title("FnO Negative / Sell ")
        st.session_state.fno_sell_symbols = fno_negative_filter_symbols_two(df2, st.session_state.sel_date)['symbol']
        st.write(fno_negative_filter_symbols(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_negative_filter_symbols(df2, st.session_state.sel_date)[fnocol])
        
        st.subheader("FnO Negative / Sell (Traded Volue/Delivery Qty)")
        st.write(fno_negative_tv_dq(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_negative_tv_dq(df2, st.session_state.sel_date)[fnocol])
        
        st.subheader("FnO Negative / Sell (Traded Volue)")
        st.write(fno_negative_tv(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_negative_tv(df2, st.session_state.sel_date)[fnocol])
        
        st.subheader("FnO Negative / Sell (Delivery wise)")
        st.write(fno_negative_deliv(df2, st.session_state.sel_date)['symbol'].count())
        st.write(fno_negative_deliv(df2, st.session_state.sel_date)[fnocol])
        
        
        # fno_negative_deliv | fno_negative_tv | fno_negative_tv_dq
    col1, col2 = st.columns(2)
    with col1:
        st.title("Positive / Buy ")
        st.session_state.buy_symbols = positive_filter_symbols(df2, st.session_state.sel_date)['symbol']
        st.write(positive_filter_symbols(df2, st.session_state.sel_date)['symbol'].count())
        buy_data = positive_filter_symbols(df2, st.session_state.sel_date)[selcol]       
        stock_info = get_symbols_data(st.session_state.buy_symbols)            
        final_df = pd.merge(pd.DataFrame(buy_data), pd.DataFrame(stock_info), on='symbol', how='inner')
        st.write(pd.DataFrame(final_df)[columns_to_display])
    with col2:
        st.title("Negative / Sell")
        st.session_state.sell_symbols = negative_filter_symbols(df2, st.session_state.sel_date)['symbol']
        st.write(negative_filter_symbols(df2, st.session_state.sel_date)['symbol'].count())
        sell_data = negative_filter_symbols(df2, st.session_state.sel_date)[selcol]
        stock_info = get_symbols_data(st.session_state.sell_symbols)
        final_df = pd.merge(pd.DataFrame(sell_data), pd.DataFrame(stock_info), on='symbol', how='inner')
        st.write(pd.DataFrame(final_df)[columns_to_display])

with positive:
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.buy_symbol = st.selectbox(
            "Symbol",
            sorted(st.session_state.buy_symbols, reverse=True))
    with col2:
        st.subheader(f"Buy Analysis for the date {st.session_state.sel_date} for  {st.session_state.buy_symbol}")
    # 
    data = fetch_details(st.session_state.buy_symbol)
    col1, col2 = st.columns(2)
    with col1:
        chart = chat_ltp_tv(data,'date', 'close_price', 'turnover_lacs', title="LTP vs Turnover(Lacs)")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'deliv_per', title="LTP vs Delivery(%)")
        col2.altair_chart(chart, use_container_width=True)
    if "coi" in data:
        col1, col2 = st.columns(2)
        with col1:
            chart = chat_ltp_tv(data,'date', 'close_price', 'coi', title="LTP vs COI")
            col1.altair_chart(chart, use_container_width=True)
        with col2:
            chart = chat_ltp_tv(data,'date', 'close_price', 'oi', title="LTP vs OI")
            col2.altair_chart(chart, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        data['qty_per_trades'] = data['ttl_trd_qnty'] // data['no_of_trades']
        chart = chat_ltp_tv(data,'date', 'close_price', 'qty_per_trades', title="LTP vs Qty Per Trades")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'no_of_trades', title="No. of Trades")
        col2.altair_chart(chart, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        chart = chat_ltp_tv(data,'date', 'close_price', 'iv_daily', title="LTP vs IV daily")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'iv_yearly', title="LTP vs IV Yearly")
        col2.altair_chart(chart, use_container_width=True)
    # st.write(data)

with negative:
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.sell_symbol = st.selectbox(
            "Symbol",
            sorted(st.session_state.sell_symbols, reverse=True))
    # symbol = df["symbol"].unique()
    
    with col2:
        st.subheader(f"Sell Analysis for the date {st.session_state.sel_date} for  {st.session_state.sell_symbol}")
    # symbol = df["symbol"].unique()
    data = fetch_details(st.session_state.sell_symbol)
    col1, col2 = st.columns(2)
    with col1:
        chart = chat_ltp_tv(data,'date', 'close_price', 'turnover_lacs', title="LTP vs Turnover(Lacs)")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'deliv_per', title="LTP vs Delivery(%)")
        col2.altair_chart(chart, use_container_width=True)
    if "coi" in data:
        col1, col2 = st.columns(2)
        with col1:
            chart = chat_ltp_tv(data,'date', 'close_price', 'coi', title="LTP vs COI")
            col1.altair_chart(chart, use_container_width=True)
        with col2:
            chart = chat_ltp_tv(data,'date', 'close_price', 'oi', title="LTP vs OI")
            col2.altair_chart(chart, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        data['qty_per_trades'] = data['ttl_trd_qnty'] // data['no_of_trades']
        chart = chat_ltp_tv(data,'date', 'close_price', 'qty_per_trades', title="LTP vs Qty Per Trades")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'no_of_trades', title="No. of Trades")
        col2.altair_chart(chart, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        chart = chat_ltp_tv(data,'date', 'close_price', 'iv_daily', title="LTP vs IV daily")
        col1.altair_chart(chart, use_container_width=True)
    with col2:
        chart = chat_ltp_tv(data,'date', 'close_price', 'iv_yearly', title="LTP vs IV Yearly")
        col2.altair_chart(chart, use_container_width=True)
    # st.write(data)

with all:
    symbols = df["symbol"].unique()
    col1, col2 = st.columns(2)
    with col1:
        selected_Symbol = st.selectbox(
            "Symbol",
            sorted(symbols, reverse=True))
    # symbol = df["symbol"].unique()
    
    with col2:
        st.subheader(f"Stock Analysis for the date {st.session_state.sel_date} for  {selected_Symbol}")
    # symbol = df["symbol"].unique()
    data = fetch_details(selected_Symbol)
    data2 = calculate_average_metrics(data, 15)
    st.write(data2)
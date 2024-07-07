# import sys
# sys.path.append("./config")
# import config
import sys
sys.path.append("H:\\sm\\config\\")
import config

# from money_flow import *
# print(config.db_name)

import pymongo
import streamlit as st
import altair as alt
import random
from nsepy import get_history
from datetime import datetime
from datetime import timedelta
# from datetime import datetime as dt
import datetime as dt
import pandas as pd
from nsepython import nse_optionchain_scrapper
import altair as alt
from functools import wraps
# from loginz import *
import numpy as np
import plotly.graph_objs as go

# print(config.expiryf)
def moneyflow_hist(df):
    df1 = pd.DataFrame()
    df['Avgpr']=(df['high']+df['low'])/2   
    df['MFCr']=df['Avgpr']*df['volume']/10000000
    df['MFStus']=df['close']-df['open']
    df['MFCrS']=np.sign(df['MFStus'])

    df['MFCrS1']=df['MFCrS']

    df['cvol']=df['volume'].diff()

    df['MFCrS1']=df['MFCrS']

    n=0

    while n<len(df['MFCrS']):

        if df['MFCrS'][n]==0:
            try:
                df['MFCrS1'][n]=df['MFCrS1'][n-1]
            except:
                print('ok')

        # df['instrument']=instr
        n+=1

    df['MFCr']=df['MFCr']*df['MFCrS1'] 

    m=1
    df['MF']=df['MFCr']

    while m<len(df['MFCr']):
        df['MF'][m]=df['MF'][m-1]+df['MFCr'][m]
        m+=1

    df['ltpdiff'] = df['close'].diff()
    df['coidff'] = df['oi'].diff()
    df['action'] = df.apply(lambda row: oi_activity(row['coidff'], row['ltpdiff']), axis=1)
    df1 =df.drop(['MFCrS', 'MFStus','MFCrS1'], axis=1)
    return df1

def memoize(func):
    cache =  {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]
    return wrapper



# # /*************** Slider
# # # Create a range slider for selecting the time range
# start_time = (pd.to_datetime(dfp['timestamp'])).min()
# end_time = (pd.to_datetime(dfp['timestamp'])).max()

# # start_time = dt.strptime(str((pd.to_datetime(dfp['timestamp'])).min())[-8:], "%H:%M:%S")
# # end_time = dt.strptime(str((pd.to_datetime(dfp['timestamp'])).max())[-8:], "%H:%M:%S")

# # selected_start_time, selected_end_time = st.slider('Select Time Range', start_time, end_time, (start_time, end_time))
# # # time_range = st.slider('Select Time Range', value=[start_time, end_time])
# # # Convert pandas timestamps to integer representations

# # /**************************
# start_time_int = int(start_time.timestamp()) 
# end_time_int = int(end_time.timestamp()) 


# # Get the selected time range using the slider
# selected_start_time_int, selected_end_time_int = st.slider('Select Time Range', start_time_int, end_time_int, (start_time_int, end_time_int), step=1800)

# # Convert the selected integer values back to pandas timestamps
# selected_start_time = pd.Timestamp(selected_start_time_int, unit='s')
# selected_end_time = pd.Timestamp(selected_end_time_int, unit='s')


# # # Filter the DataFrame based on the selected time range
# dfp = dfp[(pd.to_datetime(dfp['timestamp']) >= selected_start_time) & (pd.to_datetime(dfp['timestamp']) <= selected_end_time)]
# # /**************************


# make function for future, stock, 
# https://www.nseindia.com/api/liveEquity-derivatives?index=top20_contracts
# https://www.nseindia.com/api/liveEquity-derivatives?index=stock_fut
# https://www.nseindia.com/api/liveEquity-derivatives?index=stock_opt

def add_time_interval(time_str):
    interval = 120 # 1 minute
    # Convert time string to datetime object
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    # Add interval to datetime object
    new_time_obj = time_obj + dt.timedelta(seconds=interval)
    # Convert datetime object back to time string
    new_time_str = new_time_obj.strftime('%H:%M:%S')
    return new_time_str

def generate_random_time():
    start_time = dt.time(hour=9, minute=0, second=0)
    end_time = dt.time(hour=15, minute=30, second=0)
    # Generate a random time within the specified duration
    time_delta = dt.datetime.combine(dt.date.today(), end_time) - dt.datetime.combine(dt.date.today(), start_time)
    random_time = dt.datetime.combine(dt.date.today(), start_time) + dt.timedelta(seconds=random.randint(0, time_delta.seconds))
    return random_time.time()

def get_random():
    # random_num = random.random()
    random_num = random.uniform(0, 5)
    # Multiply the random float by 10 to get a value between 0 and 10
    # random_num *= 10

    # Round the random number to 2 decimal places
    random_num = round(random_num, 2)
    return random_num

def longshort_ze(data):
    processed_data = []
    previous_data = None

    for index, data in enumerate(data):
        if index == 0:
            previous_data = data
        else:
            new_data = {
                "time": (data["time"]),
                "celtp": data["celtp"],
                "cecoi": data['cecoi'],
                "peltp": data["peltp"],
                "pecoi": data['pecoi'],
                "cp": data["cp"],
                "previous_peltp": previous_data["peltp"],
                "pediff": (data["peltp"] - previous_data["peltp"]),
                "pestatus": oi_status(True, data['pecoi'], (data["peltp"] - previous_data["peltp"])),
                "cediff": (data["celtp"] - previous_data["celtp"]),
                "cestatus": oi_status(True, data['cecoi'], (data["celtp"] - previous_data["celtp"]))
            }
            processed_data.append(new_data)
            previous_data = data
    
    return processed_data

# def oi_activity(coi = 1, chgprice = 1):
#     if(coi >= 0 and chgprice >= 0):
#         # Buyer - Long BuildUp
#         return "Long"
    
#     if(coi <= 0 and chgprice <= 0):
#         # Buyer - Long Unwinding
#         return "Unwinding"
    
#     if(coi <= 0 and chgprice >= 0):
#         # Seller - Short Covering
#         return "Short Covering"
    
#     if(coi >= 0 and chgprice <= 0):
#         # Seller - Short Build Up
#         return "Short"
# @memoize
def oi_activity(coi, chgprice):
    if coi is None or chgprice is None:
        return None

    conditions = {
        (coi > 0 and chgprice >= 0): "Long",
        (coi < 0 and chgprice <= 0): "Unwinding",
        (coi < 0 and chgprice >= 0): "Short Covering",
        (coi > 0 and chgprice <= 0): "Short"
    }
    
    return conditions.get(True, None)

def longshort(data):
    processed_data = []
    previous_data = None

    for index, data in enumerate(data):
        
        if index == 0:
            previous_data = data
        else:
            new_data = {
                "time": (data["time"]),
                "celtp": data["celtp"],
                "cecoi": data['cecoi'],
                "peltp": data["peltp"],
                "pecoi": data['pecoi'],
                "cepdroc": data['ceprmdecay']-previous_data['ceprmdecay'],
                "pepdroc": data['peprmdecay']-previous_data['peprmdecay'],
                "ceivroc": data['ceiv']-previous_data['ceiv'],
                "peivroc": data['peiv']-previous_data['peiv'],
                "cp": data["cp"],
                "previous_peltp": previous_data["peltp"],
                "pediff": (data["peltp"] - previous_data["peltp"]),
                "pestatus": oi_status(True, data['pecoi'], (data["peltp"] - previous_data["peltp"])),
                "cediff": (data["celtp"] - previous_data["celtp"]),
                "cestatus": oi_status(True, data['cecoi'], (data["celtp"] - previous_data["celtp"]))
            }
            processed_data.append(new_data)
            previous_data = data
    
    return processed_data

# @memoize
def cedecay(ltp, sp, csp):
    return ((ltp + abs((sp) - csp))/sp) * 100

# @memoize
def pedecay(ltp, sp, csp):
    return ((ltp - abs(sp - csp))/sp) * 100


# def cedecay(ltp, sp, csp):
#     if(csp > sp):
#         return ((ltp - (csp - sp))/sp)*100
#     else:
#         return ((ltp + (sp - csp))/sp)*100

# def pedecay(ltp, sp, csp):
#     if(csp > sp):
#         return ((ltp + (csp - sp))/sp)*100
#     else:
#         return ((ltp - (sp - csp))/sp)*100


def oi_status(ce = True, coi = 1, chgprice = 1):
    if(ce == True):
        if(coi >= 0 and chgprice >= 0):
            # Buyer - Long BuildUp
            return "Long"
        
        if(coi <= 0 and chgprice <= 0):
            # Buyer - Long Unwinding
            return "Unwinding"
        
        if(coi <= 0 and chgprice >= 0):
            # Seller - Short Covering
            return "Short Covering"
        
        if(coi >= 0 and chgprice <= 0):
            # Seller - Short Build Up
            return "Short"

    else:
        if(coi >= 0 and chgprice >= 0):
            # Buyer - Long BuildUp
            return "Long"
        
        if(coi <= 0 and chgprice <= 0):
            # Buyer - Long Unwinding
            return "Unwinding"
        
        if(coi <= 0 and chgprice >= 0):
            # Seller - Short Covering
            return "Short Covering"
        
        if(coi >= 0 and chgprice <= 0):
            # Seller - Short Build Up
            return "Short"

# def prmdecay(datalist, currentStrikePrice, formatted_timestamp):
def prmdecay(datalist, currentStrikePrice, formatted_timestamp):
    pdecay = []
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    for data in datalist:
        d={
            "celtp": data['CE']['lastPrice'],
            "cedecay": cedecay(data['CE']['lastPrice'], data['strikePrice'], currentStrikePrice ),
            "strikePrice": data['strikePrice'],
            "pedecay": pedecay(data['PE']['lastPrice'], data['strikePrice'], currentStrikePrice ),
            "peltp": data['PE']['lastPrice'],
            "time": formatted_timestamp
        }
        pdecay.append(d)

    return pdecay

def inmillion(n):
    return f"({round(abs(n)/1000000, 2)})" if n < 0 else round(n/1000000, 2)

def get_nifty_data(ssp=None):
    payload=nse_optionchain_scrapper('NIFTY')
    expiryDate=payload['records']['expiryDates'][0]
    listofstrikeprices = [payload['records']['strikePrices']][0]
    cp = payload['records']['underlyingValue']
    currentStrikePrice = int(cp) - ((int(cp)))%50
    newlistsp = [int(d) for d in listofstrikeprices if int(d) > (currentStrikePrice-249) and int(d) < (currentStrikePrice+251)]
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    sdata = []
    if ssp:
        sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]

    # print("ssp", ssp)
    # if ssp is not None:
    #    sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]
    # else:
    #   sdata = []
    oci_data = [d for d in payload['filtered']['data'] if (d['strikePrice']) > (currentStrikePrice-50) and d['strikePrice'] < (currentStrikePrice+50)]
    cdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == currentStrikePrice]]
    filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-199) and d['strikePrice'] < (currentStrikePrice+201)]
    # print(newlistsp)
    # return {
    #     "filter_data": filter_data,
    #     "cdata": cdata,
    #     "oci_data": oci_data, 
    #     "sdata": sdata,
    #     "currentStrikePrice" : currentStrikePrice, 
    #     "formatted_timestamp": formatted_timestamp, 
    #     "cp": cp, 
    #     "expiryDate": expiryDate,
    #     "listofsp": [19700, 19750, 19800, 19850, 19900, 19950]
    # }
    return {
        "filter_data": filter_data,
        "cdata": cdata,
        "oci_data": oci_data, 
        "sdata": sdata,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate,
        "listofsp": newlistsp
    }

def get_bnifty_data(ssp=None):
    payload=nse_optionchain_scrapper('BANKNIFTY')
    expiryDate=payload['records']['expiryDates'][0]
    listofstrikeprices = [payload['records']['strikePrices']][0]
    cp = payload['records']['underlyingValue']
    currentStrikePrice = int(cp) - ((int(cp)))%100
    newlistsp = [int(d) for d in listofstrikeprices if int(d) > (currentStrikePrice-399) and int(d) < (currentStrikePrice+401)]
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    sdata = []
    if ssp:
        sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]

    cdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == currentStrikePrice]]
    # filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-399) and d['strikePrice'] < (currentStrikePrice+401)]
    # Modify the list comprehension to include formatted_timestamp
    filter_data = [
        {**d, "formatted_timestamp": formatted_timestamp} 
        for d in payload['filtered']['data'] 
        if d['strikePrice'] > (currentStrikePrice - 399) and d['strikePrice'] < (currentStrikePrice + 401)
    ]
    return {
        "filter_data": filter_data,
        "cdata": cdata,
        "sdata": sdata,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate,
        "listofsp": newlistsp
    }

def get_finnifty_data(ssp=None):
    payload=nse_optionchain_scrapper('FINNIFTY')
    expiryDate=payload['records']['expiryDates'][0]
    listofstrikeprices = [payload['records']['strikePrices']][0]
    cp = payload['records']['underlyingValue']
    # currentStrikePrice = int(cp) - ((int(cp)))%50
    currentStrikePrice = int(cp) - int(cp) % 50
    # newlistsp = [int(d) for d in listofstrikeprices if int(d) > (currentStrikePrice-199) and int(d) < (currentStrikePrice+201)]
    newlistsp = [int(d) for d in list(listofstrikeprices) if (currentStrikePrice - 199) < int(d) < (currentStrikePrice + 201)]
    # print(newlistsp)
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    sdata = []
    if ssp:
        sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]

    # print("ssp", ssp)
    # if ssp is not None:
    #    sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]
    # else:
    #   sdata = []

    cdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == currentStrikePrice]]
    filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-199) and d['strikePrice'] < (currentStrikePrice+201)]
    return {
        "filter_data": filter_data,
        "cdata": cdata,
        "sdata": sdata,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate,
        "listofsp": newlistsp,
        "ls": listofstrikeprices
    }

def get_midcpnifty_data(ssp=None):
    payload=nse_optionchain_scrapper('MIDCPNIFTY')
    expiryDate=payload['records']['expiryDates'][0]
    listofstrikeprices = [payload['records']['strikePrices']][0]
    cp = payload['records']['underlyingValue']
    # currentStrikePrice = int(cp) - ((int(cp)))%50
    currentStrikePrice = int(cp) - int(cp) % 25
    # newlistsp = [int(d) for d in listofstrikeprices if int(d) > (currentStrikePrice-199) and int(d) < (currentStrikePrice+201)]
    newlistsp = [int(d) for d in list(listofstrikeprices) if (currentStrikePrice - 199) < int(d) < (currentStrikePrice + 201)]
    # print(newlistsp)
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    sdata = []
    if ssp:
        sdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == ssp]]

    cdata = [formatted_timestamp, [data for data in payload['filtered']['data'] if data['strikePrice'] == currentStrikePrice]]
    filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-199) and d['strikePrice'] < (currentStrikePrice+201)]
    return {
        "filter_data": filter_data,
        "cdata": cdata,
        "sdata": sdata,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate,
        "listofsp": newlistsp,
        "ls": listofstrikeprices
    }


def get_stock_data(lotsize=50, multiplier=5, stock = 'RELIANCE'):
    payload=nse_optionchain_scrapper(stock)
    expiryDate=payload['records']['expiryDates'][0]
    listofstrikeprices = [payload['records']['strikePrices']][0]
    cp = payload['records']['underlyingValue']
    currentStrikePrice = int(cp) - ((int(cp)))%(lotsize)
    newlistsp = [int(d) for d in listofstrikeprices if int(d) > (currentStrikePrice-(lotsize*multiplier - 1)) and int(d) < (currentStrikePrice+(lotsize*multiplier + 1))]
    timestamp = payload['records']['timestamp']
    datetime_obj = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime("%H:%M:%S")
    filter_data = [d for d in payload['filtered']['data'] if d['strikePrice'] > (currentStrikePrice-(lotsize*multiplier - 1)) and d['strikePrice'] < (currentStrikePrice+(lotsize*multiplier + 1))]
    
    return {
        "filter_data": filter_data,
        "currentStrikePrice" : currentStrikePrice, 
        "formatted_timestamp": formatted_timestamp, 
        "cp": cp, 
        "expiryDate": expiryDate,
        "listofsp": newlistsp
    }


def getvoi(a, b):
    return round((int(a) / b if b != 0 else 0),3)

def ndata(filter_data, timestamp="", currentStrikePrice="", cp=""):
    new_arr = []
    currentStrikePrice = get_nifty_data()['currentStrikePrice']
    for dd in filter_data:
        # "cescore" : ((getvoi(dd['CE']['changeinOpenInterest'], dd['CE']['totalTradedVolume'])) / (getvoi(dd['CE']['changeinOpenInterest'], dd['CE']['totalTradedVolume'])).max() * 0.3) + (dd['CE']['impliedVolatility'] / dd['CE']['impliedVolatility'].max() * 0.25) + ((cedecay(dd['CE']['lastPrice'], dd['strikePrice'], currentStrikePrice)) / (cedecay(dd['CE']['lastPrice'], dd['strikePrice'], currentStrikePrice)).max() * 0.3) + (round(int(dd['CE']['openInterest'])*50) / round(int(dd['CE']['openInterest'])*50).max() * 0.15),
        new_data = {
            "cp": cp,
            "strikePrice": dd['strikePrice'],
            "time": timestamp[0:5],
            "ceiv": dd['CE']['impliedVolatility'],
            "celtp": dd['CE']['lastPrice'],
            "celtpchg": dd['CE']['change'] or '',
            "ceoi" : round(int(dd['CE']['openInterest'])*50),
            "cecoi": round(int(dd['CE']['changeinOpenInterest'])),
            "cecoip": dd['CE']['pchangeinOpenInterest'],
            "cettvol": dd['CE']['totalTradedVolume'],
            "cestatus": oi_status(True, dd['CE']['changeinOpenInterest'], dd['CE']['change']),
            "ceprmdecay": cedecay(dd['CE']['lastPrice'], dd['strikePrice'], currentStrikePrice),
            "cevoi": round((int(dd['CE']['changeinOpenInterest']) / dd['CE']['totalTradedVolume'] if dd['CE']['totalTradedVolume'] != 0 else 0),3),
            "cecoivol": getvoi(dd['CE']['changeinOpenInterest'], dd['CE']['totalTradedVolume']),
            "peiv": dd['PE']['impliedVolatility'],
            "peltp": dd['PE']['lastPrice'],
            "peltpchg": dd['PE']['change'] or '',
            "peoi" : round(int(dd['PE']['openInterest'])*50),
            "pecoi": round(int(dd['PE']['changeinOpenInterest'])),
            "pecoip": dd['PE']['pchangeinOpenInterest'],
            "pettvol": dd['PE']['totalTradedVolume'],
            "pestatus": oi_status(False, dd['PE']['changeinOpenInterest'], dd['PE']['change']),
            "peprmdecay": pedecay(dd['PE']['lastPrice'], dd['strikePrice'], currentStrikePrice ),
            "pevoi": round((int(dd['PE']['changeinOpenInterest']) / dd['PE']['totalTradedVolume'] if dd['PE']['totalTradedVolume'] != 0 else 0),3),
            "pecoivol": round((int(dd['PE']['changeinOpenInterest']) / dd['PE']['totalTradedVolume'] if dd['PE']['totalTradedVolume'] != 0 else 0),3),
        }
        new_arr.append(new_data)
    return new_arr

def calculate_voi(dd):
    voi_ce = round((int(dd['CE']['changeinOpenInterest']) / dd['CE']['totalTradedVolume']) if dd['CE']['totalTradedVolume'] != 0 else 0, 3)
    voi_pe = round((int(dd['PE']['changeinOpenInterest']) / dd['PE']['totalTradedVolume']) if dd['PE']['totalTradedVolume'] != 0 else 0, 3)
    return voi_ce, voi_pe

def calculate_coivol(dd):
    coivol_ce = round((int(dd['CE']['changeinOpenInterest']) / dd['CE']['totalTradedVolume']) if dd['CE']['totalTradedVolume'] != 0 else 0, 3)
    coivol_pe = round((int(dd['PE']['changeinOpenInterest']) / dd['PE']['totalTradedVolume']) if dd['PE']['totalTradedVolume'] != 0 else 0, 3)
    return coivol_ce, coivol_pe

def voi(filter_data, timestamp=""):
    new_arr = []
    for dd in filter_data:
        voi_ce, voi_pe = calculate_voi(dd)
        coivol_ce, coivol_pe = calculate_coivol(dd)
        new_data = {
            "strikePrice": dd['strikePrice'],
            "time": timestamp,
            "CE": {
                "impliedVolatility": dd['CE']['impliedVolatility'],
                "openInterest": int(dd['CE']['openInterest'])*50,
                "totalTradedVolume": dd['CE']['totalTradedVolume'],
                "coi": int(dd['CE']['changeinOpenInterest']),
                "pcoi": dd['CE']['pchangeinOpenInterest'],
                "ltpch": dd['CE']['change'],
                "pltpch": dd['CE']['pChange'],
                "voi": voi_ce,
                "coivol": coivol_ce
            },
            "PE": {
                "impliedVolatility": dd['PE']['impliedVolatility'],
                "openInterest": int(dd['PE']['openInterest'])*50,
                "totalTradedVolume": dd['PE']['totalTradedVolume'],
                "coi": int(dd['PE']['changeinOpenInterest']),
                "pcoi": dd['PE']['pchangeinOpenInterest'],
                "ltpch": dd['PE']['change'],
                "pltpch": dd['PE']['pChange'],
                "voi": voi_pe,
                "coivol": coivol_pe
            }
        }
        new_arr.append(new_data)
    return new_arr

def nse_optionchain_ltp(payload,strikePrice,optionType,inp=0,intent=""):
    expiryDate=payload['records']['expiryDates'][inp]
    for x in range(len(payload['records']['data'])):
      if((payload['records']['data'][x]['strikePrice']==strikePrice) & (payload['records']['data'][x]['expiryDate']==expiryDate)):
          if(intent==""): return payload['records']['data'][x][optionType]['lastPrice']
          if(intent=="sell"): return payload['records']['data'][x][optionType]['bidprice']
          if(intent=="buy"): return payload['records']['data'][x][optionType]['askPrice']

def get_oc_live(symbol, expiry_date, strike_price1):
    # Get the current time and round it to the nearest minute
    now = datetime.now()
    now = now.replace(second=0, microsecond=0)

    # Fetch the option chain for the specified symbol and expiry date
    option_chain = pd.DataFrame(get_history(symbol=symbol, start=now, end=now, index=True, expiry_date=expiry_date, option_type='CE', strike_price=strike_price1))

    # Print the option chain data
    return (option_chain)

def unique_sp(data):
    strike_prices = []
    for lst in data:
        for dct in lst:
            if (dct["strikePrice"]) not in (strike_prices):
                strike_prices.append((dct["strikePrice"]))
    return strike_prices

def filter_oidata(data, cp=""):
    strike_prices = []
    # ccp = get_nifty_data()['cp']
    for lst in data:
        for dct in lst:
            obj = {"cp": cp, "strikePrice": dct['strikePrice'], "time": dct['time'], "celtp": dct['celtp'], "cestatus": dct['cestatus'], "celtpchg": dct['celtpchg'], "ceiv": dct['ceiv'], "cecoi": dct['cecoi'], "ceoi": dct['ceoi'], "cecoip": dct['cecoip'], "cettvol": dct['cettvol'], "cevoi": dct['cevoi'], "ceprmdecay": dct['ceprmdecay'], "pecoi": dct['pecoi'], "pestatus": dct['pestatus'], "peiv": dct['peiv'], "pecoip": dct['pecoip'], "pettvol": dct['pettvol'], "peprmdecay": dct['peprmdecay'], "pevoi": dct['pevoi'], "peoi": dct['peoi'], "peltpchg": dct['peltpchg'], "peltp": dct['peltp']}
            strike_prices.append(obj)
    return strike_prices

# nifty50 = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
# banknifty = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
# niftyit = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20IT"

# def get_data(url):
#     data = nsefetch(url)
#     # data1 = pd.DataFrame(data)
#     return data['data']

# def get_eq_mf():
#     totalmf = 0
#     for d in get_data(nifty50):
#         if (d['priority'] == 0):
#             totalmf += int(d['totalTradedValue']/10000000)
#     return totalmf

# def get_nifty_mf():
#     totalmf = 0
#     for d in get_data(nifty50):
#         if (d['priority'] == 1):
#             totalmf += int(d['totalTradedValue']/10000000)
#     return totalmf

# def get_bank_mf():
#     totalmf = 0
#     for d in get_data(banknifty):
#         if (d['priority'] == 0):
#             totalmf += int(d['totalTradedValue']/10000000)
#     return totalmf

# def get_banknifty_mf():
#     totalmf = 0
#     for d in get_data(banknifty):
#         if (d['priority'] == 1):
#             totalmf += int(d['totalTradedValue']/10000000)
#     return totalmf    
def display_chart_2d2(data, x, y1, r2, clr, title="Bar Chart"):
    df = pd.DataFrame(data)
    bar_y2 = (
        alt.Chart(df, title=str(f'{title}'))
        .mark_bar(color=str(clr))
        .encode(
            x=x,
            y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(r2), str(y1)],
        )
    )

    # Text labels for bar values
    text_y2 = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom")
        .encode(
            x=x,
            y=r2,
            text=(r2),
        )
    )

    # Line chart for y1 (blue)
    line_y1 = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r2)],
        )
    )

    # text_y1 = (
    #     alt.Chart(df)
    #     .mark_text(align="center", baseline="top")
    #     .encode(
    #         x=x,
    #         y=y1,
    #         text=(y1),
    #     )
    # )


    # Combine line, bar, and text charts
    # chart = (line_y1 + bar_y2 + text_y2).configure_axis(labelFontSize=12)
    chart = (line_y1 + bar_y2 ).resolve_scale(y="independent").configure_axis(labelFontSize=10)
    return chart


def display_chart_2d22(data, x, y1, r2, clr, title="Bar Chart"):
    df = pd.DataFrame(data)
    bar_y2 = (
        alt.Chart(df, title=str(f'{title}'))
        .mark_line(color=str(clr), strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(r2), str(y1)],
        )
    )

    # Text labels for bar values
    text_y2 = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom")
        .encode(
            x=x,
            y=r2,
            text=(r2),
        )
    )

    # Line chart for y1 (blue)
    line_y1 = (
        alt.Chart(df)
        .mark_line(color="#666666", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r2)],
        )
    )

    zero_line = (
        alt.Chart(pd.DataFrame({'z': [0]}))
        .mark_rule(color='#666666', strokeWidth=1)
        .encode(y='z:Q')
    )

    # text_y1 = (
    #     alt.Chart(df)
    #     .mark_text(align="center", baseline="top")
    #     .encode(
    #         x=x,
    #         y=y1,
    #         text=(y1),
    #     )
    # )


    # Combine line, bar, and text charts
    # chart = (line_y1 + bar_y2 + text_y2).configure_axis(labelFontSize=12)
    chart = (line_y1 + bar_y2 + zero_line).resolve_scale(y="independent").configure_axis(labelFontSize=10)
    return chart
    # Combine line and bar charts
    # chart = line_y1 + bar_y2

    # st.altair_chart(chart, use_container_width=True)


def display_chart_2d(data, x, y1, r2, clr, title="Bar Chart"):
    df = pd.DataFrame(data)
    bar_y2 = (
        alt.Chart(df, title=str(title))
        .mark_bar(color=str(clr))
        .encode(
            x=x,
            y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(r2), str(y1)],
        )
    )

    # Text labels for bar values
    text_y2 = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom")
        .encode(
            x=x,
            y=r2,
            text=(r2),
        )
    )

    # Line chart for y1 (blue)
    line_y1 = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=2)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(r2)],
        )
    )

    # text_y1 = (
    #     alt.Chart(df)
    #     .mark_text(align="center", baseline="top")
    #     .encode(
    #         x=x,
    #         y=y1,
    #         text=(y1),
    #     )
    # )


    # Combine line, bar, and text charts
    # chart = (line_y1 + bar_y2 + text_y2).configure_axis(labelFontSize=12)
    chart = (line_y1 + bar_y2 ).resolve_scale(y="independent").configure_axis(labelFontSize=10)

    # Combine line and bar charts
    # chart = line_y1 + bar_y2

    st.altair_chart(chart, use_container_width=True)

def get_timechart_sp(data,type='ceoi', title="Time Series"):
    data = pd.DataFrame(data)
    color = alt.Color("sp:N")
    hover = alt.selection_single(
        fields=["time"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title=title)
        .mark_line()
        .encode(
            x="time",
            y=type,
            color=color,
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="time",
            y=type,
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("time", title="time"),
                alt.Tooltip(str(type), title=str(type)),
                alt.Tooltip("sp", title="StrikePrice"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

def oci_bar_chart(data, x, y1, y2, r2, title="OCI Chart"):
    df = pd.DataFrame(data[-200:])
    line_y1 = (
        alt.Chart(df)
        .mark_line(color="green", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
            color=alt.ColorValue("green")  # Set color for y1
        )
    )

    line_y2 = (
        alt.Chart(df)
        .mark_line(color="red", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(y2, axis=alt.Axis(title=str(y2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
            color=alt.ColorValue("red")  # Set color for y1
        )
    )

    # Line chart for r2 (red)
    line_r2 = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
        )
    )

    chart = alt.layer(line_y1, line_y2, line_r2).resolve_scale(y="independent").configure_axis(labelFontSize=10)
    # line_y1 = (
    #     alt.Chart(df)
    #     .mark_line(color="green", strokeWidth=1)
    #     .encode(
    #         x=x,
    #         y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
    #         tooltip=[str(x), str(y1), str(r2)],
    #     )
    # )

    # # Line chart for y1 (blue)
    # line_y2 = (
    #     alt.Chart(df)
    #     .mark_line(color="red", strokeWidth=1)
    #     .encode(
    #         x=x,
    #         y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
    #         tooltip=[str(x), str(y1), str(r2)],
    #     )
    # )

    # Line chart for y1 (green)
    # line_y1 = (
    #     alt.Chart(df)
    #     .mark_line(color="green", strokeWidth=1)
    #     .encode(
    #         x=x,
    #         y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
    #         tooltip=[str(x), str(y1), str(y2), str(r2)],
    #     )
    # )

    # # Line chart for y2 (blue)
    # line_y2 = (
    #     alt.Chart(df)
    #     .mark_line(color="red", strokeWidth=1)
    #     .encode(
    #         x=x,
    #         y=alt.Y(y2, axis=alt.Axis(title=str(y2)), scale=alt.Scale(zero=False)),
    #         tooltip=[str(x), str(y1), str(y2), str(r2)],
    #     )
    # )

    # # Line chart for r2 (red)
    # line_r2 = (
    #     alt.Chart(df)
    #     .mark_line(color="blue", strokeWidth=1)
    #     .encode(
    #         x=x,
    #         y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
    #        tooltip=[str(x), str(y1), str(y2), str(r2)],
    #     )
    # )

    # chart = (line_y1 + line_y2 + line_r2).resolve_scale(y="independent").configure_axis(labelFontSize=10)
    return chart

def oci_line_chart(data, x, y1, y2, r2, title="OCI Chart"):
    df = pd.DataFrame(data)
    
    line_y1 = (
        alt.Chart(df)
        .mark_line(color="green", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(y1, axis=alt.Axis(title=str(y1)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
            color=alt.ColorValue("green")  # Set color for y1
        )
        
    )

    text_y1 = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom")
        .encode(
            x=x,
            y=y1,
            text=(y1),
        )
    )

    bar_y2 = (
        alt.Chart(df)
        .mark_bar(color="red", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(y2, axis=alt.Axis(title=str(y2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
            color=alt.ColorValue("red")  # Set color for y1
        )
    )

    text_y1 = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom")
        .encode(
            x=x,
            y=y2,
            text=(y2),
        )
    )

    line_y2 = (
        alt.Chart(df)
        .mark_line(color="red", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(y2, axis=alt.Axis(title=str(y2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
            color=alt.ColorValue("red")  # Set color for y1
        )
    )

    # Line chart for r2 (red)
    line_r2 = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=1)
        .encode(
            x=x,
            y=alt.Y(r2, axis=alt.Axis(title=str(r2)), scale=alt.Scale(zero=False)),
            tooltip=[str(x), str(y1), str(y2), str(r2)],
        )
    )

    chart = alt.layer(line_y1, line_y2, line_r2).resolve_scale(y="independent").configure_axis(labelFontSize=10)
    return chart

def oi_alarm(oi, oi_first):
    # Check your condition and return True or False accordingly
    if oi > oi_first:
        return False
    else:
        return True


def get_dbdata(db_string, db_name, db_collection, strikeprice, type):
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]

    cursorce=collection.find({'strikeprice': strikeprice, 'index': 'NIFTY','type': type },{'_id':0,'timestamp':1, 'nftyltp':1, 'last_price':1, 'strikeprice':1, 'volume':1, 'oi':1, 'iv':1,'delta':1,'rho':1, 'gamma':1,'theta':1,'strikeprice':1, 'type':1})
    dfp =  pd.DataFrame(list(cursorce))
    dfp['volume']  = (dfp['volume'] / 50)
    dfp['timestamp'] = dfp['timestamp'].str[-8:]

    dfp['ltpdiff'] = dfp['last_price'].diff()

    dfp['csp'] = (dfp['nftyltp']) - (((dfp['nftyltp'])))%50
    if(type == 'CE'):
        dfp['prmdecay'] = (dfp.apply(lambda row: cedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1)).pct_change()*100
    else:
        dfp['prmdecay'] = (dfp.apply(lambda row: pedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1)).pct_change()*100
    
    dfp['iv'] = pd.to_numeric(dfp['iv'], errors='coerce')
    dfp['iv_roc'] = dfp['iv'].pct_change()*100
    
    oi_base=dfp.iloc[0:1,3].mean()
    vol_base=dfp.iloc[0:1,2].mean()

    dfp['cvol']=dfp['volume']-vol_base
    dfp['coi']=dfp['oi']-oi_base
    dfp['nt'] = dfp['volume']/dfp['last_price']
    dfp['coibnt'] = dfp['coi']/dfp['nt']
    dfp['coidv'] = dfp['coi']/dfp['cvol']

    dfp['cvoldff']=dfp['volume'].diff()
    dfp['coidff']=dfp['oi'].diff()
    dfp['coidvff'] = dfp['coidff']/dfp['volume']

    dfp['action'] = dfp.apply(lambda row: oi_activity(row['coi'], row['ltpdiff']), axis=1)

    sum_of_long = sum([row['coi'] for _, row in dfp.iterrows() if row['action'] == 'Long'])
    sum_of_short = sum([row['coi'] for _, row in dfp.iterrows() if row['action'] == 'Short'])
    sum_of_unwinding = sum([row['coi'] for _, row in dfp.iterrows() if row['action'] == 'Unwinding'])
    sum_of_short_covering = sum([row['coi'] for _, row in dfp.iterrows() if row['action'] == 'Short Covering'])
    # lsratio = str("Long - ", sum_of_long/1, ", Short - ",sum_of_short/1, ", Short Covering - ", sum_of_short_covering/1, ", Unwinding - ", sum_of_unwinding/1,  ", L/s(Millions) - ", (sum_of_long - sum_of_short)/1000000)
    # print(lsratio)
    return {
        "dfp": dfp,
        "long": sum_of_long,
        "short": sum_of_short,
        "unwinding": sum_of_unwinding,
        "scovering": sum_of_short_covering,
        "last_updated": dfp['timestamp'],
        "niftyltp": dfp['nftyltp'],
        "csp": dfp['csp']
    }

# @memoize
def get_mf_opv2(strikeprice, type, idx):
    dfce = pd.DataFrame()
    kite=connectZerodha()
    
    # FOR LAST WEEK OF EXPIRY MONTH
    # expiryforinstr = '23JUN'
    # FOR REGULAR WEEK'S EXPIRY
    
    indx = idx
    if(idx == 'FINNIFTY'):
        expiryforinstr=config.expiryforinstr_fin
    else:
        expiryforinstr=config.expiryforinstr
    indxCE = 'NFO:' + indx + expiryforinstr + str(strikeprice) + type  

    to_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    from_date = datetime.today().strftime("%Y-%m-%d") + " 09:15:00"

    # to_date = (datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d %H:%M:%S")
    # from_date = (datetime.today() - timedelta(days = 1)).strftime("%Y-%m-%d") + " 09:15:00"
    
    # from_date = "2023-07-28 9:15:00"
    # to_date="2023-07-28 15:30:00"

    token = kite.quote(indxCE)[indxCE]['instrument_token']
    # print(token)
    dfce = pd.DataFrame(list(kite.historical_data(token, from_date, to_date, "minute", False, True)))
    dfce['time'] = pd.to_datetime(dfce['date'], format='%d|%m|%Y').dt.strftime('%H:%M:%S')
    dfce['strikeprice'] = strikeprice
    oi_first = dfce['oi'].iloc[0]
    dfce['alarm'] = dfce.apply(lambda row: oi_alarm(row['oi'], oi_first), axis=1)
    # sel_col = ['time', 'MF', 'oi', 'alarm']
    # dd = dfce[sel_col]
    # print(dfce)
    df = moneyflow_hist(dfce)
    # print(df)
    # print("data fetched from get_mf_opv2")
    # dfce['time'] = pd.to_datetime(dfce['date'], format='%d|%m|%Y').dt.strftime('%H:%M:%S')
    # dfce['Avgpr'] = (dfce['high'] + dfce['low']) / 2   
    # dfce['MFCr'] = dfce['Avgpr'] * dfce['volume'] / 10000000
    # dfce['MFStus'] = dfce['close'] - dfce['open']
    # dfce['MFCrS'] = np.sign(dfce['MFStus'])
    # dfce['MFCrS1'] = dfce['MFCrS']
    # dfce['cvol'] = dfce['volume'].diff()
    # dfce['MFCrS1'] = dfce['MFCrS'].replace(0, np.nan).ffill().fillna(0)
    # dfce['MFCr'] = dfce['MFCr'] * dfce['MFCrS1']
    # dfce['MFCr1'] = dfce['MFCr'].cumsum()

    return df

def get_mf_fut(instrument):
    dfce = pd.DataFrame()
    kite=connectZerodha()
    
    to_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    from_date = datetime.today().strftime("%Y-%m-%d") + " 09:15:00"
    
    # from_date = "2023-07-28 9:15:00"
    # to_date="2023-07-28 15:30:00"

    # from_date = "2023-07-12 9:15:00"
    # to_date="2023-07-12 15:30:00"

    token = kite.quote(instrument)[instrument]['instrument_token']
    # print(token)
    dfce = pd.DataFrame(list(kite.historical_data(token, from_date, to_date, "minute", False, True)))
    dfce['time'] = pd.to_datetime(dfce['date'], format='%d|%m|%Y').dt.strftime('%H:%M:%S')
    dfce['instrument'] = instrument
    oi_first = dfce['oi'].iloc[0]
    dfce['alarm'] = dfce.apply(lambda row: oi_alarm(row['oi'], oi_first), axis=1)
    df = moneyflow_hist(dfce)
    sel_col = ['time', 'oi', 'MF', 'alarm', 'volume']
    return df[sel_col]

def get_mf_cash(token):
    dfce = pd.DataFrame()
    kite=connectZerodha()
    
    to_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    from_date = datetime.today().strftime("%Y-%m-%d") + " 09:15:00"
    
    # from_date = "2023-06-30 9:15:00"
    # to_date="2023-06-30 15:30:00"

    # token = kite.quote(instrument)[instrument]['instrument_token']
    # print(token)
    dfce = pd.DataFrame(list(kite.historical_data(token, from_date, to_date, "minute", False, True)))
    dfce['time'] = pd.to_datetime(dfce['date'], format='%d|%m|%Y').dt.strftime('%H:%M:%S')
    dfce['instrument'] = token
    oi_first = dfce['oi'].iloc[0]
    dfce['alarm'] = dfce.apply(lambda row: oi_alarm(row['oi'], oi_first), axis=1)
    df = moneyflow_hist(dfce)
    sel_col = ['timestamp', 'time', 'oi', 'MF', 'alarm', 'volume']
    return df[sel_col]


# @memoize
def get_data(db_string, db_name, db_collection, strikeprice, type):
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]

    projection = {
        '_id': 0,
        'timestamp': 1,
        'nftyltp': 1,
        'last_price': 1,
        'strikeprice': 1,
        'volume': 1,
        'oi': 1,
        'iv': 1,
        'type': 1
    }

    query = {
        'strikeprice': strikeprice,
        'index': 'NIFTY',
        'type': type
    }

    cursor = collection.find(query, projection)
    dfp = pd.DataFrame(list(cursor))
    
    dfp['volume'] /= 50
    dfp['timestamp'] = dfp['timestamp'].str[-8:]
    dfp['ltpdiff'] = dfp['last_price'].diff()
    dfp['csp'] = dfp['nftyltp'] - (dfp['nftyltp'] % 50)

    if type == 'CE':
        dfp['prmdecay'] = dfp.apply(lambda row: cedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100
    else:
        dfp['prmdecay'] = dfp.apply(lambda row: pedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100

    dfp['iv'] = pd.to_numeric(dfp['iv'], errors='coerce')
    dfp['iv_roc'] = dfp['iv'].pct_change() * 100

    oi_base = dfp.iloc[0, 3]
    vol_base = dfp.iloc[0, 2]
    dfp['cvol'] = dfp['volume'] - vol_base
    dfp['coi'] = dfp['oi'] - oi_base
    dfp['nt'] = dfp['volume'] / dfp['last_price']
    dfp['coibnt'] = (dfp['coi'] / dfp['nt']).pct_change() * 100
    dfp['coidv'] = dfp['coi'] / dfp['cvol']

    dfp['cvoldff'] = dfp['volume'].diff()
    dfp['coidff'] = dfp['oi'].diff()
    dfp['coidvff'] = dfp['coidff'] / dfp['volume']

    dfp['action'] = dfp.apply(lambda row: oi_activity(row['coi'], row['ltpdiff']), axis=1)
    

    sum_of_long = dfp.loc[dfp['action'] == 'Long', 'coi'].sum()
    sum_of_short = dfp.loc[dfp['action'] == 'Short', 'coi'].sum()
    sum_of_unwinding = dfp.loc[dfp['action'] == 'Unwinding', 'coi'].sum()
    sum_of_short_covering = dfp.loc[dfp['action'] == 'Short Covering', 'coi'].sum()

    return {
        "dfp": dfp,
        "long": sum_of_long,
        "short": sum_of_short,
        "unwinding": sum_of_unwinding,
        "scovering": sum_of_short_covering,
        "last_updated": dfp['timestamp'],
        "niftyltp": dfp['nftyltp'],
        "csp": dfp['csp']
    }

# Define the oi_activity function

def get_all_data(db_string, db_name, db_collection, idx, strikeprice, type):
    # print((strikeprice))
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]
 
    query = {
        'strikeprice': strikeprice,
        'index': idx,
        'type': type
    }

    cursor = collection.find(query)
    dfp = pd.DataFrame(list(cursor))

    # print(dfp.iloc[1])        

    dfp['volume'] /= 50
    dfp['timestamp'] = dfp['timestamp'].str[-8:]
    dfp['ltpdiff'] = dfp['last_price'].diff()
    # fnftyltp
    if(idx == 'FNIFTY'):
        dfp['csp'] = dfp['fnftyltp'] - (dfp['fnftyltp'] % 50)
    else:
        dfp['csp'] = dfp['nftyltp'] - (dfp['nftyltp'] % 50)

    if type == 'CE':
        dfp['prmdecay'] = dfp.apply(lambda row: cedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100
    else:
        dfp['prmdecay'] = dfp.apply(lambda row: pedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100

    dfp['iv'] = pd.to_numeric(dfp['iv'], errors='coerce')
    dfp['iv_roc'] = dfp['iv'].pct_change() * 100

    
    oi_base = dfp.iloc[0, 7]
    vol_base = dfp.iloc[0, 6]
    dfp['cvol'] = dfp['volume'] - int(vol_base)
    dfp['coi'] = dfp['oi'] - oi_base
    dfp['nt'] = dfp['volume'] / dfp['last_price']
    dfp['coibnt'] = (dfp['coi'] / dfp['nt']).pct_change() * 100
    dfp['coidv'] = dfp['coi'] / dfp['cvol']

    dfp['coivol'] = dfp['cvol']/dfp['volume']
    # dfp['coivol'] = []
    dfp['cvoldff'] = dfp['volume'].diff()
    dfp['coidff'] = dfp['oi'].diff()
    dfp['coidvff'] = dfp['coidff'] / dfp['volume']

    dfp['action'] = dfp.apply(lambda row: oi_activity(row['coidff'], row['ltpdiff']), axis=1)
    # dfp['alarm'] = False
    oi_first = dfp['oi'].iloc[0]
    dfp['alarm'] = dfp.apply(lambda row: oi_alarm(row['oi'], oi_first), axis=1)

    # Set the condition and update the 'alarm' column accordingly
    # dfp.loc[(dfp['timestamp'] >= pd.Timestamp('9:15')) & (dfp['oi'] > dfp['oi'].iloc[0]), 'alarm'] = True
    # dfp.loc[(dfp['oi'] > dfp['oi'].iloc[0]), 'alarm'] = True
    
    sum_of_long = dfp.loc[dfp['action'] == 'Long', 'oi'].sum()
    sum_of_short = dfp.loc[dfp['action'] == 'Short', 'oi'].sum()
    sum_of_unwinding = dfp.loc[dfp['action'] == 'Unwinding', 'oi'].sum()
    sum_of_short_covering = dfp.loc[dfp['action'] == 'Short Covering', 'oi'].sum()

    fniftyltp = ''
    if(idx == 'FNIFTY'):
        fniftyltp: dfp['fnftyltp']
    else:
        fniftyltp: dfp['nftyltp']

    return {
        "dfp": dfp,
        "long": sum_of_long,
        "short": sum_of_short,
        "unwinding": sum_of_unwinding,
        "scovering": sum_of_short_covering,
        "last_updated": dfp['timestamp'],
        "niftyltp": fniftyltp,
        "csp": dfp['csp']
    }
 
def get_oi_data(db_string, db_name, db_collection, idx='NIFTY', strikeprices=[18500], type='CE'):
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]
    # cursorpe = collection.aggregate([
    #     {
    #         '$match': {
    #             'strikeprice': {'$in': strikeprices},
    #             'index': idx,
    #             'type': 'PE'
    #         }
    #     },
    #     {
    #         '$group': {
    #             '_id': '$strikeprice',
    #             'total_oi': {'$sum': '$oi'}
    #         }
    #     },
    #     {
    #         '$project': {
    #             '_id': 0,
    #             'strikeprice': '$_id',
    #             'total_oi': 1
    #         }
    #     }
    # ])
    cursorpe = collection.aggregate([
        {
            '$match': {
                'strikeprice': {'$in': strikeprices},
                'index': idx,
                'type': type
            }
        },
        {
        '$group': {
                '_id': {
                    'timestamp': '$timestamp',
                    'strikeprice': '$strikeprice'
                },
                'total_oi': {'$sum': '$oi'}
            }
        },
        {
            '$project': {
                '_id': 0,
                'timestamp': '$_id.timestamp',
                'strikeprice': '$_id.strikeprice',
                'total_oi': 1
            }
        }
    ])
    dfstr = pd.DataFrame(list(cursorpe))
    # current_datetime = datetime.now()
    # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # dfstr['time'] = (formatted_datetime)[-8:]
    dfstr['time'] = dfstr['timestamp'].str[-8:]
    return dfstr


def get_oci_data(db_string, db_name, db_collection, idx='NIFTY', strikeprice=18500, type='CE'):
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]

    if(idx == 'BNIFTY'):
        query = {
            'strikeprice': {
                '$gte': strikeprice - 100,
                '$lte': strikeprice + 100
            },
            'index': idx,
            'type': type
        }
    elif(idx == 'FNIFTY'):   
        query = {
            'strikeprice': {
                '$gte': strikeprice - 100,
                '$lte': strikeprice + 100
            },
            'index': idx,
            'type': type
        } 
    else:
        query = {
            'strikeprice': {
                '$gte': strikeprice - 50,
                '$lte': strikeprice + 50
            },
            'index': idx,
            'type': type
        }
        
    cursor = collection.find(query)
    dfp = pd.DataFrame(list(cursor)) 
    
    dfp['volume'] /= 50
    dfp['timestamp'] = dfp['timestamp'].str[-8:]
    dfp['ltpdiff'] = dfp['last_price'].diff()

    if(idx == 'NIFTY'):
        dfp['csp'] = dfp['nftyltp'] - (dfp['nftyltp'] % 50) 
    elif(idx == 'FNIFTY'):
        dfp['csp'] = dfp['fnftyltp'] - (dfp['fnftyltp'] % 50)
    else:
        dfp['csp'] = dfp['bnftyltp'] - (dfp['bnftyltp'] % 100) 
    
    dfp['iv'] = pd.to_numeric(dfp['iv'], errors='coerce')
    oi_base = dfp.iloc[0, 7]
    vol_base = dfp.iloc[0, 6]
    dfp['cvol'] = dfp['volume'] - int(vol_base)
    dfp['coi'] = dfp['oi'] - oi_base

    dfp['coivol'] = dfp['coi']/dfp['volume']
    
    if type == 'CE':
        dfp['prmdecay'] = dfp.apply(lambda row: cedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100
    else:
        dfp['prmdecay'] = dfp.apply(lambda row: pedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100

    dfp['action'] = dfp.apply(lambda row: oi_activity(row['coi'], row['ltpdiff']), axis=1)
    
    sum_of_long = dfp.loc[dfp['action'] == 'Long', 'coi'].sum()
    sum_of_short = dfp.loc[dfp['action'] == 'Short', 'coi'].sum()
    sum_of_unwinding = dfp.loc[dfp['action'] == 'Unwinding', 'coi'].sum()
    sum_of_short_covering = dfp.loc[dfp['action'] == 'Short Covering', 'coi'].sum()

    return {
            "dfp":dfp,
            "long": sum_of_long,
            "short": sum_of_short,
            "unwinding": sum_of_unwinding,
            "scovering": sum_of_short_covering,
            }

def get_oci(db_string, db_name, db_collection, idx, strikeprice):
    # instr_nfty = dfp['strikeprice'].unique()  
    cedata = get_oci_data(db_string, db_name, db_collection, idx, strikeprice, 'CE')  
    dfce = cedata['dfp']
    celong = cedata['long']
    ceshort = cedata['short']
    ceunwinding = cedata['unwinding']
    cescovering = cedata['scovering']
    dfce['cescore'] = (dfce['coivol'] / dfce['coivol'].max() * 0.3) + (dfce['iv'] / dfce['iv'].max() * 0.25) + (dfce['prmdecay'] / dfce['prmdecay'].max() * 0.3) + (dfce['oi'] / dfce['oi'].max() * 0.15)
    dfce['cescore_roc'] = dfce['cescore'].pct_change() * 100
    
    pedata = get_oci_data(db_string, db_name, db_collection, idx, strikeprice, 'PE')  
    dfpe = pedata['dfp']
    pelong = pedata['long']
    peshort = pedata['short']
    peunwinding = pedata['unwinding']
    pescovering = pedata['scovering']
    dfpe['pescore'] = (dfpe['coivol'] / dfpe['coivol'].max() * 0.3) + (dfpe['iv'] / dfpe['iv'].max() * 0.25) + (dfpe['prmdecay'] / dfpe['prmdecay'].max() * 0.3) + (dfpe['oi'] / dfpe['oi'].max() * 0.15)
    dfpe['pescore_roc'] = (dfpe['pescore'].pct_change() * 100)

     
    # # Normalize the values
    # coi_volume_norm = dfp['coivol'] / dfp['coivol'].max()
    # iv_norm = dfp['iv'] / dfp['iv'].max()
    # premium_decay_norm = dfp['premium_decay'] / dfp['premium_decay'].max()
    # oi_norm = dfp['oi'] / dfp['oi'].max()

    # # Apply weightages
    # coi_volume_weighted = coi_volume_norm * 0.3
    # iv_weighted = iv_norm * 0.25
    # premium_decay_weighted = premium_decay_norm * 0.3
    # oi_weighted = oi_norm * 0.15

    # Calculate the overall score
    # overall_score = coi_volume_weighted + iv_weighted + premium_decay_weighted + oi_weighted
    dfoci = pd.DataFrame()
    dfoci['time'] = dfce['timestamp']
    
    if(idx == 'NIFTY'):
        dfoci['nftyltp'] = dfce['nftyltp']
    elif(idx == 'FNIFTY'):
        dfoci['fnftyltp'] = dfce['fnftyltp']
    else:
        dfoci['bnftyltp'] = dfce['bnftyltp']

    # dfoci['strikeprice'] = dfce['strikeprice']
    dfoci['cescore'] = dfce['cescore']
    dfoci['pescore'] = dfpe['pescore']
    dfoci['cescore_roc'] = dfce['cescore_roc']
    dfoci['pescore_roc'] = dfpe['pescore_roc']
    # dfoci['time'] = dfoci['time'].str[:5]
    # dfoci['cescore'] = dfoci.groupby('time')['cescore'].transform('sum')  
    # dfoci['pescore'] = dfoci.groupby('time')['pescore'].transform('sum')  
    # dfoci['cescore_roc'] = dfoci.groupby('time')['cescore_roc'].transform('sum')  
    # dfoci['pescore_roc'] = dfoci.groupby('time')['pescore_roc'].transform('sum')  
    # sum_df = dfoci.groupby('time')[['cescore', 'pescore', 'cescore_roc', 'pescore_roc']].sum().reset_index()

    # Merge the summed values DataFrame with the original DataFrame based on 'time' column
    # dfoci = dfoci.merge(sum_df, on='time', suffixes=('', '_sum'))
        
    return {
        "dfoci":dfoci.drop_duplicates(),
        "dfce": dfce,
        "dfpe": dfpe,
        "lsdata": {
            "celong": inmillion(celong),
            "pelong": inmillion(pelong),
            "ceshort": inmillion(ceshort),
            "peshort": inmillion(peshort),
            "ceunwinding": inmillion(ceunwinding),
            "peunwinding": inmillion(peunwinding),
            "cescovering": inmillion(cescovering),
            "pescovering": inmillion(pescovering)
        }
    }
 
# Define the base time-series chart.
def get_oi_chart(data, title):
    lines = (
        alt.Chart(data, title=f'{title}')
        .mark_line()
        .encode(
            x="time",
            y="oi",
            color="strikeprice",
        )
    )

    return (lines)

def oigraph(data, title):
    # colors = ['#FF0000', '#FF3333', '#FF6666', '#FF9999', '#FFCCCC', '#FF3333', '#FF6666', '#FF9999']
    cols = data.drop('time', axis=1).columns.tolist()
    trace1 = go.Scatter(x=data['time'], y=data[cols[0]], mode='lines+markers', marker=dict(color='#00FF00'), name=f'{cols[0]}', yaxis='y')
    trace2 = go.Scatter(x=data['time'], y=data[cols[1]], mode='lines+markers', marker=dict(color='#FF3333'), name=f'{cols[1]}', yaxis='y')
    trace3 = go.Scatter(x=data['time'], y=data[cols[2]], mode='lines+markers', marker=dict(color='#FF6666'), name=f'{cols[2]}', yaxis='y')    
    trace4 = go.Scatter(x=data['time'], y=data[cols[3]], mode='lines+markers', marker=dict(color='#FF9999'), name=f'{cols[3]}', yaxis='y')    
    trace5 = go.Scatter(x=data['time'], y=data[cols[4]], mode='lines+markers', marker=dict(color='#00FFCC'), name=f'{cols[4]}', yaxis='y')    
    trace6 = go.Scatter(x=data['time'], y=data[cols[5]], mode='lines+markers', marker=dict(color='#00FF33'), name=f'{cols[5]}', yaxis='y')    
    trace7 = go.Scatter(x=data['time'], y=data[cols[6]], mode='lines+markers', marker=dict(color='#00FF66'), name=f'{cols[6]}', yaxis='y')    
    trace8 = go.Scatter(x=data['time'], y=data[cols[7]], mode='lines+markers', marker=dict(color='#00FF99'), name=f'{cols[7]}', yaxis='y')    

    layout = go.Layout(title=f'{title}', xaxis=dict(title='Time'), yaxis=dict(title='OI'))
    fig = go.Figure(data=[trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8], layout=layout)
    return fig


# old function commented out in if condition
if (True):
    pass
    # def get_data_all(db_string, db_name, db_collection):
    #     client = pymongo.MongoClient(db_string)
    #     db = client[db_name]
    #     collection = db[db_collection]

    #     projection = {
    #         '_id': 0,
    #         'timestamp': 1,
    #         'nftyltp': 1,
    #         'last_price': 1,
    #         'strikeprice': 1,
    #         'volume': 1,
    #         'oi': 1,
    #         'iv': 1,
    #         'delta': 1,
    #         'rho': 1,
    #         'gamma': 1,
    #         'theta': 1,
    #         'type': 1
    #     }

    #     query = {
    #         'index': 'NIFTY',
    #         }

    #     cursor = collection.find(query, projection)
    #     dfp = pd.DataFrame(list(cursor))

    #     dfp['volume'] /= 50
    #     dfp['timestamp'] = dfp['timestamp'].str[-8:]
    #     dfp['ltpdiff'] = dfp['last_price'].diff()
    #     dfp['csp'] = dfp['nftyltp'] - (dfp['nftyltp'] % 50)

    #     if type == 'CE':
    #         dfp['prmdecay'] = dfp.apply(lambda row: cedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100
    #     else:
    #         dfp['prmdecay'] = dfp.apply(lambda row: pedecay(row['last_price'], row['strikeprice'], row['csp']), axis=1).pct_change() * 100

    #     dfp['iv'] = pd.to_numeric(dfp['iv'], errors='coerce')
    #     dfp['iv_roc'] = dfp['iv'].pct_change() * 100

    #     oi_base = dfp.iloc[0, 3]
    #     vol_base = dfp.iloc[0, 2]
    #     dfp['cvol'] = dfp['volume'] - vol_base
    #     dfp['coi'] = dfp['oi'] - oi_base
    #     dfp['nt'] = dfp['volume'] / dfp['last_price']
    #     dfp['coibnt'] = dfp['coi'] / dfp['nt']
    #     dfp['coidv'] = dfp['coi'] / dfp['cvol']

    #     dfp['cvoldff'] = dfp['volume'].diff()
    #     dfp['coidff'] = dfp['oi'].diff()
    #     dfp['coidvff'] = dfp['coidff'] / dfp['volume']

    #     dfp['action'] = dfp.apply(lambda row: oi_activity(row['coi'], row['ltpdiff']), axis=1)

    #     sum_of_long = dfp.loc[dfp['action'] == 'Long', 'coi'].sum()
    #     sum_of_short = dfp.loc[dfp['action'] == 'Short', 'coi'].sum()
    #     sum_of_unwinding = dfp.loc[dfp['action'] == 'Unwinding', 'coi'].sum()
    #     sum_of_short_covering = dfp.loc[dfp['action'] == 'Short Covering', 'coi'].sum()

    #     return {
    #         "dfp": dfp,
    #         "long": sum_of_long,
    #         "short": sum_of_short,
    #         "unwinding": sum_of_unwinding,
    #         "scovering": sum_of_short_covering,
    #         "last_updated": dfp['timestamp'],
    #         "niftyltp": dfp['nftyltp'],
    #         "csp": dfp['csp']
    #     }


def get_fu(db_string, db_name, db_collection):
    client = pymongo.MongoClient(db_string)
    db = client[db_name]
    collection = db[db_collection]

    cursor=collection.find({'_id':0,'timestamp':1,'last_price':1,'volume':1,'ohlc':1,'oi':1,'coi':1,'MF_fin':1,'nftyltp':1})
    dfeq =  pd.DataFrame(list(cursor))
    return dfeq

__all__ = ['voi', 
           'nse_optionchain_ltp', 
           'get_oc_live', 
           'generate_random_time', 
           'get_nifty_data', 
           'get_bnifty_data',
           'get_finnifty_data',
           'prmdecay', 
           'add_time_interval',
           'ndata',
           'unique_sp',
           'filter_oidata',
           'get_random',
           'oi_status',
           'longshort',
           'display_chart_2d',
           'get_timechart_sp',
           'get_fu',
           'display_chart_2d22',
           'inmillion',
           'get_oi_chart',
           'get_mf_opv2',
           'oigraph',
           'get_mf_fut',
           'get_mf_cash']





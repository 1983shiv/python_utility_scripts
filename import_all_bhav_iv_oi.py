import csv
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nse']
stocks_collection = db['stocks']

# Function to process OI data
def process_and_update_fut_oi_data(file_path, expiry, expiryNext, type):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # date = datetime.strptime(row['Date'].strip(), '%Y-%m-%d')
            expirydate = (row['XpryDt'])
            # expirydate = datetime.strptime(row['XpryDt'].strip(), '%Y-%m-%d')
            intrument = (row['FinInstrmTp'])
            if(intrument == type):
            # FinInstrmNm
                if(expirydate == expiry):
                    date = datetime.strptime(row['TradDt'].strip(), '%Y-%m-%d')
                    symbol = row['TckrSymb']
                    coi = int(float(row['ChngInOpnIntrst']))  # Parse coi as integer
                    oi = int(float(row['OpnIntrst']))  

                    # Construct expiry data
                    expiry_data = {
                        'expiry': expirydate,
                        'coi': coi,
                        'oi': oi
                    }
                    print(f'expiry: {expirydate} coi: {coi} and oi: {oi}')
                    # Update document in nsestocks collection ('%d-%b-%Y') %d-%m-%Y and '%Y-%m-%d'
                    query = {'symbol': symbol, 'date': date}
                    update = {
                        '$push': {
                            'drvt': {'$each': [expiry_data]}
                        }
                    }
                    stocks_collection.update_one(query, update)
                    # Update document in nsestocks collection ('%d-%b-%Y') and '%Y-%m-%d'
                    query = {'symbol': symbol, 'date': date}
                    update = {
                        '$set': {
                            'coi': coi,
                            'oi': oi,
                            'expiry': expiry
                        }
                    }
                    print(f'expiry: {expiry} coi: {coi} and oi: {oi}')
                    stocks_collection.update_one(query, update)
                    print(f'record update for - {date}')
                else:
                    print(f"some error occured {expirydate} and expiry {expiry}, {intrument} and {type} ")
                    pass

                if(expirydate == expiryNext):
                    date = datetime.strptime(row['TradDt'].strip(), '%Y-%m-%d')
                    symbol = row['TckrSymb']
                    coi = int(float(row['ChngInOpnIntrst']))  # Parse coi as integer
                    oi = int(float(row['OpnIntrst']))  

                    # Construct expiry data
                    expiry_data = {
                        'expiry': expirydate,
                        'coi': coi,
                        'oi': oi
                    }
                    print(f'expiry: {expiryNext} coi: {coi} and oi: {oi}')
                    # Update document in nsestocks collection ('%d-%b-%Y') and '%Y-%m-%d'
                    query = {'symbol': symbol, 'date': date}
                    update = {
                        '$push': {
                            'drvt': {'$each': [expiry_data]}
                        }
                    }
                    stocks_collection.update_one(query, update)
                    print(f'record update for - {date}')
                else:
                    print(f"some error occured {expirydate} and expiry {expiryNext}, {intrument} and {type} ")
                    pass

# Function to insert bhav data into mongodb
def insert_or_update_document(collection, document):
    collection.insert_one(document)
    print("New document inserted for date:", document['date'])
   
# Function to update iv data
def process_and_update_iv_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # date = datetime.strptime(row['Date'].strip(), '%Y-%m-%d')
            date = datetime.strptime(row['Date'].strip(), '%d-%b-%y') 
            symbol = row['Symbol']
            daily = None
            if row['a'] != '-':
                daily = round(float(row['a'])*100,2)
            yearly = None
            if row['b'] != '-':
                yearly = round(float(row['b'])*100,2)


            # Update document in nsestocks collection ('%d-%b-%Y') and '%Y-%m-%d'
            query = {'symbol': symbol, 'date': date}
            update = {
                '$set': {
                    'iv_daily': daily,
                    'iv_yearly': yearly
                }
            }
            stocks_collection.update_one(query, update)
            print("IV data updated for date:", date, symbol)


# with open('sec_bhavdata_full_12072024.csv', 'r') as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         if row[' SERIES'].strip() == 'EQ':  # Strip any extra spaces
#             document = {
#                 'symbol': str(row['SYMBOL']).strip(),
#                 'date': datetime.strptime(row[' DATE1'].strip(), '%d-%b-%Y'),
#                 'prev_close': float(row[' PREV_CLOSE'].strip()),
#                 'open_price': float(row[' OPEN_PRICE'].strip()),
#                 'high_price': float(row[' HIGH_PRICE'].strip()),
#                 'low_price': float(row[' LOW_PRICE'].strip()),
#                 'last_price': float(row[' LAST_PRICE'].strip()),
#                 'close_price': float(row[' CLOSE_PRICE'].strip()),
#                 'ttl_trd_qnty': int(row[' TTL_TRD_QNTY'].strip()),
#                 'turnover_lacs': float(row[' TURNOVER_LACS'].strip()),
#                 'no_of_trades': int(row[' NO_OF_TRADES'].strip()),
#                 'deliv_qty': int(row[' DELIV_QTY'].strip()),
#                 'deliv_per': float(row[' DELIV_PER'].strip())
#             }
#             if stocks_collection is not None:
#                 insert_or_update_document(stocks_collection, document)

# Expiry Date
# expiryNext = '29-08-2024'
# expiry = '25-07-2024'
expiryNext = '2024-08-29'
expiry = '2024-07-25'
type = 'STF'

# Call and update IV data
# process_and_update_iv_data('CMVOLT_12072024.csv')
# Call and update OI Data
process_and_update_fut_oi_data('BhavCopy_NSE_FO_0_0_0_20240708_F_0000.csv', expiry, expiryNext, type)

# print("OI data processed and nse collection updated successfully")

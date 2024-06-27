import csv
from pymongo import MongoClient
from datetime import datetime
import os

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nse']
collection = db['stock_info']


def import_bhavcopy(filename):
    # with open('sec_bhavdata_full_24052024.csv', 'r') as file:
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[' SERIES'].strip() == 'EQ':  # Strip any extra spaces
                document = {
                    'symbol': str(row['SYMBOL']).strip(),
                    'date': datetime.strptime(row[' DATE1'].strip(), '%d-%b-%Y'),
                    'prev_close': float(row[' PREV_CLOSE'].strip()),
                    'open_price': float(row[' OPEN_PRICE'].strip()),
                    'high_price': float(row[' HIGH_PRICE'].strip()),
                    'low_price': float(row[' LOW_PRICE'].strip()),
                    'last_price': float(row[' LAST_PRICE'].strip()),
                    'close_price': float(row[' CLOSE_PRICE'].strip()),
                    'ttl_trd_qnty': int(row[' TTL_TRD_QNTY'].strip()),
                    'turnover_lacs': float(row[' TURNOVER_LACS'].strip()),
                    'no_of_trades': int(row[' NO_OF_TRADES'].strip()),
                    'deliv_qty': int(row[' DELIV_QTY'].strip()),
                    'deliv_per': float(row[' DELIV_PER'].strip())
                }
                # collection.insert_one(document)
                if collection is not None:
                    insert_or_update_document(collection, document)

def process_and_update_stock_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbol = row['symbol']
            mcap = row['mcap']  # Accessing the 'mcap' column
            book_value = row['book_value']  # Accessing the 'book_value' column
            intrinsic_value = row['intrinsic_value']  # Accessing the 'intrinsic_value' column
            stock_pe = row['stock_pe']  # Accessing the 'stock_pe' column
            industry_pe = row['industry_pe']  # Accessing the 'industry_pe' column
            debt = row['debt']  # Accessing the 'debt' column
            int_coverage = row['int_coverage']  # Accessing the 'int_coverage' column
            promoter_holding = row['promoter_holding']  # Accessing the 'promoter_holding' column
            change_in_prom_hold = row['change_in_prom_hold']  # Accessing the 'change_in_prom_hold' column
            fii_holding = row['fii_holding']  # Accessing the 'fii_holding' column
            change_in_fii_holding = row['change_in_fii_holding']  # Accessing the 'change_in_fii_holding' column
            dii_holding = row['dii_holding']  # Accessing the 'dii_holding' column
            change_in_dii_holding = row['change_in_dii_holding']  # Accessing the 'change_in_dii_holding' column
            debt_to_equity = row['debt_to_equity']  # Accessing the 'debt_to_equity' column
            high_52week = row['high_52week']  # Accessing the 'high_52week' column
            low_52week = row['low_52week']  # Accessing the 'low_52week' column


            # Update document in nsestocks collection ('%d-%b-%Y') and '%Y-%m-%d'
            query = {'symbol': symbol}
            update = {
                '$set': {
                    'mcap': mcap,
                    'book_value': book_value,
                    'intrinsic_value': intrinsic_value,
                    'stock_pe': stock_pe,
                    'industry_pe': industry_pe,
                    'debt': debt,
                    'int_coverage': int_coverage,
                    'promoter_holding': promoter_holding,
                    'change_in_prom_hold': change_in_prom_hold,
                    'fii_holding': fii_holding,
                    'change_in_fii_holding': change_in_fii_holding,
                    'dii_holding': dii_holding,
                    'change_in_dii_holding': change_in_dii_holding,
                    'debt_to_equity': debt_to_equity,
                    'high_52week': high_52week,
                    'low_52week': low_52week
                }
            }
            collection.update_one(query, update)
            print(f"Data updated for - {symbol}")


def process_and_update_fut_oi_data(file_path, expiry, type):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # date = datetime.strptime(row['Date'].strip(), '%Y-%m-%d')
            expirydate = (row['XpryDt'])
            intrument = (row['FinInstrmNm'])
            # FinInstrmNm
            if(expirydate == expiry and intrument == type):
                date = datetime.strptime(row['RptgDt'].strip(), '%d-%b-%Y')
                symbol = row['TckrSymb']
                coi = int(float(row['ChngInOpnIntrst']))  # Parse coi as integer
                oi = int(float(row['OpnIntrst']))  
                # Construct expiry data
                expiry_data = {
                    'expiry': expirydate,
                    'coi': coi,
                    'oi': oi
                }

                # Update document in nsestocks collection ('%d-%b-%Y') and '%Y-%m-%d'
                query = {'symbol': symbol, 'date': date}
                update = {
                    '$push': {
                        'drvt': {'$each': [expiry_data]}
                    }
                }
                collection.update_one(query, update)
                print(f'record update for - {date}')
            else:
                print(f"some error occured {expirydate} and expiry {expiry}, {intrument} and {type} ")
                pass
                

process_and_update_stock_data('stock_details.csv')

print("Data inserted successfully into db")
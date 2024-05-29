import csv
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nsestocks']
collection = db['stocks']

with open('sec_bhavdata_full_24052024.csv', 'r') as file:
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
            collection.insert_one(document)

print("Data inserted successfully into db")

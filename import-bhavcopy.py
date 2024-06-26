import csv
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://192.168.29.213:27017/')
db = client['nsestocks']
collection = db['stocks']

# Function to insert or update documents in MongoDB
def insert_or_update_document(collection, document):
    # Check if a document with the same date already exists in the collection
    existing_document = collection.find_one({'date': document['date']})
    if existing_document:
        # If it exists, update the document
        # collection.update_one({'_id': existing_document['_id']}, {'$set': document})
        print("Document updated for date:", document['date'])
    else:
        # If it doesn't exist, insert a new document
        # collection.insert_one(document)
        print("New document inserted for date:", document['date'])

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
            # collection.insert_one(document)
            if collection is not None:
                insert_or_update_document(collection, document)

print("Data inserted successfully into db")
import csv
from pymongo import MongoClient
from datetime import datetime
import math

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nsestocks']
stocks_collection = db['stocks']

# Function to process IV data and update nsestocks collection
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
                    'daily': daily,
                    'yearly': yearly
                }
            }
            stocks_collection.update_one(query, update)

# Call the function with the path to your IV CSV file
process_and_update_iv_data('CMVOLT_24052024.csv')

print("IV data processed and nsestocks collection updated successfully")

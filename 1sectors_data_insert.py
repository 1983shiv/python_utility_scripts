import csv
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nsestocks']
sectors_collection = db['stock_info']

# Function to process and insert data from sectors.csv
def process_and_insert_sectors_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            document = {
                'symbol': str(row['SYMBOL']).strip(),
                'sector': str(row['SECTORS']).strip(),
                'industry': str(row['INDUSTRY']).strip(),
                'company_name': str(row['COMPANY NAME']).strip()
            }
            sectors_collection.update_one({'symbol': document['symbol']}, {'$set': document}, upsert=True)

# Call the function with the path to your sectors CSV file
process_and_insert_sectors_data('sectors.csv')

print("Sectors data inserted successfully into db")

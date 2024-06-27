import csv
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['nse']
stocks_collection = db['stocks']



# Function to process IV data and update nsestocks collection
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
                stocks_collection.update_one(query, update)
                print(f'record update for - {date}')
            else:
                print(f"some error occured {expirydate} and expiry {expiry}, {intrument} and {type} ")
                pass
                

# Expiry Date
expiry = '27-Jun-2024'
# expiry = '25-Jul-2024'
type = 'FUTSTK'

# Call the function with the path to your IV CSV file
process_and_update_fut_oi_data('NSE_FO_bhavcopy_26062024.csv', expiry, type)

# print("OI data processed and nse collection updated successfully")

'''
Abhijeet Babar.

Week 10
Date: 05/27/2021
Course: Python Programming(ICT-4370)

Program Description:
Week 8:
        Imports the values from the JSON file for the stocks in the portfolio and genrates line graph,
        that shows the dates on the x-axis of the graph and the closing price on y-axis.
        This code also add the imported data to the database(SQLite).
        At the end the program genrates a output.png file for ploted graph

Week 10:(from line number 147)
        In week 10 assignment I extended my assignemnt by improting data of provided stocks of one year by using Yahoo finance.
        I was also able to create .csv files for each stock and at the end I was able to create a output.json file.
        I got to know that yahoo finance is depricated in 2017 so I used yfinance library that has same functionalities.

'''
# Supports JSON and CSV file read/write
import json
import csv

import sqlite3

# Supports graph plotting
import matplotlib
import matplotlib.pyplot as plt

# Supports date calculations
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

# Supports data read
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

import yfinance as yf
from pandas_datareader import data as pdr

# Define New stock Class
class Stock():
    def __init__(self, symbol):
        # initialize attributes to describe a stock
        self.symbol = symbol
        self.dates = []
        self.openingPrices = []
        self.highs = []
        self.lows = []
        self.closingPrices = []
        self.volumes = []

    def addData(self, date, opening, high, low, close, volume):
        self.dates.append(date)
        self.openingPrices.append(opening)
        self.highs.append(high)
        self.lows.append(low)
        self.closingPrices.append(float("{:.2f}".format(float(close))))
        self.volumes.append(volume)

# Define tables for storing data

def create_tables(cursor):
    sql_create_table = """CREATE TABLE IF NOT EXISTS stock_txn (
                                            stockSymbol text NOT NULL,
                                            stockDate text NOT NULL,
                                            stockOpen real NOT NULL,
                                            stockHigh real NOT NULL,
                                            stockLow real NOT NULL,
                                            stockClose real NOT NULL,
                                            stockVolume integer NOT NULL
                                            ); """
    cursor.execute(sql_create_table)


# Insert data into to table created
def write_data(cursor, dataSet):

    for stock in dataSet:
        sql_insert_txn = "INSERT INTO stock_txn VALUES (" + \
            "'" + stock['Symbol'] + "', '"
        sql_insert_txn = sql_insert_txn + \
            str(datetime.strptime(stock['Date'], '%d-%b-%y'))
        sql_insert_txn = sql_insert_txn + "', '" + \
            (stock['Open']) + "', '" + (stock['High'])
        sql_insert_txn = sql_insert_txn + "', '" + \
            (stock['Low']) + "', " + str(stock['Close'])
        sql_insert_txn = sql_insert_txn + ", " + str(stock['Volume']) + ");"
        cursor.execute(sql_insert_txn)


data = {}

# Opens AllStocks.json
filePath = "AllStocks.json"
with open(filePath) as f:
    dataSet = json.load(f)

investmentDictionary = {}

# iterate through json file and add each time a new symbol is encountered, add it to the investmentDictionary
for investment in dataSet:
    investmentStr = str(investment)
    symbol = investment['Symbol']
    if symbol not in investmentDictionary:
        newInvestment = Stock(symbol)
        investmentDictionary[symbol] = {'Stock': newInvestment}
    currentStock = investmentDictionary[symbol]['Stock']
    currentStock.addData(datetime.strptime(investment["Date"], '%d-%b-%y'), investment["Open"],
                         investment["High"], investment["Low"], investment["Close"], investment["Volume"])

for investment in investmentDictionary:
    closes = investmentDictionary[investment]['Stock'].closingPrices
    dates = matplotlib.dates.date2num(
        investmentDictionary[investment]['Stock'].dates)
    name = investmentDictionary[investment]['Stock'].symbol
    plt.plot_date(dates, closes, linestyle='solid', marker='None', label=name)
    # Adds label to x axis
    plt.xlabel("Date")
    # Adds label to y axis
    plt.ylabel("Closing Price")

# Connect to database to create tables
dbPath = r'allStocksDB.db'
conn = sqlite3.connect(dbPath)
cursor = conn.cursor()
create_tables(cursor)

# Add values to the database
write_data(cursor, dataSet)

plt.legend(title='Stocks')

# Saves the polt as a PNG file
plt.savefig("output.png")

plt.show()

# Commit the database transactions and close the DB.
conn.commit()
conn.close()



################################     Week 10 Assignemnt    ################################
'''
Yahoo! finance has decommissioned their historical data API, 
causing many programs that relied on it to stop working.

fix-yahoo-finance fixes the problem by scraping the data from Yahoo! 
finance and returning a Pandas DataFrame in the same format 
as pandas_datareader’s get_data_yahoo().
'''

# Supports read from Yahoo Finance
yf.pdr_override()

# The program gets data from Yahoo Finance, the start_date and today's date.
# Stock symbol list extracted from AllStock.json
stock_list = ['AIG', 'F', 'FB', 'GOOG', 'IBM', 'M', 'MSFT', 'RDS-A']

today = date.today()
# Start date is a year ago of current date
start_date =  date.today() - relativedelta(years=1)

# for storing name of the files.
files = []

# Gets data from Yahoo Finance using the start_date defined above and today's date
def getData(stock):
    print(stock)
    data = pdr.get_data_yahoo(stock, start=start_date, end=today)
    dataname = stock + "_Stock_data_from_" + \
        str(start_date) + "_to_" + str(today)
    files.append(dataname + ".csv")
    SaveData(data, dataname)

# Create a file in current dir.
def SaveData(df, filename):
    df.to_csv(filename + '.csv')

# Get data for each Stock listed stock_list
for stock in stock_list:
    getData(stock)

# Collects data in CSV files and compiles data to one JSON file
jsonFileName = "output.json"
data = {}

# To create/update the output JSON file from all the genrated CSV's
for i in range(0, len(files)):
    with open(files[i]) as csvFile:
        csvReader = csv.DictReader(csvFile)
        num = 0
        for rows in csvReader:
            id = rows['Date']
            rows['Symbol'] = stock_list[i]
            data[files[i] + "_" + str(num)] = rows
            num += 1

# Writes all data to output.json file
with open(jsonFileName, 'w') as jsonFile:
    jsonFile.write(json.dumps(data, indent=4))

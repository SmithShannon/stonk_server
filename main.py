import pandas as pd
import requests, os
import datetime as dt

from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('key')
working_dir = os.getcwd()

today = dt.date.today()
next30days = today+dt.timedelta(days=30)

dates = 'from='+next30days.strftime('%y-%m-%d')+'&to='+today.strftime('%Y-%m-%d')

stock_res = 'https://financialmodelingprep.com/api/v3/available-traded/list?apikey='+key
dividend_res = 'https://financialmodelingprep.com/api/v3/stock_dividend_calendar?'+dates+'&apikey='+key

def to_record(row):
    record = {}
    for k in row.keys():
        record[k] = [row[k]]
    return pd.DataFrame(record)

def build_dataframe(request_string):
    res = requests.get(request_string).json()
    return pd.concat(pd.Series(res).apply(to_record).tolist())

stocks = build_dataframe(stock_res)
dividend = build_dataframe(dividend_res)

#which stock has the highest dividend to price ratio that is tradable on the TSX?
tsx_stocks = stocks[stocks['exchangeShortName']=='TSX']

div_agg = dividend[['symbol','dividend']].groupby('symbol').sum()

tsx_div = tsx_stocks.merge(right=div_agg,how='inner',on='symbol',suffixes=("", ""))

tsx_div['ratio'] = tsx_div['dividend']/tsx_div['price']

tsx_div.to_csv(working_dir+'dividend_ratios.csv')

print(tsx_div.sort_values('ratio',ascending=False).head(5))
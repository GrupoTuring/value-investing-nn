import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from turingquant.support import get_income_statement, get_balance_sheet, get_cashflow

def get_sp500_tickers():
    """Function that get all companies symbols from S&P500
    Returns:
        (list of str) all companies symbols
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    tickers = [s.replace('\n', '') for s in tickers]

    return tickers

def get_annual_hpr(ticker, period=126):
    """Function that calculates the Anual Holding Period Return (HPR)
    Args:
        symbol (str): S&P500 companie symbol
    Return:
        (pandas.DataFrame) Holding Period Return
    """

    stock = yf.Ticker(ticker)

    stock_data = stock.history(period="max")

    dividends = stock_data['Dividends']
    close_prices = stock_data['Close']

    dividend_period_sum = dividends.copy()

    for row in range(period, len(dividends)):
        dividend_period_sum.iloc[row] = dividends.iloc[row-period:row].sum()

    dividend_semesterly_sum = dividend_period_sum.resample("BM").last().ffill()
    close_semesterly_prices = close_prices.resample("BM").last().ffill()
    
    isJune = dividend_semesterly_sum.index.month.isin([6])

    income = dividend_semesterly_sum[isJune]
    value = close_semesterly_prices[isJune]

    holding_period_return = (
        income.shift(1) + value.shift(1) - value) / value

    return holding_period_return


def get_features(symbol):
    """Function that creates the fundamental dataset
    Args:
        symbol (str): S&P500 companie symbol
    Return:
        (pandas.DataFrame) Table containing F-Score model data 
        and Holding Period Return (HPR) as the target
    """
       
    income_statement =  get_income_statement(symbol)
    time.sleep(0.3)
    balance_sheet = get_balance_sheet(symbol)
    time.sleep(0.3)
    cash_flow = get_cashflow(symbol)
    time.sleep(1)
    
    # profitability
    ROA = balance_sheet['Total Assets'] / income_statement['Net Income Common Stockholders']
    delta_ROA = ROA.pct_change(periods = -1)
    CFO = cash_flow['Operating Cash Flow']
    ROE = income_statement['Net Income Common Stockholders'] / balance_sheet['Common Stock Equity']
    
    # Leverage / Liquidity
    delta_leverage = balance_sheet['Total Debt'] / balance_sheet['Total Assets']
    delta_liquidity = (balance_sheet['Total Assets']/ (balance_sheet['Total Assets'] - balance_sheet['Common Stock Equity'])).pct_change(periods = -1)
    issue_new = balance_sheet['Common Stock Equity'].pct_change(periods=-1)

    # Operating Efficiency
    delta_turnover = (income_statement['Total Revenue'] / balance_sheet['Total Assets']).pct_change(periods = -1)
    delta_margin = ((income_statement['EBIT'] + income_statement['Reconciled Depreciation']) / income_statement['Total Revenue']).pct_change(periods = -1)
    
    # Dates
    #dates = income_statement.index
    #print(dates)

    # concatenate
    df_cols = [ROA, delta_ROA, CFO, ROE, delta_leverage, delta_liquidity, issue_new, delta_turnover, delta_margin]
    df = pd.concat(df_cols, axis=1)
    df.columns = ['ROA', 'delta_ROA', 'CFO', 'Accrual', 'delta_leverage', 'delta_liquidity', 'issue_new', 'delta_margin', 'delta_turn_over']
    
    rows = df.shape[0]
    
    df['HPR'] = get_annual_hpr(ticker=symbol).iloc[-rows:].to_numpy()[::-1]

    df['symbol'] = symbol

    return df.iloc[:-1]

if __name__ == '__main__':
    # S&P500 tickers
    tickers = get_sp500_tickers()

    # get fundamentalist data
    cont = 1
    features = []
    for ticker in tickers:
        try:
            features.append(get_features(symbol=ticker))
            print(ticker)
        except:
            cont = cont +1
            print('Error')
            
    print("Count of Errors: ", cont)

    df = pd.concat(features)
    df.to_csv('s&p500_fundamental_data.csv', index=True, index_label='date')

    
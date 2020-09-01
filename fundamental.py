import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

def get_financials(url):   
    page_source = requests.get(url)

    soup_html = BeautifulSoup(page_source.text, 'html.parser')
    table_soup = soup_html.find('div', class_="M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)")
    
    # Get Title Row
    headlines = table_soup.find('div', class_="D(tbr) C($primaryColor)")
    headlines = headlines.findAll('span')
    title_row = list()
    for line in headlines:
        title_row.append(line.text)
    
    table = pd.DataFrame(None, columns = title_row)
    remaining_lines = table_soup.findAll('div', class_="D(tbr) fi-row Bgc($hoverBgColor):h")
    for row in remaining_lines:
        columns = row.findChildren('div',recursive=False)
        line_values = list()
        for col in columns:
            has_comma = ',' in col.text
            is_empty = '-' in col.text and len(col.text) == 1
            if has_comma:
                value = float(col.text.replace(',', ''))
            elif is_empty:
                value = np.nan
            else:
                value = col.text
            line_values.append(value)
        table.loc[len(table)] = line_values
    table = table.set_index(title_row[0])
    return table.T

def get_income_statement(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/financials'
    return get_financials(url).drop(['ttm'], axis=0)

def get_balance_sheet(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet'
    return get_financials(url)        

def get_cashflow(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '/cash-flow'
    return get_financials(url).drop(['ttm'], axis=0)

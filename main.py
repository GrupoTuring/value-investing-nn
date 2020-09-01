import pandas as pd
from fundamental import get_income_statement, get_balance_sheet, get_cashflow

def get_features(income_statement, balance_sheet, cash_flow):
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

    # concatenate
    df_cols = [ROA, delta_ROA, CFO, ROE, delta_leverage, delta_liquidity, issue_new, delta_turnover, delta_margin]
    df = pd.concat(df_cols, axis=1)
    df.columns = ['ROA', 'delta_ROA', 'CFO', 'Accrual', 'delta_leverage', 'delta_liquidity', 'issue_new', 'delta_margin', 'delta_turn_over']

    return df.iloc[:-1]

if __name__ == '__main__':
    # ticker
    symbol  = 'MSFT'

    # get fundamentalist data
    income_statement = get_income_statement(symbol)
    balance_sheet = get_balance_sheet(symbol)
    cash_flow = get_cashflow(symbol)

    # combine all together
    X_msft = get_features(income_statement, balance_sheet, cash_flow)
    print(X_msft.head())

import yfinance as yf


def get_annual_hpr(ticker, period=252):
    """
    Essa função calcula o holding period return anual de junho
    """

    stock = yf.Ticker(ticker)

    stock_data = stock.history(period="max")

    dividends = stock_data['Dividends']
    close_prices = stock_data['Close']

    dividend_period_sum = dividends.copy()

    for row in range(period, len(dividends)):
        dividend_period_sum.iloc[row] = dividends.iloc[row-period:row].sum()

    dividend_semesterly_sum = dividend_period_sum.resample("2Q").last().ffill()
    close_semesterly_prices = close_prices.resample("2Q").last().ffill()

    isJune = dividend_semesterly_sum.index.month.isin([6])

    income = dividend_semesterly_sum[isJune]
    value = close_semesterly_prices[isJune]

    holding_period_return = (
        income + value - value.shift(-1)) / value.shift(-1)

    return holding_period_return

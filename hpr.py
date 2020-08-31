from alpha_vantage.timeseries import TimeSeries


def initialize_alpha_vantage():
    """
    Essa função inicializa a api da alpha vantage 
    """

    key = input('Insira sua chave do alpha vantage: ')

    return TimeSeries(key=key, output_format='pandas')


def get_annual_hpr(ticker, period=252):
    """
    Essa função calcula o holding period return anual de junho
    """

    time_series = initialize_alpha_vantage()

    stock_data, _ = time_series.get_daily_adjusted(ticker, outputsize='full')

    dividends = stock_data['7. dividend amount']
    close_prices = stock_data['5. adjusted close']

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

import pandas as pd
import streamlit as st
import yfinance as yf

@st.cache_data
def load_ticker_history(stock_selected, period):

    """Load historical price data for a given stock ticker.
    
    Fetches historical OHLCV (Open, High, Low, Close, Volume) data for a specified
    stock ticker over the given period and returns it as a DataFrame with the Date
    column formatted as date objects.
    
    Args:
        stock_selected (str): The stock ticker symbol (e.g., 'PETR4.SA').
        period (str): The time period for historical data (e.g., '1mo', '3mo', '1y').
    
    Returns:
        pd.DataFrame: A DataFrame containing historical OHLCV data with Date as the first column,
                      and all numerical values rounded to 2 decimal places.
    """
    stocks = yf.Ticker(stock_selected)

    df_stock = stocks.history(period = period)
    df_stock = df_stock.reset_index().round(2)
    df_stock['Date'] = pd.to_datetime(df_stock['Date']).dt.date

    return df_stock

@st.cache_data
def df_stocks_close(period, stocks_list):

    """Fetch closing prices for multiple stocks over a specified period.
    
    Retrieves the closing prices for each stock ticker in the provided list
    and returns them as a DataFrame where each column represents a ticker.
    
    Args:
        period (str): The time period for historical data (e.g., '1mo', '3mo', '1y').
        stocks_list (list): A list of stock ticker symbols to fetch data for.
    
    Returns:
        pd.DataFrame: A DataFrame with dates as index and stock tickers as columns,
                      containing the closing prices for each stock.
    """
    df_close_prices = pd.DataFrame()

    for ticker in stocks_list:

        ticker_data = yf.Ticker(ticker)
        hist = ticker_data.history(period=period)
        df_close_prices[ticker] = hist['Close']
    
    return df_close_prices

@st.cache_data(ttl=300)
def load_ticker_info_today(stock_selected):

    """Load current and fundamental information for a stock ticker.
    
    Retrieves real-time price data, trading information, and company details
    for the specified stock ticker. Price data is automatically updated every 5 minutes.
    
    Args:
        stock_selected (str): The stock ticker symbol (e.g., 'PETR4.SA').
    
    Returns:
        dict: A dictionary containing the following keys:
              - 'Last Price': Current closing price (float)
              - 'Previous Close': Previous day's closing price (float)
              - 'Pct Today': Percentage change from previous close (float)
              - 'Open Price': Today's opening price (float)
              - 'Day High': Today's highest price (float)
              - 'Day Low': Today's lowest price (float)
              - 'Long Name': Company full name (str)
              - 'Summary': Business description (str)
              - 'Web Site': Company website URL (str)
              - 'Sector': Industry sector (str)
              - 'Industry': Specific industry classification (str)
    """
    stocks = yf.Ticker(stock_selected)

    last_price = round(stocks.fast_info["lastPrice"], 2)
    previous_close = round(stocks.info["previousClose"], 2)
    pct_today = (last_price / previous_close - 1) * 100
    open_price = round(stocks.info["open"], 2)
    day_high = round(stocks.info["dayHigh"], 2)
    day_low = round(stocks.info["dayLow"], 2)
    long_name = stocks.info["longName"]
    business_summary = stocks.info["longBusinessSummary"]
    web_site = stocks.info["website"]
    sector = stocks.info["sector"]
    industry = stocks.info["industry"]

    ticker_info = {
        'Last Price': last_price,
        'Previous Close': previous_close,
        'Pct Today': pct_today,
        'Open Price': open_price,
        'Day High': day_high,
        'Day Low': day_low,
        'Long Name' : long_name,
        'Summary' : business_summary,
        'Web Site' : web_site,
        'Sector' : sector,
        'Industry' : industry
    }

    return ticker_info

def statistics_historical_data(df_stock):

    """Calculate key statistical metrics from historical stock data.
    
    Computes various statistical measures including volatility, returns, price statistics,
    and variation coefficients from a DataFrame of historical stock prices.
    
    Args:
        df_stock (pd.DataFrame): A DataFrame containing at least 'Close', 'High', and 'Low' columns
                                with historical price data.
    
    Returns:
        dict: A dictionary containing the following statistical metrics:
              - 'Volatility': Annualized volatility (% per year)
              - 'Cumulative Return': Total cumulative return over the period (%)
              - 'High Price': Maximum price in the period (float)
              - 'Low Price': Minimum price in the period (float)
              - 'Median Price': Median closing price (float)
              - 'Mean Price': Average closing price (float)
              - 'Standard Deviation': Standard deviation of closing prices (float)
              - 'Coefficient Variation': Ratio of standard deviation to mean (%)
    """
    returns = df_stock['Close'].pct_change().fillna(0)
    volatility = (returns.std() * 252 ** 0.5) * 100 # Annualized volatility
    cumulative_return = ((1 + returns).prod() - 1) * 100
    median_price = df_stock['Close'].median()
    mean_price = df_stock['Close'].mean()
    standard_deviation_price = df_stock['Close'].std()
    coefficient_variation_price = standard_deviation_price / mean_price * 100
    high_price = df_stock['High'].max()
    low_price = df_stock['Low'].min()

    stats = {
        'Volatility': volatility,
        'Cumulative Return': cumulative_return,
        'High Price': high_price,
        'Low Price': low_price,
        'Median Price': median_price,
        'Mean Price': mean_price,
        'Standard Deviation': standard_deviation_price,
        'Coefficient Variation': coefficient_variation_price
    }

    return stats

def df_returns(df_close_prices):

    """Calculate daily percentage returns from closing prices.
    
    Computes the daily percentage change in closing prices for each stock,
    filling NaN values (typically the first row) with zeros.
    
    Args:
        df_close_prices (pd.DataFrame): A DataFrame with dates as index and stock tickers as columns,
                                       containing closing prices.
    
    Returns:
        pd.DataFrame: A DataFrame with the same structure as input, containing daily percentage
                     returns for each stock.
    """
    df_close_returns = df_close_prices.pct_change().fillna(0)

    return df_close_returns

def df_stocks_returns_ranking(df_close_returns):

    """Rank stocks by cumulative returns over a period.
    
    Calculates cumulative returns for each stock and returns them sorted
    in descending order for easy ranking comparison.
    
    Args:
        df_close_returns (pd.DataFrame): A DataFrame with daily percentage returns for each stock
                                        (typically the output of df_returns function).
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Ticker' and 'Cumulative Return (%)',
                     sorted by Cumulative Return in descending order, rounded to 2 decimal places.
    """
    df_cumulative_returns = ((1 + df_close_returns).prod() - 1) * 100
    df_cumulative_returns = df_cumulative_returns.reset_index().rename(columns={'index' : 'Ticker', 0 : 'Cumulative Return'}).sort_values(by= 'Cumulative Return', ascending= False).round(2)

    return df_cumulative_returns

def df_stocks_returns_period(df_close_returns):

    """Calculate cumulative returns over time for multiple stocks.
    
    Computes the cumulative returns for each stock on each date, enabling
    visualization of return growth over the specified period.
    
    Args:
        df_close_returns (pd.DataFrame): A DataFrame with daily percentage returns for each stock.
    
    Returns:
        pd.DataFrame: A DataFrame with dates as index and stock tickers as columns,
                     containing cumulative returns (%) rounded to 2 decimal places.
    """
    df_returns_period = (((1 + df_close_returns).cumprod() -1) * 100).round(2)

    return df_returns_period

def df_annualized_volatility(df_close_returns):

    """Calculate and rank stocks by annualized volatility.
    
    Computes the annualized volatility for each stock (assuming 252 trading days per year)
    and returns them sorted in descending order.
    
    Args:
        df_close_returns (pd.DataFrame): A DataFrame with daily percentage returns for each stock.
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Ticker' and 'Annualized Volatility (%)',
                     sorted by Annualized Volatility in descending order, rounded to 2 decimal places.
    """
    annualized_volatility = ((df_close_returns.std() * 252 ** 0.5) * 100).round(2).sort_values(ascending = False)
    annualized_volatility = annualized_volatility.reset_index().rename(columns={'index' : 'Ticker', 0 : 'Annualized Volatility'})

    return annualized_volatility

def df_coefficient_variation(df_close_prices):
    
    """Calculate and rank stocks by coefficient of variation.
    
    Computes the coefficient of variation (ratio of standard deviation to mean)
    for each stock, which measures relative price volatility.
    
    Args:
        df_close_prices (pd.DataFrame): A DataFrame with dates as index and stock tickers as columns,
                                       containing closing prices.
    
    Returns:
        pd.DataFrame: A DataFrame with columns 'Ticker' and 'Coefficient Variation (%)',
                     sorted by Coefficient Variation in descending order, rounded to 2 decimal places.
    """
    coefficient_variation = (df_close_prices.std() / df_close_prices.mean() * 100).round(2).sort_values(ascending = False)
    coefficient_variation = coefficient_variation.reset_index().rename(columns = {'index' : 'Ticker', 0 : 'Coefficient Variation'})

    return coefficient_variation
                


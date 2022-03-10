"""
Back Testing  -  Trading Strategy - RSI , MV and Bollianger Band
"""
import os
import backtrader.sizers
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.analyzers as btanalyzer
import numpy as np

from self.tradingSetup.backtrader.Strategy.RSI import rsi
from self.tradingSetup.backtrader.Strategy.mvav import mvav
from self.tradingSetup.backtrader.Strategy.BBand_Strategy import BBand_Strategy

cwd = os.getcwd()
print(f"Current working directory: {cwd}")
DESIRED_WIDTH = 320
pd.set_option('display.width', DESIRED_WIDTH)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 2000)

class GenericCSV(bt.feeds.GenericCSVData):
    """Add Rows"""
    lines = ('pivot', 'RSIpivot', 'divsignal')
    params = (('pivot', 7), ('RSIpivot', 8), ('divsignal', 9))

class BacktestBackTrader:
    """Create instance"""

    def __init__(self, ):
        self.cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)

    def back_trader(self, data):
        # Add Strategy
        self.cerebro.addstrategy(rsi)
        # Add Data
        self.cerebro.adddata(data)
        self.cerebro.broker.setcash(100000000.0)
        self.cerebro.broker.setcommission(commission=0.000000001)

        # ADD Observer
        self.cerebro.addobserver(bt.observers.BuySell)
        self.cerebro.addobserver(bt.observers.Value)
        self.cerebro.addsizer(backtrader.sizers.PercentSizer, percents=100)
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

        # ADD Analyzer
        self.cerebro.addanalyzer(btanalyzer.SharpeRatio, _name="sharpe")
        self.cerebro.addanalyzer(btanalyzer.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(btanalyzer.Transactions, _name="tran")
        self.cerebro.addanalyzer(btanalyzer.TradeAnalyzer, _name="Trade")
        self.cerebro.addanalyzer(btanalyzer.Returns, _name="returns")
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")


        backtest_result = self.cerebro.run(maxcpus=1, stdstats=False, runonce=False, safediv=False)
        # Graph plotting
        self.cerebro.plot(iplot=True, volume=False)


if __name__ == "__main__":
    # Download data from Yahoo
    df = yf.download(tickers='INFY.NS', period='1mo', interval='5m', progress=False)
    df = df.reset_index()
    df.rename(columns={"Datetime": "Date"}, inplace=True)
    df.Date = pd.to_datetime(df.Date)
    df['Date'] = df['Date'].dt.tz_localize(None)
    df = df.set_index("Date")
    df = df.rename(columns={'Open': open, 'High': 'high', 'Low': 'low', 'Close': 'close'})
    df["pivot"] = np.nan
    df["RSIpivot"] = np.nan
    df["divsignal"] = np.nan
    df.to_csv("backtest_backtrader.csv")
    data1 = GenericCSV(dataname="backtest_backtrader.csv")
    # data1 = bt.feeds.PandasData(dataname=df)
    BacktestBackTrader().back_trader(data=data1)

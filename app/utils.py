import pandas as pd
import numpy as np
from app.models import Ticker
import requests
from time import sleep
import yfinance as yf

def currency_abbreviation(number):
    abbreviations = [(1e12, 'T'), (1e9, 'B'), (1e6, 'M'), (1e3, 'K')]

    for factor, suffix in abbreviations:
        if abs(number) >= factor:
            formatted_number = "{:.2f}{}".format(number / factor, suffix)
            break
    else:
        formatted_number = "{:,.2f}".format(number)  # Default format for smaller numbers

    return formatted_number


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.insert(0, item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop(0)
        else:
            print("Error: Stack is empty.")
            return None

    def replace_top(self, new_item):
        if not self.is_empty():
            self.items[0] = new_item
        else:
            print("Error: Stack is empty.")
            return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
    

class Trades():
    """
    Class to extract trades from a given excel file
    """
    def __init__(self, excel_file):
        self.original_data = pd.read_excel(excel_file)

        self.original_data['Date'] = pd.to_datetime(self.original_data['Date'], format='%m/%d/%y %H:%M').dt.date

        self.all_tickers = self.original_data['Ticker'].dropna().unique().tolist()
        self.MarginCall_df = self.original_data[self.original_data['Description'] == 'Margin Call']
        self.trades_df = pd.DataFrame()
        self.portfolio_df = pd.DataFrame()
        self.trades_Extracted : bool = False
        # self.opening_balance = float(self.original_data[self.original_data['Description'] == 'Opening']['Balance'])
        self.opening_balance = float(self.original_data.loc[self.original_data['Description'] == 'Opening', 'Balance'].iloc[0])

        # self.closing_balance = float(self.original_data[self.original_data['Description'] == 'Closing']['Balance'])
        self.closing_balance = float(self.original_data.loc[self.original_data['Description'] == 'Closing', 'Balance'].iloc[0])


    def extract_trades(self):

        for ticker in self.all_tickers:
            temp_df=self.original_data[self.original_data['Ticker'] == ticker ]
            # Initialize variables to store trade information
            open_trades = Stack()

            # Initialize variables to store trade information
            current_trade = None
            trades = []
            intraday_trades =[]

            # Iterate through the rows
            for index, row in temp_df.iterrows():
                if row['Description'] == 'Open':
                      # New trade started or adding to/reducing an existing trade
                      current_trade = {
                              'OpenIndex': index,
                              'OpenDate': row['Date'],
                              'Ticker': row['Ticker'],
                              'OpenDebit': row['Debit'],
                              'CloseIndex': None,
                              'CloseDate': None,
                              'CloseCredit': 0.0,
                              'ProfitLoss': 0.0,
                              'IsIntraday' : None,
                          }
                      # added the current trade to stack
                      open_trades.push(current_trade)

                elif row['Description'] == "Add" and not open_trades.is_empty():
                    current_trade = open_trades.pop()
                    current_trade['OpenDebit'] += row['Debit']
                    open_trades.push(current_trade)

                elif row['Description'] == "Reduce" and not open_trades.is_empty():
                    current_trade = open_trades.pop()
                    current_trade['OpenDebit'] -= row['Credit']
                    open_trades.push(current_trade)

                elif row['Description'] == 'Close' and not open_trades.is_empty():
                    current_trade = open_trades.pop()
                    # Close the current trade
                    current_trade['CloseIndex'] = index
                    current_trade['CloseDate'] = row['Date']
                    current_trade['CloseCredit'] += row['Credit']
                    current_trade['ProfitLoss'] = current_trade['CloseCredit'] - current_trade['OpenDebit']


                    if row['Date'] == current_trade['OpenDate']:
                          # This is an intraday trade
                          # intraday_trades.append(current_trade)
                          # current_trade = None  # Reset current trade
                          current_trade['IsIntraday'] = True
                    else:
                          current_trade['IsIntraday'] = False
                    # Append the trade to the list of trades
                    trades.append(current_trade)
                    current_trade = None  # Reset current trade


            # Create a new DataFrame from the list of trades
            Trades = pd.DataFrame(trades)
            # intraday_trades = pd.DataFrame(intraday_trades)
            self.trades_df = pd.concat([self.trades_df, Trades], ignore_index=True)

        self.trades_df.sort_values(by='CloseDate', inplace=True, ignore_index=True)
        self.Trades_Extracted = True


    def compute_portfolio_value(self):

        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None

        self.portfolio_df = self.trades_df.copy()
        self.portfolio_df.sort_values(by='CloseDate', inplace=True, ignore_index=True)
        self.portfolio_df.dropna(inplace=True)

        portfolio_value = [self.opening_balance + self.portfolio_df['ProfitLoss'].iloc[0]]

        for index in range(1, self.portfolio_df.shape[0]):
            portfolio_value.append(portfolio_value[index-1] + self.portfolio_df['ProfitLoss'].iloc[index])

        self.portfolio_df['Portfolio_value'] = portfolio_value

        # Group by 'CloseDate' and calculate the average 'Portfolio_value'
        self.portfolio_df['Portfolio_value'] = self.portfolio_df.groupby('CloseDate')['Portfolio_value'].transform('mean')


    def compute_hit_ratio(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None

        profitable_trades = self.trades_df[self.trades_df['ProfitLoss'] > 0].shape[0]
        loss_trades = self.trades_df[self.trades_df['ProfitLoss'] <= 0].shape[0]

        hit_ratio = np.round(profitable_trades / loss_trades,2)
        # print(f"Hit Ratio: {hit_ratio:.2f}")
        return hit_ratio, profitable_trades, loss_trades


    def get_drawdown_analysis(self):
        # compute portfolio value first
        # mandatory step
        self.compute_portfolio_value()
        
        df = self.portfolio_df[['CloseDate','Portfolio_value']].copy()

        # Calculate drawdowns
        df["PreviousPeak"] = df["Portfolio_value"].cummax()
        df["Drawdown"] = df["Portfolio_value"] - df["PreviousPeak"]

        return df['CloseDate'].to_list(),df['Drawdown'].to_list()

    def compute_max_drawdown(self):
        _,drawdown_list = self.get_drawdown_analysis()
        return min(drawdown_list)
    
    def get_intraday_trades(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None
        return self.trades_df[self.trades_df['IsIntraday'] == True].copy()


    def get_swing_trades(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None
        return self.trades_df[self.trades_df['IsIntraday'] == False].copy()


    def get_num_trades(self):

        total_trades = self.trades_df.shape[0]
        swing_trades = self.get_swing_trades().shape[0]
        intraday_trades = self.get_intraday_trades().shape[0]
        margil_calls = self.MarginCall_df.shape[0]

        return (total_trades,swing_trades,intraday_trades,margil_calls)


    def get_balance(self):
        return (self.opening_balance,self.closing_balance)


    def get_most_profitable_tickers(self):

        most_profitable_tickers = pd.DataFrame(self.trades_df.groupby('Ticker')['ProfitLoss'].sum().nlargest(3))
        
        most_profitable_tickers = most_profitable_tickers.to_dict()['ProfitLoss']
        
        return most_profitable_tickers


    def get_least_profitable_tickers(self):

        least_profitable_tickers = pd.DataFrame(self.trades_df.groupby('Ticker')['ProfitLoss'].sum().nsmallest(3))

        least_profitable_tickers = least_profitable_tickers.to_dict()['ProfitLoss']
        
        return least_profitable_tickers
    

    def get_monthly_profitloss(self):

        df=self.trades_df.copy()
        df = pd.concat([df, self.MarginCall_df], ignore_index=True)
        df['month'] = pd.to_datetime(df['CloseDate']).dt.month
        monthly_profit_loss = pd.DataFrame(df.groupby('month')['ProfitLoss'].sum())
        monthly_profit_loss['month'] = monthly_profit_loss.index.map({1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'})
        monthly_profit_loss.index=monthly_profit_loss['month']
        monthly_profit_loss.drop(columns=['month'], inplace=True)
        
        return monthly_profit_loss.to_dict()['ProfitLoss']

    def get_sector_profitloss(self):
        
        df =self.trades_df.copy()

        sector_pnl = pd.DataFrame(df.groupby('Sector')['ProfitLoss'].sum())
    
        return sector_pnl.to_dict()['ProfitLoss']

    def get_sector_for_all_Trades(self):
        if not self.Trades_Extracted:
            print(f"LOG :: Sector for Trade : Trades not extracted from raw data yet!!")
            return
        
        for index, row in self.trades_df.iterrows():
            if row['Ticker'].split()[0].isdigit():
                if row['Ticker'].split()[1] == "CH":
                    ticker = f"{row['Ticker'].split()[0]}.SS"
                elif row['Ticker'].split()[1] == "JP":
                    ticker = f"{row['Ticker'].split()[0]}.T"
                elif row['Ticker'].split()[1] == "LN":
                    ticker = f"{row['Ticker'].split()[0]}.L"
                elif row['Ticker'].split()[1] == "TT":
                    ticker = f"{row['Ticker'].split()[0]}.TW"
                elif row['Ticker'].split()[1] == "JT":
                    ticker = f"{row['Ticker'].split()[0]}.T"
            else:
                if row['Ticker'].split()[1] == "LN":
                    ticker = f"{row['Ticker'].split()[0]}.L"
                else:
                    ticker = row['Ticker'].split()[0]

            print(f"Index {index} : ticker : {ticker}")
            
            
            # check is ticker exists in db already
            if Ticker.objects.filter(ticker = ticker).exists():
                ticker_in_db =  Ticker.objects.get(ticker=ticker)
                self.trades_df.loc[index,'Sector'] = ticker_in_db.get_sector_name()
                
            # if ticker doesnt exist in db then get the sector details from API
            else:
                print(f"LOG :: {ticker} not found in db")
                try:
                    sleep(0.1)
                    tickerdata = yf.Ticker(ticker)
                    if tickerdata.info['quoteType'] == 'EQUITY':
                      self.trades_df.loc[index, 'Sector'] = tickerdata.info['sector']
                      Ticker.objects.create(ticker = ticker, company_name=tickerdata.info['longName'], industry=tickerdata.info['industry'],sector = tickerdata.info['sector'])
                    elif tickerdata.info['quoteType'] == 'ETF':
                      self.trades_df.loc[index, 'Sector'] = 'Financial Services'
                      Ticker.objects.create(ticker = ticker, company_name=tickerdata.info['longName'],sector = 'Financial Services')
                    else:
                      self.trades_df.loc[index, 'Sector'] = tickerdata.info['quoteType']
                      Ticker.objects.create(ticker = ticker,sector = tickerdata.info['quoteType'])
            
                except Exception as e:

                    # print(f"Ticker {ticker} not found")
                    print(f"Exception thrown for {ticker} : {e}")
                    self.trades_df.loc[index, 'Sector'] = "NONE"
                    continue


    def get_sector_none(self):
        sector_none = self.trades_df[self.trades_df["Sector"]=="NONE"].copy()
        return sector_none


    def next_fn(self):
        pass


# global utility functions NOT member func of class Trades
def compute_hit_ratio(df:pd.DataFrame):
    profitable_trades = df[df['ProfitLoss'] > 0].shape[0]
    loss_trades = df[df['ProfitLoss'] <= 0].shape[0]
    hit_ratio = np.round(profitable_trades / loss_trades,2)
    return hit_ratio, profitable_trades, loss_trades

def compute_profit_loss(df:pd.DataFrame):
    pnl = np.round(df['ProfitLoss'].sum(),2)
    return pnl

def get_most_profitable_tickers(df:pd.DataFrame):
    most_profitable_tickers = pd.DataFrame(df.groupby('Ticker')['ProfitLoss'].sum().nlargest(3))
    
    most_profitable_tickers = most_profitable_tickers.to_dict()['ProfitLoss']
    
    return most_profitable_tickers

def get_least_profitable_tickers(df:pd.DataFrame):

    least_profitable_tickers = pd.DataFrame(df.groupby('Ticker')['ProfitLoss'].sum().nsmallest(3))
    
    least_profitable_tickers = least_profitable_tickers.to_dict()['ProfitLoss']
    
    return least_profitable_tickers

def get_monthly_profitloss(df:pd.DataFrame):
    df_local = df.copy()
    df_local['month'] = pd.to_datetime(df_local['CloseDate']).dt.month
    monthly_profit_loss = pd.DataFrame(df_local.groupby('month')['ProfitLoss'].sum())
    monthly_profit_loss['month'] = monthly_profit_loss.index.map({1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'})
    monthly_profit_loss.index=monthly_profit_loss['month']
    monthly_profit_loss.drop(columns=['month'], inplace=True)
    
    return monthly_profit_loss.to_dict()['ProfitLoss']

def get_sector_profitloss(df:pd.DataFrame):
    
    df_local =df.copy()

    sector_pnl = pd.DataFrame(df_local.groupby('Sector')['ProfitLoss'].sum())

    # sector_pnl.index  = sector_pnl['Sector']

    # sector_pnl.drop(columns=['Sector'], inplace=True)

    return sector_pnl.to_dict()['ProfitLoss']
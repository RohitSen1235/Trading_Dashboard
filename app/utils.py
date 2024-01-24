import pandas as pd
import numpy as np

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

        #  # Define a custom formatter for the y-axis
        # def drawdown_formatter(x, pos):
        #     return f"${abs(x):,.2f}"  # Use absolute value for drawdowns

        # # return portfolio_df
        # # Plotting Time Series for Portfolio Value (Balance) at "Close" points
        # plt.figure(figsize=(12, 6))
        # plt.plot(self.portfolio_df['CloseDate'], self.portfolio_df['Portfolio_value'], marker='', linestyle='-', color='b')
        # plt.title('Portfolio Value at "Close" Points Over Time')
        # plt.xlabel('Date')
        # plt.ylabel('Portfolio Value')
        # plt.legend()
        # # Apply the custom formatter to the y-axis
        # plt.gca().yaxis.set_major_formatter(drawdown_formatter)
        # plt.grid(True)
        # plt.show()
        # return self.portfolio_df

    def compute_hit_ratio(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None

        # Calculate the hit ratio
        # hit_ratio = self.trades_df[self.trades_df['ProfitLoss'] >= 0].shape[0] / self.trades_df.shape[0]
        profitable_trades = self.trades_df[self.trades_df['ProfitLoss'] > 0].shape[0]
        loss_trades = self.trades_df[self.trades_df['ProfitLoss'] <= 0].shape[0]
        hit_ratio = np.round(profitable_trades / loss_trades,2)
        # print(f"Hit Ratio: {hit_ratio:.2f}")
        return hit_ratio, profitable_trades, loss_trades

    def get_drawdown_analysis(self):
        # compute portfolio value first
        self.compute_portfolio_value()
        
        df = self.portfolio_df[['CloseDate','Portfolio_value']].copy()

        # Calculate drawdowns
        df["PreviousPeak"] = df["Portfolio_value"].cummax()
        df["Drawdown"] = df["Portfolio_value"] - df["PreviousPeak"]

        # # Define a custom formatter for the y-axis
        # def drawdown_formatter(x, pos):
        #     return f"${abs(x):,.2f}"  # Use absolute value for drawdowns

        # # Plot drawdowns over time
        # plt.figure(figsize=(10, 6))
        # plt.plot(df["CloseDate"], df["Drawdown"], label="Drawdown")
        # plt.title("Portfolio Drawdown Analysis")
        # plt.xlabel("Close Date")
        # plt.ylabel("Drawdown")
        # plt.legend()

        # # Apply the custom formatter to the y-axis
        # plt.gca().yaxis.set_major_formatter(drawdown_formatter)

        # plt.grid(True)
        # plt.show()
        return df['CloseDate'].to_list(),df['Drawdown'].to_list()

    def get_intraday_trades(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None
        return self.trades_df[self.trades_df['IsIntraday'] == True]

    def get_swing_trades(self):
        if not self.Trades_Extracted:
            print("Error: Trades have not been extracted.")
            return None
        return self.trades_df[self.trades_df['IsIntraday'] == False]
    
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

        # returns dict of the dataframe
        return most_profitable_tickers.to_dict()
    
    def get_monthly_profitloss(self):

        df=self.trades_df.copy()
        df = pd.concat([df, self.MarginCall_df], ignore_index=True)
        df['month'] = pd.to_datetime(df['CloseDate']).dt.month
        monthly_profit_loss = pd.DataFrame(df.groupby('month')['ProfitLoss'].sum())
        monthly_profit_loss['month'] = monthly_profit_loss.index.map({1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'})
        monthly_profit_loss.index=monthly_profit_loss['month']
        monthly_profit_loss.drop(columns=['month'], inplace=True)
        
        return monthly_profit_loss.to_dict()
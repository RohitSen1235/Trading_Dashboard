from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd
import numpy as np
from app.utils import Trades, currency_abbreviation, compute_hit_ratio
from app.utils import compute_profit_loss,get_least_profitable_tickers,get_monthly_profitloss,get_most_profitable_tickers
from app.utils import get_sector_profitloss
from app.models import Ticker

data:Trades

def save_sector_db(request):
    content={}
    
    if request.method == "POST":
    
        if 'excelFile' in request.FILES:

            excel_file = request.FILES['excelFile']
            # Process the uploaded Excel file as needed
            # You can use libraries like pandas to read and manipulate the Excel data

            # Example: Print the name of the uploaded file
            print("Uploaded Excel file name:", excel_file.name)

            sector_data = pd.read_excel(excel_file)


            for index, row in sector_data.iterrows():
                
                if Ticker.objects.filter(ticker=row['Symbol']).exists:
                    print(f"Ticker Present : {row['Symbol']} , sector : {row['Sector']}")
                    ticker = Ticker.objects.filter(ticker=row['Symbol'])
                    ticker.update_sector(row['Sector'])
                                

    return render(request,"savedb.html",context=content)

# Create your views here.
def index(request):
    content={}
    return render(request,"index.html",context=content)

def dashboard(request):
    content={}
    
    global data

    if 'excelFile' in request.FILES:

        excel_file = request.FILES['excelFile']
        # Process the uploaded Excel file as needed
        # You can use libraries like pandas to read and manipulate the Excel data
        # Example: Print the name of the uploaded file
        print("Uploaded Excel file name:", excel_file.name)

        content['file_name'] = excel_file.name
        
        # data = pd.read_excel(excel_file)
        data = Trades(excel_file)
        
        # extracting trades mandatory step
        data.extract_trades()
        
        data.get_sector_for_all_Trades()
        print(data.trades_df)
        problamatic_tickers = data.get_sector_none()
        print(problamatic_tickers)
        # computing hit ratio
        content['hit_ratio'],content['n_profit_trades'],content['n_loss_trades'] = data.compute_hit_ratio()
        
        # getting count of different catagory of trades
        trades_all = data.get_num_trades()
        content['total_num_trades'] = trades_all[0]
        content['num_swing_trades'] = trades_all[1]
        content['num_intraday_trades'] = trades_all[2]
        content['num_margin_calls'] = trades_all[3]
        
        # get opening and closing balances
        balances = data.get_balance()
        content['opening_balance'] = currency_abbreviation(balances[0])
        content['closing_balance'] = currency_abbreviation(balances[1])
        content['profit'] = currency_abbreviation(balances[1] - balances[0])
        content['percentage_gain'] = np.round((balances[1] - balances[0])*100/balances[0], 2)
        content['profitable_tickers'] = data.get_most_profitable_tickers()
        content['loss_tickers']  =data.get_least_profitable_tickers()
        # Example: Save the file to a specific location
        # with open('path/to/save/' + excel_file.name, 'wb') as destination:
        #     for chunk in excel_file.chunks():
        #         destination.write(chunk)

    if request.method == "POST":
        pass
    
    return render(request,"dashboard.html",context=content)



def intraday_stats(request):

    content={"current_segment" : "Intraday"}

    global data

    intraday_data = data.get_intraday_trades()
    # computing hit ratio
    content['hit_ratio'],content['n_profit_trades'],content['n_loss_trades'] = compute_hit_ratio(intraday_data)
    
    content['profit'] = compute_profit_loss(intraday_data)
    content['profit_formated'] = currency_abbreviation(content['profit'])
    content['profitable_tickers'] = get_most_profitable_tickers(intraday_data)
    content['loss_tickers']  =get_least_profitable_tickers(intraday_data)
    content['segment'] = "intraday"

    return render(request,"segment_stats.html",context=content)

def swing_stats(request):

    content={"current_segment" : "Intraday"}

    global data

    swing_data = data.get_swing_trades()
    # computing hit ratio
    content['hit_ratio'],content['n_profit_trades'],content['n_loss_trades'] = compute_hit_ratio(swing_data)
    
    content['profit'] = compute_profit_loss(swing_data)
    content['profit_formated'] = currency_abbreviation(content['profit'])
    content['profitable_tickers'] = get_most_profitable_tickers(swing_data)
    content['loss_tickers']  =get_least_profitable_tickers(swing_data)
    content['segment'] = "swing"

    return render(request,"segment_stats.html",context=content)


def get_overall_hitratio(request):
    global data

    _,n_wins,n_losses = data.compute_hit_ratio()
    print(f"get_hitratio API called")
    return JsonResponse({'hit_ratio':[n_wins,n_losses]})


def get_overall_monthly_profitloss(request):

    global data

    monthly_pnl = data.get_monthly_profitloss()
    bar_colors = ["red" if value < 0 else "green" for key, value in monthly_pnl.items()]
    print(bar_colors)
    print(f"monthly_pnl {monthly_pnl}")
    return JsonResponse({'monthly_pnl':monthly_pnl,
                         'bar_colors':bar_colors})

def get_overall_sector_profitloss(request):

    global data

    sector_pnl = data.get_sector_profitloss()
    bar_colors = ["red" if value < 0 else "green" for key, value in sector_pnl.items()]
    print(bar_colors)
    print(f"monthly_pnl {sector_pnl}")
    return JsonResponse({'sector_pnl':sector_pnl,
                         'bar_colors':bar_colors})

def get_drawdown_analysis(request):
    
    global data

    X,Y = data.get_drawdown_analysis()
    
    return JsonResponse({'date':X,
                         'drawdown':Y})

def get_segment_hitratio(request,segment):
    global data

    if segment == "intraday":
        segment_data = data.get_intraday_trades()
    elif segment == "swing":
        segment_data = data.get_swing_trades()
    else:
        segment_data = data.trades_df
    
    _,n_wins,n_losses = compute_hit_ratio(segment_data)    
    
    return JsonResponse({'hit_ratio':[n_wins,n_losses]})

def get_segment_monthly_profitloss(request,segment):

    global data

    if segment == "intraday":
        segment_data = data.get_intraday_trades()
    elif segment == "swing":
        segment_data = data.get_swing_trades()
    else:
        segment_data = data.trades_df
        
    monthly_pnl = get_monthly_profitloss(segment_data)
    # monthly_pnl = monthly_pnl['ProfitLoss']
    bar_colors = ["red" if value < 0 else "green" for key, value in monthly_pnl.items()]

    return JsonResponse({'monthly_pnl':monthly_pnl,
                         'bar_colors':bar_colors})

def get_segment_sector_profitloss(request,segment):

    global data

    if segment == "intraday":
        segment_data = data.get_intraday_trades()
    elif segment == "swing":
        segment_data = data.get_swing_trades()
    else:
        segment_data = data.trades_df
        
    sector_pnl = get_sector_profitloss(segment_data)
    # sector_pnl = sector_pnl['ProfitLoss']
    bar_colors = ["red" if value < 0 else "green" for key, value in sector_pnl.items()]

    return JsonResponse({'sector_pnl':sector_pnl,
                         'bar_colors':bar_colors})
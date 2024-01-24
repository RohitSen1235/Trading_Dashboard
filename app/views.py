from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd
import numpy as np
from app.utils import Trades, currency_abbreviation

data:Trades

# Create your views here.
def index(request):
    content={}
    return render(request,"index.html",context=content)

def dashboard(request):
    content={}
    
    global data

    if request.method == "POST":
    
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
    
    return render(request,"dashboard.html",context=content)

def get_hitratio(request):
    global data

    _,n_wins,n_losses = data.compute_hit_ratio()
    print(f"get_hitratio API called")
    return JsonResponse({'hit_ratio':[n_wins,n_losses]})

def get_monthly_profitloss(request):

    global data

    monthly_pnl = data.get_monthly_profitloss()['ProfitLoss']
    bar_colors = ["red" if value < 0 else "green" for key, value in monthly_pnl.items()]
    print(bar_colors)
    print(f"monthly_pnl {monthly_pnl}")
    return JsonResponse({'monthly_pnl':monthly_pnl,
                         'bar_colors':bar_colors})

def get_drawdown_analysis(request):
    
    global data

    X,Y = data.get_drawdown_analysis()
    
    return JsonResponse({'date':X,
                         'drawdown':Y})
from django.shortcuts import render
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd

data:pd.DataFrame

# Create your views here.
def index(request):
    content={}
    return render(request,"index.html",context=content)

def dashboard(request):
    content={}
    
    global data

    if request.method == "POST":
    
        if 'excelFile' in request.FILES:
            global data
            excel_file = request.FILES['excelFile']
            # Process the uploaded Excel file as needed
            # You can use libraries like pandas to read and manipulate the Excel data

            # Example: Print the name of the uploaded file
            print("Uploaded Excel file name:", excel_file.name)

            content['file_name'] = excel_file.name
            
            data = pd.read_excel(excel_file)

            print(data.head(10))

            # Example: Save the file to a specific location
            # with open('path/to/save/' + excel_file.name, 'wb') as destination:
            #     for chunk in excel_file.chunks():
            #         destination.write(chunk)
    
    return render(request,"dashboard.html",context=content)
from django.db import models
import pandas as pd

class Ticker(models.Model):
    ticker=models.CharField(unique=True,max_length = 32)
    company_name = models.CharField(null=True, max_length = 128)
    industry = models.CharField(max_length = 512)
    sector = models.CharField(null=True, max_length = 128)

    def is_ticker_present(self,ticker_name):
        # Check if the ticker exists in the database
        return self.objects.filter(ticker=ticker_name).exists()
    
    def update_sector(self, sector_name):
        self.sector = sector_name
        self.save()

    def get_sector_name(self):
        return self.sector
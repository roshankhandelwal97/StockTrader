from django.db import models
from django.conf import settings
from django.db.models import F, DecimalField

class Transaction(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRANSACTION_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticker_name = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    total_amount = models.DecimalField(max_digits=20, decimal_places=10)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticker_name = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    money_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'ticker_name')
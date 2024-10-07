from django.contrib import admin
from .models import Transaction, Portfolio


admin.site.register(Transaction)
admin.site.register(Portfolio)
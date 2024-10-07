from django.urls import path
from .views import BuyStockView, SellStockView, StockDetailView, PortfolioView, StockDetailUserView

urlpatterns = [
    path('buy/', BuyStockView.as_view(), name='buy_stock'),
    path('sell/', SellStockView.as_view(), name='sell_stock'),
    path('stock/<str:ticker>/', StockDetailView.as_view(), name='stock_detail'),
    path('stock/user/<str:ticker>/', StockDetailUserView.as_view(), name='stock_details'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio_view'),


]

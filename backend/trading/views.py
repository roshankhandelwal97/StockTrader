import yfinance as yf
from django.db.models import F, DecimalField
from decimal import Decimal, getcontext
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Transaction, Portfolio
from django.db.models import F


class StockDetailView(views.APIView):

    permission_classes = [AllowAny]
    def get(self, request, ticker):
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            stock_info = {
                'ticker': ticker,
                'current_price': data['Close'].iloc[-1],
                'open': data['Open'].iloc[-1],
                'high': data['High'].iloc[-1],
                'low': data['Low'].iloc[-1],
                'volume': data['Volume'].iloc[-1]
            }
            return Response(stock_info, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No data found for the specified ticker.'}, status=status.HTTP_404_NOT_FOUND)

class StockDetailUserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        # Get the current user
        user = request.user
        
        # Get the latest transaction for this ticker
        latest_transaction = Transaction.objects.filter(
            user=user, ticker_name=ticker
        ).order_by('-id').first()

        # Get the current portfolio entry
        portfolio_entry = Portfolio.objects.get(user=user, ticker_name=ticker)

        # Fetch the current price using yfinance
        stock = yf.Ticker(ticker)
        current_price_data = stock.history(period="1d")
        if not current_price_data.empty:
            current_price = Decimal(current_price_data['Close'].iloc[-1])  # Convert to Decimal
        else:
            current_price = None
        # Calculate profit/loss
        if current_price is not None:
            total_invested = portfolio_entry.money_invested
            current_value = current_price * portfolio_entry.quantity
            portfolio_profit_loss = portfolio_entry.profit_loss
            # current_profit_loss = current_value - total_invested
        else:
            profit_loss = None

        # Prepare response
        response_data = {
            'name': ticker,
            'last_price': latest_transaction.price if latest_transaction else None,
            'current_price': current_price,
            'total_quantity': portfolio_entry.quantity,
            # 'profit_loss_current': profit_loss,
            'portfolio_profit_loss': portfolio_profit_loss
        }

        return Response(response_data, status=status.HTTP_200_OK)    

class BuyStockView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker_name = request.data.get('ticker_name')
        quantity = Decimal(request.data.get('quantity'))  # Convert input to Decimal
        stock_info = yf.Ticker(ticker_name)
        price = Decimal(stock_info.history(period="1d").iloc[-1]['Close'])
        total_amount = price * quantity

        Transaction.objects.create(
            user=request.user,
            ticker_name=ticker_name,
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            transaction_type=Transaction.BUY
        )

        portfolio, created = Portfolio.objects.get_or_create(
            user=request.user,
            ticker_name=ticker_name,
            defaults={'quantity': Decimal('0.0'), 'money_invested': Decimal('0.0'), 'profit_loss': Decimal('0.0')}
        )
        if not created:
            portfolio.quantity = F('quantity') + quantity
            portfolio.money_invested = F('money_invested') + total_amount
        else:
            portfolio.quantity = quantity
            portfolio.money_invested = total_amount

        portfolio.save()

        return Response({
            'ticker_name': ticker_name,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount
        }, status=status.HTTP_201_CREATED)

class SellStockView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker_name = request.data.get('ticker_name')
        quantity = Decimal(request.data.get('quantity'))  # Convert input to Decimal
        portfolio = Portfolio.objects.get(user=request.user, ticker_name=ticker_name)

        if portfolio.quantity < quantity:
            return Response({'error': 'Not enough stock in portfolio'}, status=status.HTTP_400_BAD_REQUEST)

        stock_info = yf.Ticker(ticker_name)
        price = Decimal(stock_info.history(period="1d").iloc[-1]['Close'])
        total_amount = price * quantity

        Transaction.objects.create(
            user=request.user,
            ticker_name=ticker_name,
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            transaction_type=Transaction.SELL
        )

        portfolio.quantity -= quantity
        portfolio.money_invested -= total_amount
        portfolio.save()

        return Response({
            'ticker_name': ticker_name,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount
        }, status=status.HTTP_200_OK)

class PortfolioView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all portfolio entries for the logged-in user
        portfolios = Portfolio.objects.filter(user=request.user)
        # Prepare data to return
        data = [{
            'ticker_name': portfolio.ticker_name,
            'quantity': portfolio.quantity
        } for portfolio in portfolios]

        return Response(data, status=status.HTTP_200_OK)

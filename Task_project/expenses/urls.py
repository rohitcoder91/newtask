# expenses/urls.py
from django.urls import path
from .views import add_expense, show_balances,show_all_userbalances

urlpatterns = [
    path('add_expense/', add_expense, name='add_expense'),
    path('show_balances/', show_all_userbalances, name='all_balances'),
    path('show_balances/<str:user_id>/', show_balances, name='show_balances'),
]

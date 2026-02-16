from django.urls import path
from . import views
app_name = 'inventory'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('parts/', views.part_list, name='part_list'),
    path('parts/<int:part_id>/recommendations/', views.part_recommendations, name='part_recommendations'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('payments/', views.payment_list, name='payment_list'),
    path('ai/forecast/<int:part_id>/', views.forecast_part_sales, name='forecast_part_sales'),
]

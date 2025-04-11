from .views import StockReportJSON
from django.urls import path, include

urlpatterns = [
    path('report-json/<str:item_code>/', StockReportJSON.as_view(), name='stock-report'),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.urls')),  
    path('api/', include('purchase.urls')),
    path('api/', include('sell.urls')),
    path('api/', include('report.urls'))
]

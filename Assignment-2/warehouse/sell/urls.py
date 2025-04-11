from .views import SellHeaderViewSet, SellDetailViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'sell', SellHeaderViewSet, basename='sell')

sell_detail = SellDetailViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = router.urls + [
    path('sell/<str:header_code>/details/', sell_detail, name='sell-detail'),
]

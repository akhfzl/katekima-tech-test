from .views import PurchaseHeaderViewSet, PurchaseDetailViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'purchase', PurchaseHeaderViewSet, basename='purchase')

purchase_detail = PurchaseDetailViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = router.urls + [
    path('purchase/<str:header_code>/details/', purchase_detail, name='purchase-detail'),
]

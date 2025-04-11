from django.shortcuts import render
from .serializers import PurchaseDetailSerializer, PurchaseHeaderSerializer, PurchaseHeader, PurchaseDetail
from rest_framework import viewsets, status
from rest_framework.response import Response

class PurchaseHeaderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseHeaderSerializer
    queryset = PurchaseHeader.objects.filter(is_deleted=False)
    lookup_field = 'code'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            {
                "code": status.HTTP_204_NO_CONTENT,
                "message": "Purchase header deleted successfully"
            },
            status=status.HTTP_200_OK  
        )

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseDetailSerializer

    def get_queryset(self):
        return PurchaseDetail.objects.filter(
            is_deleted=False,
            header__code=self.get_header_code()
        )
    
    def get_header_code(self):
        return self.kwargs['header_code']

    def perform_create(self, serializer):
        header_code = self.get_header_code()
        try:
            header = PurchaseHeader.objects.get(code=header_code)
        except PurchaseHeader.DoesNotExist:
            return Response(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid purchase header code."
                },
                status=status.HTTP_200_OK  
            )
        serializer.save(header=header)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            {
                "code": status.HTTP_204_NO_CONTENT,
                "message": "Purchase detail deleted successfully"
            },
            status=status.HTTP_200_OK  
        )

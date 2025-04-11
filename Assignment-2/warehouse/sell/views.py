from django.shortcuts import render
from .serializers import SellHeaderSerializer, SellDetailSerializer, SellHeader, SellDetail
from rest_framework import viewsets, status
from rest_framework.response import Response

class SellHeaderViewSet(viewsets.ModelViewSet):
    serializer_class = SellHeaderSerializer
    queryset = SellHeader.objects.filter(is_deleted=False)
    lookup_field = 'code' 

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(
            {
                "code": status.HTTP_204_NO_CONTENT,
                "message": "Sell header deleted successfully"
            },
            status=status.HTTP_200_OK 
        )

class SellDetailViewSet(viewsets.ModelViewSet):
    serializer_class = SellDetailSerializer

    def get_queryset(self):
        return SellDetail.objects.filter(
            is_deleted=False,
            header__code=self.kwargs['header_code']
        )

    def perform_create(self, serializer):
        header_code = self.kwargs['header_code']
        try:
            header = SellHeader.objects.get(code=header_code)
        except SellHeader.DoesNotExist:
            return Response(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid Sell header code."
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
                "message": "Sell detail deleted successfully"
            },
            status=status.HTTP_200_OK 
        )

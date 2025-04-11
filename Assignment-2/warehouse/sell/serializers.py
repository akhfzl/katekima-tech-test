from .models import SellHeader, SellDetail
from rest_framework import serializers

class SellHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellHeader
        fields = '__all__'

class SellDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellDetail
        exclude = ['header'] 

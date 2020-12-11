from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Fridge


class UserSerializer(serializers.ModelSerializer):
    fridges = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',  'fridges']


class ProductSerializer(serializers.ModelSerializer):
    fridge_id = serializers.PrimaryKeyRelatedField(queryset=Fridge.objects.get_queryset())

    class Meta:
        model = Product
        fields = ('id', 'product_name', 'quantity_g', 'quantity', 'carbohydrates', 'energy_kcal', 'fat', 'fiber',
                  'proteins', 'sugar', 'salt', 'sodium', 'image_url', 'date_added', 'expiration_date', 'fridge_id')


class FridgeSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Fridge
        fields = ('id', 'fridge_name', 'user_id', 'products')

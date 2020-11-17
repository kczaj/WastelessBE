from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product


class UserSerializer(serializers.HyperlinkedModelSerializer):
    products = serializers.HyperlinkedRelatedField(many=True, view_name='product-detail', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'products']


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ('product_name', 'quantity_g', 'quantity', 'carbohydrates', 'energy_kcal', 'fat', 'fiber',
                  'proteins', 'salt', 'sodium', 'image_url', 'date_added', 'expiration_date', 'fridge_id',
                  'user_id')

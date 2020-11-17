from rest_framework import serializers

from .models import User, Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('product_name', 'quantity_g', 'quantity', 'carbohydrates', 'energy_kcal', 'fat', 'fiber',
                  'proteins', 'salt', 'sodium', 'image_url', 'date_added', 'expiration_date', 'fridge_id',
                  'user_id')

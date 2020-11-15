from django.shortcuts import render

from rest_framework import viewsets

from .serializers import UserSerializer, ProductSerializer
from .models import User, Product


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('product_name')
    serializer_class = ProductSerializer

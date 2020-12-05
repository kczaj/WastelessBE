from django.shortcuts import render

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User

from .serializers import ProductSerializer, UserSerializer, FridgeSerializer
from .models import Product, Fridge


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all().order_by('product_name')
    serializer_class = ProductSerializer


class FridgeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Fridge.objects.all().order_by('fridge_name')
    serializer_class = FridgeSerializer

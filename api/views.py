from django.shortcuts import render

from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User

from .serializers import ProductSerializer, UserSerializer, FridgeSerializer
from .models import Product, Fridge


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserViewSet(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all().order_by('product_name')
    serializer_class = ProductSerializer


class FridgeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Fridge.objects.all().order_by('fridge_name')
    serializer_class = FridgeSerializer

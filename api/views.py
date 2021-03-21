from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets, mixins, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg

from .models import Product, Fridge, Recipe, Comment, Rating
from .serializers import ProductSerializer, UserSerializer, FridgeSerializer, UserCreateSerializer, \
    ChangePasswordSerializer, RecipeSerializer, CommentSerializer, RatingSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                         generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class CurrentUserFridges(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FridgeSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
        return Fridge.objects.filter(user_id=user)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all().order_by('product_name')
    serializer_class = ProductSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all().order_by('recipe_name')
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        ingredients = self.request.query_params.get('ingredients', None)
        tags = self.request.query_params.get('tags', None)
        difficulty = self.request.query_params.get('difficulty', None)
        meal = self.request.query_params.get('meal', None)
        queryset = Recipe.objects.annotate(
            ratings_num=Count('ratings'),
            rating=Avg('ratings__rating'))
        if ingredients is not None:
            queryset = queryset.filter(ingredients__contains=ingredients)
        if tags is not None:
            queryset = queryset.filter(tags__contains=tags)
        if difficulty is not None:
            queryset = queryset.filter(difficulty__contains=difficulty)
        if meal is not None:
            queryset = queryset.filter(meal__contains=meal)

        return queryset

class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class RatingForUserViewSet(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'recipe_id'

    def get_queryset(self):
        user = self.request.user
        r_id = self.kwargs['recipe_id']
        return Rating.objects.filter(recipe_id=r_id, user_id=user)

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['user_id'] = self.request.user.id
        return self.create(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Comment.objects.all().order_by('date_added')
    serializer_class = CommentSerializer


class FridgeProductViewSet(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        f_id = self.kwargs['fridge_id']
        return Product.objects.filter(fridge_id=f_id)


class FridgeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Fridge.objects.all().order_by('fridge_name')
    serializer_class = FridgeSerializer


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })


class Logout(APIView):
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return JsonResponse({'message': 'Logged out correctly'}, status=200)

from functools import reduce
from itertools import combinations
import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets, mixins, generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, FloatField, F, Sum, Q
from django.db.models.functions import Coalesce, Cast

from .models import Product, Fridge, Recipe, Comment, Rating, Ingredient
from .serializers import ProductSerializer, UserSerializer, FridgeSerializer, UserCreateSerializer, \
    ChangePasswordSerializer, RecipeSerializer, CommentSerializer, RatingSerializer, IngredientSerializer


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


class CurrentUserFridges(generics.ListAPIView, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = FridgeSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
        return Fridge.objects.filter(user_id=user)

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['user_id'] = self.request.user.id
        return self.create(request, *args, **kwargs)


class CurrentUserRecipes(generics.ListAPIView, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(user_id=user)

    def post(self, request, *args, **kwargs):
        request.data['user_id'] = self.request.user.id
        return self.create(request, *args, **kwargs)


class CurrentUserComments(generics.ListAPIView, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(author=user)

    def post(self, request, *args, **kwargs):
        request.data['author'] = self.request.user.id
        return self.create(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all().order_by('product_name')
    serializer_class = ProductSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all().order_by('ingredient_name')

    def get_queryset(self):
        queryset = Ingredient.objects.all().order_by('ingredient_name')
        ingredient = self.request.query_params.get('ingredient', None)
        if ingredient is not None:
            ingredient = ingredient.lower()
            queryset = queryset.filter(ingredient_name__contains=ingredient)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all().order_by('recipe_name')
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        recipe_name = self.request.query_params.get('name', None)
        ingredients = self.request.query_params.get('ingredients', None)
        tags = self.request.query_params.get('tags', None)
        difficulty = self.request.query_params.get('difficulty', None)
        meal = self.request.query_params.get('meal', None)
        order = self.request.query_params.get('order', None)
        order_dict = {'pp': '-popularity', 'na': 'recipe_name', 'nd': '-recipe_name', 'ra': 'rating', 'rd': '-rating',
                      'pa': 'ratings_num', 'pd': '-ratings_num', 'ta': 'prep_time', 'td': '-prep_time'}
        queryset = Recipe.objects.annotate(
            ratings_num=Count('ratings'),
            rating=Coalesce(Avg('ratings__rating'), 0),
            popularity=Cast(Count('ratings'), FloatField()) * Cast(Coalesce(Avg('ratings__rating'), 1) ** 2,
                                                                FloatField()) + (
                               Cast(Count('comments'), FloatField()) - Cast('ratings_num', FloatField()))
        )
        if recipe_name is not None:
            queryset = queryset.filter(recipe_name__icontains=recipe_name)
        if ingredients is not None:
            queryset = queryset.filter(ingredients__contains=ingredients)
        if tags is not None:
            queryset = queryset.filter(tags__contains=tags)
        if difficulty is not None:
            queryset = queryset.filter(difficulty__contains=difficulty)
        if meal is not None:
            queryset = queryset.filter(meal__contains=meal)
        if order is not None:
            if order in order_dict:
                queryset = queryset.order_by(order_dict.get(order))
            else:
                queryset = queryset.order_by(order_dict.get('pp'))
        else:
            queryset = queryset.order_by(order_dict.get('pp'))

        return queryset


class RecommendationsForFridgeViewSet(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        f_id = self.kwargs['fridge_id']
        fridge_ingredients = Product.objects.filter(fridge_id=f_id).values_list('category', flat=True)
        recipes = Recipe.objects.all()
        recommendations = set()
        for recipe in recipes:
            num_of_ingredients = len(recipe.ingredients)
            required_ingredients = round(0.7 * num_of_ingredients)
            present_ingredients = 0
            recipe_ingredients = [row[0] for row in recipe.ingredients]
            for ingredient in fridge_ingredients:
                if ingredient in recipe_ingredients:
                    present_ingredients += 1
            if present_ingredients >= required_ingredients:
                recommendations.add(recipe.id)

        queryset = recipes.filter(id__in=recommendations)

        recipe_name = self.request.query_params.get('name', None)
        ingredients = self.request.query_params.get('ingredients', None)
        tags = self.request.query_params.get('tags', None)
        difficulty = self.request.query_params.get('difficulty', None)
        meal = self.request.query_params.get('meal', None)
        order = self.request.query_params.get('order', None)
        order_dict = {'pp': '-popularity', 'na': 'recipe_name', 'nd': '-recipe_name', 'ra': 'rating', 'rd': '-rating',
                      'pa': 'ratings_num', 'pd': '-ratings_num', 'ta': 'prep_time', 'td': '-prep_time'}
        queryset = queryset.annotate(
            ratings_num=Count('ratings'),
            rating=Coalesce(Avg('ratings__rating'), 0),
            popularity=Cast(Count('ratings'), FloatField()) * Cast(Coalesce(Avg('ratings__rating'), 1) ** 2,
                                                                FloatField()) + (
                               Cast(Count('comments'), FloatField()) - Cast('ratings_num', FloatField()))
        )
        if recipe_name is not None:
            queryset = queryset.filter(recipe_name__icontains=recipe_name)
        if ingredients is not None:
            queryset = queryset.filter(ingredients__contains=ingredients)
        if tags is not None:
            queryset = queryset.filter(tags__contains=tags)
        if difficulty is not None:
            queryset = queryset.filter(difficulty__contains=difficulty)
        if meal is not None:
            queryset = queryset.filter(meal__contains=meal)
        if order is not None:
            if order in order_dict:
                queryset = queryset.order_by(order_dict.get(order))
            else:
                queryset = queryset.order_by(order_dict.get('pp'))
        else:
            queryset = queryset.order_by(order_dict.get('pp'))

        return queryset


class UrgentRecommendationsForFridgeViewSet(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        f_id = self.kwargs['fridge_id']
        fridge_ingredients = Product.objects.filter(fridge_id=f_id)
        expiring_ingredients = list()

        for ingredient in fridge_ingredients:
            expiration_date = ingredient.expiration_date
            diff = expiration_date.date() - datetime.date.today()
            if diff.days < 3:
                expiring_ingredients.append(ingredient.category)
        if not expiring_ingredients:
            return Recipe.objects.none()

        recipes = Recipe.objects.all()
        recommendations = set()
        for recipe in recipes:
            num_of_ingredients = len(expiring_ingredients)
            required_ingredients = round(0.7 * num_of_ingredients)
            present_ingredients = 0
            recipe_ingredients = [row[0] for row in recipe.ingredients]
            for ingredient in expiring_ingredients:
                if ingredient in recipe_ingredients:
                    present_ingredients += 1
            if present_ingredients >= required_ingredients:
                recommendations.add(recipe.id)

        queryset = recipes.filter(id__in=recommendations)

        recipe_name = self.request.query_params.get('name', None)
        ingredients = self.request.query_params.get('ingredients', None)
        tags = self.request.query_params.get('tags', None)
        difficulty = self.request.query_params.get('difficulty', None)
        meal = self.request.query_params.get('meal', None)
        order = self.request.query_params.get('order', None)
        order_dict = {'pp': '-popularity', 'na': 'recipe_name', 'nd': '-recipe_name', 'ra': 'rating', 'rd': '-rating',
                      'pa': 'ratings_num', 'pd': '-ratings_num', 'ta': 'prep_time', 'td': '-prep_time'}
        queryset = queryset.annotate(
            ratings_num=Count('ratings'),
            rating=Coalesce(Avg('ratings__rating'), 0),
            popularity=Cast(Count('ratings'), FloatField()) * Cast(Coalesce(Avg('ratings__rating'), 1) ** 2,
                                                                FloatField()) + (
                               Cast(Count('comments'), FloatField()) - Cast('ratings_num', FloatField()))
        )
        if recipe_name is not None:
            queryset = queryset.filter(recipe_name__icontains=recipe_name)
        if ingredients is not None:
            queryset = queryset.filter(ingredients__contains=ingredients)
        if tags is not None:
            queryset = queryset.filter(tags__contains=tags)
        if difficulty is not None:
            queryset = queryset.filter(difficulty__contains=difficulty)
        if meal is not None:
            queryset = queryset.filter(meal__contains=meal)
        if order is not None:
            if order in order_dict:
                queryset = queryset.order_by(order_dict.get(order))
            else:
                queryset = queryset.order_by(order_dict.get('pp'))
        else:
            queryset = queryset.order_by(order_dict.get('pp'))

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

from django.contrib.auth import password_validation
from django.contrib.auth.models import User, UserManager
from rest_framework import serializers

from .models import Product, Fridge, Recipe, Comment, Rating


class UserSerializer(serializers.ModelSerializer):
    fridges = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'fridges']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user = User.objects.create_user(username, email, password)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Your old password was entered incorrectly. Please enter it again.'
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': "The two password fields didn't match."})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    fridge_id = serializers.PrimaryKeyRelatedField(queryset=Fridge.objects.get_queryset())

    class Meta:
        model = Product
        fields = (
            'id', 'product_name', 'categories', 'quantity_g', 'quantity', 'carbohydrates', 'energy_kcal', 'fat',
            'fiber',
            'proteins', 'sugar', 'salt', 'sodium', 'image_url', 'date_added', 'expiration_date', 'fridge_id')


class RecipeSerializer(serializers.ModelSerializer):
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    rating = serializers.FloatField(required=False)
    ratings_num = serializers.IntegerField(required=False)

    class Meta:
        model = Recipe
        fields = (
        'id', 'user_id', 'recipe_name', 'difficulty', 'tags', 'ingredients', 'description', 'instructions', 'image_url',
        'meal', 'prep_time', 'rating', 'ratings_num', 'comments')


class CommentSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.get_queryset())

    class Meta:
        model = Comment
        fields = ('id', 'author', 'date_added', 'content', 'recipe_id')


class RatingSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.get_queryset())

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'recipe_id', 'user_id')

    def create(self, validated_data):
        return Rating.objects.create(**validated_data)


class FridgeSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Fridge
        fields = ('id', 'fridge_name', 'user_id', 'products')

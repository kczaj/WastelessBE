from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.


class Fridge(models.Model):
    fridge_name = models.CharField(max_length=50)
    user_id = models.ForeignKey('auth.User', related_name='fridges', on_delete=models.CASCADE)

    def __str__(self):
        return self.fridge_name


class Product(models.Model):
    product_name = models.CharField(max_length=150)
    quantity_g = models.FloatField()
    quantity = models.IntegerField()
    carbohydrates = models.FloatField()
    energy_kcal = models.IntegerField()
    fat = models.FloatField()
    fiber = models.FloatField()
    proteins = models.FloatField()
    salt = models.FloatField()
    sugar = models.FloatField(default=0.0)
    sodium = models.FloatField()
    image_url = models.CharField(max_length=200, blank=True)
    date_added = models.DateTimeField()
    expiration_date = models.DateTimeField()
    fridge_id = models.ForeignKey(Fridge, related_name='products', on_delete=models.CASCADE)
    categories = ArrayField(models.CharField(max_length=50, blank=True), blank=False, null=True)

    def __str__(self):
        return self.product_name


class Recipe(models.Model):
    user_id = models.ForeignKey('auth.User', related_name='recipes', on_delete=models.CASCADE, null=True)
    recipe_name = models.CharField(max_length=200)
    ingredients = ArrayField(ArrayField(models.CharField(max_length=50, blank=True), blank=False, default=list, size=3),
                             default=list)
    tags = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)
    DIFFICULTY_CHOICES = [('BG', 'Beginner'), ('IT', 'Intermediate'), ('AD', 'Advanced')]
    difficulty = models.CharField(
        max_length=2,
        choices=DIFFICULTY_CHOICES,
        default='BG',
    )
    description = models.TextField()
    instructions = models.TextField()
    image_url = models.TextField()
    MEAL_CHOICES = [('BF', 'Breakfast'), ('LU', 'Lunch'), ('DN', 'Dinner'), ('SU', 'Supper')]
    meal = models.CharField(max_length=2, choices=MEAL_CHOICES, default='BF')
    prep_time = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.recipe_name


class Comment(models.Model):
    author = models.ForeignKey('auth.User', related_name='comments', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    date_added = models.DateTimeField()
    content = models.TextField()
    recipe_id = models.ForeignKey(Recipe, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Rating(models.Model):
    user_id = models.ForeignKey('auth.User', related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    recipe_id = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.id

from django.db import models


# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.CharField(max_length=30)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=40)
    token = models.CharField(max_length=50, unique=True, blank=True)
    user_id = models.CharField(max_length=50, primary_key=True, unique=True)

    def __str__(self):
        return self.user_id


class Product(models.Model):
    product_name = models.CharField(max_length=30)
    quantity_g = models.IntegerField()
    quantity = models.IntegerField()
    carbohydrates = models.IntegerField()
    energy_kcal = models.IntegerField()
    fat = models.IntegerField()
    fiber = models.IntegerField()
    proteins = models.IntegerField()
    salt = models.IntegerField()
    sodium = models.IntegerField()
    image_url = models.CharField(max_length=100)
    date_added = models.DateField()
    expiration_date = models.DateField()
    fridge_id = models.CharField(max_length=50, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

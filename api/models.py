from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.


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
    fridge_id = models.CharField(max_length=50, blank=True)
    user_id = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

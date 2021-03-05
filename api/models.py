from django.db import models


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
    image_url = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField()
    expiration_date = models.DateTimeField()
    fridge_id = models.ForeignKey(Fridge, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

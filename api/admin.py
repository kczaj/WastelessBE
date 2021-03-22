from django.contrib import admin
from .models import Product, Fridge, Recipe, Comment, Rating
# Register your models here.
admin.site.register(Product)
admin.site.register(Fridge)
admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(Rating)

from django.contrib import admin
from .models import Product, Fridge, Recipe, Comment, Rating, Ingredient
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
import json

# Register your models here.

admin.site.register(Fridge)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Ingredient)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'category', 'date_added', 'expiration_date')
    list_filter = ('category',)
    ordering = ("-date_added",)

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            Product.objects.annotate(date=TruncDay("date_added"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe_name', 'difficulty', 'meal')
    list_filter = ('difficulty', 'meal')

    def changelist_view(self, request, extra_context=None):
        difficulties = (Recipe.objects.order_by("difficulty").values('difficulty').annotate(count=Count("difficulty")))
        to_json = {'difficulties': json.dumps(list(difficulties), cls=DjangoJSONEncoder)}
        to_json['difficulties'] = to_json['difficulties'].replace("BG", "Beginner")
        to_json['difficulties'] = to_json['difficulties'].replace("IT", "Intermediate")
        to_json['difficulties'] = to_json['difficulties'].replace("AD", "Advanced")
        meals = (Recipe.objects.order_by("meal").values('meal').annotate(count=Count("meal")))
        to_json["meals"] = json.dumps(list(meals), cls=DjangoJSONEncoder)
        to_json['meals'] = to_json['meals'].replace("BF", "Breakfast")
        to_json['meals'] = to_json['meals'].replace("LU", "Lunch")
        to_json['meals'] = to_json['meals'].replace("DN", "Dinner")
        to_json['meals'] = to_json['meals'].replace("SU", "Supper")

        # Serialize and attach the chart data to the template context
        extra_context = extra_context or {"chart_data": to_json}
        print(to_json)

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')
    ordering = ("-date_joined",)

    def changelist_view(self, request, extra_context=None):
        chart_data = (
            User.objects.annotate(date=TruncDay("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        print(as_json)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

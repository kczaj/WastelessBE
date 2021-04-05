from django.contrib import admin
from .models import Product, Fridge, Recipe, Comment, Rating, Ingredient
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
import json

# Register your models here.
admin.site.register(Product)
admin.site.register(Fridge)
admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Ingredient)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')
    ordering = ("-date_joined",)

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            User.objects.annotate(date=TruncDay("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

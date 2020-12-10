from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'fridges', views.FridgeViewSet)
# router.register(r'profile', views.CurrentUserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('profile/', views.CurrentUserViewSet.as_view())
]
from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'fridges', views.FridgeViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'comments', views.CommentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.CurrentUserViewSet.as_view()),
    path('profile/fridges/', views.CurrentUserFridges.as_view()),
    path('profile/changepassword', views.ChangePasswordView.as_view()),
    path('register/', views.UserCreate.as_view()),
    path('login/', views.CustomAuthToken.as_view()),
    path('logout/', views.Logout.as_view()),
    path('fridge/<int:fridge_id>/', views.FridgeProductViewSet.as_view())
]

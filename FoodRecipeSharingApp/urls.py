from django.urls import include, path
from rest_framework import routers
from FoodRecipeSharingApp.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


router=routers.DefaultRouter()
router.register(r'recipe',RecipeViewset)
router.register(r'category',CategoryViewset)
router.register(r'rating',RatingViewset)
router.register(r'users',UserViewSet)
router.register(r'recipe-step',RecipeStepViewSet)
router.register(r'review',ReviewViewset)
router.register(r'favourite',FavouriteViewset)
urlpatterns = [
    path("",include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


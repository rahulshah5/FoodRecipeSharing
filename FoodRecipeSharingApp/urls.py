from django.urls import include, path
from rest_framework import routers
from FoodRecipeSharingApp.views import *

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


router=routers.DefaultRouter()
router.register(r'recipe',RecipeViewset,basename="recipe")
router.register(r'category',CategoryViewset, basename="category")
router.register(r'rating',RatingViewset,basename="rating")
router.register(r'recipe-step',RecipeStepViewSet, basename="recipe-step")
router.register(r'review',ReviewViewset,basename="review")
router.register(r'favourite',FavouriteViewset,basename='favourite')
router.register(r'post-recipe-steps',RecipeStepViewSet,basename="post-recipe-steps")
router.register(r'post-recipe-image',RecipeImageViewSet,basename="post-recipe-images")

urlpatterns = [
    path("",include(router.urls)),
    path("search/",SearchViewSet.as_view(),name="search"),
    path('register/',UserRegisterViewSet.as_view(),name='register-user'),
    path('login/',UserLoginViewSet.as_view(),name='login'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    path('profile/',UserProfileView.as_view(),name="profile"),
    path('post-recipe/',RecipePostView.as_view(),name="Post-Recipe"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path("api/post-recipe-steps",RecipeStepViewSet.as_view(),name="post-recipe-steps"),
   
]


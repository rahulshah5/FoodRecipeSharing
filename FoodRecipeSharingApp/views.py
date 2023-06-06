
from rest_framework import viewsets
from FoodRecipeSharingApp.models import Recipe, Category,Rating,Review,Favourite
from FoodRecipeSharingApp.serializers import *
from django.contrib.auth.models import User
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

class RecipeViewset(viewsets.ModelViewSet):
    queryset=Recipe.objects.all()
    serializer_class=RecipeSerializer

class CategoryViewset(viewsets.ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer


class RatingViewset(viewsets.ModelViewSet):
    queryset=Rating.objects.all()
    serializer_class=RatingSerializer

class ReviewViewset(viewsets.ModelViewSet):
    queryset=Review.objects.all()
    serializer_class=ReviewSerializer


class FavouriteViewset(viewsets.ModelViewSet):
    queryset=Favourite.objects.all()
    serializer_class=FavouriteSerializer

class RecipeStepViewSet(viewsets.ModelViewSet):
    queryset=RecipeStep.objects.all()
    serializer_class=RecipeStepSerializer


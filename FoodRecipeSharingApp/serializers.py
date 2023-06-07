from rest_framework import serializers
from FoodRecipeSharingApp.models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("username",)

class RecipeStepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=RecipeStep
        fields="__all__"

class RecipeImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=RecipeImage
        fields=('image',)

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    recipeImage=RecipeImageSerializer()
    class Meta:
        model=Recipe
        fields=('title','author','category','ingredients','cooking_time','difficulty_level','tags','recipeImage')




class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class RatingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Rating
        fields="__all__"

class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Review
        fields="__all__"

class FavouriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Favourite
        fields="__all__"


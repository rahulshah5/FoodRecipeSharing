from rest_framework import serializers
from FoodRecipeSharingApp.models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=User
        fields=['full_name','email','gender','password','password2']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        pass1=attrs.get('password')
        pass2=attrs.get('password2')
        if pass1 != pass2:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        return attrs
    
    def create(self,validate_data):
        return User.objects.create_user(**validate_data)
    


class UserLoginSerializer(serializers.HyperlinkedModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=User
        fields=["email",'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','full_name','gender']

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


from rest_framework import serializers
from FoodRecipeSharingApp.models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=User
        fields=['full_name','email','gender','password','password2','country']
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

class RecipeSerializer(serializers.ModelSerializer):
    recipeImage=RecipeImageSerializer()
    
    class Meta:
        model=Recipe
        fields=('title','author','category','ingredients','cooking_time','difficulty_level','tags','recipeImage','description')

    def validate(self, attrs):
        title=attrs.get('title')
        difficultyLevel=attrs.get('difficulty_level')
        recipeImg=attrs.get('recipeImage')
        category=attrs.get('category')
        ingredients=attrs.get('ingredients')
        description=attrs.get('description')

        if title is None:
            return serializers.ValidationError("Recipe Title is required")
        elif difficultyLevel is None: 
            return serializers.ValidationError("Difficulty level is required")
        elif recipeImg is None:
            return serializers.ValidationError("Recipe Image is required")
        elif category is None:
            return serializers.ValidationError("Category is required")
        elif ingredients is None:
            return serializers.ValidationError("Ingredients is required")
        elif description is None:
            return serializers.ValidationError("Description is required")

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class RatingSerializer(serializers.ModelSerializer):
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
        exclude=['user']
        

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ingredient
        fields="__all__"

    def validate(self, attrs):
        name=attrs.get('name')
        filterName=Ingredient.objects.filter(name);
        if filterName is not None:
            return serializers.ValidationError("Ingredient already exists");


        
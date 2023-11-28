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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","full_name","email","country","gender","created_at"]

class RecipeStepSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecipeStep
        fields="__all__"

class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecipeImage
        fields="__all__"

class RecipeSerializer(serializers.ModelSerializer):
    
    ingredient_names = serializers.SerializerMethodField()
    tags_name=serializers.SerializerMethodField()
    author_name=serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category_name=serializers.SerializerMethodField()
    
    class Meta:
        model=Recipe
        fields=["id","title","category","category_name","tags","ingredients","ingredient_names","cooking_time","description","servings","difficulty_level","author","tags_name","author_name","average_rating","image","image_url"]

    
    
    def get_category_name(self,obj):
        return obj.category.name
    def get_image_url(self, obj):
        if 'request' in self.context:
            return self.context['request'].build_absolute_uri(obj.image.image.url) 
        return None
    def get_tags_name(self,obj):
        return [tags.name for tags in obj.tags.all()]

    def get_ingredient_names(self, obj):
        return [ingredient.name for ingredient in obj.ingredients.all()]

    def get_author_name(self, obj):
        return obj.author.full_name
    

    


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class RatingSerializer(serializers.ModelSerializer):
    author_name=serializers.SerializerMethodField()
    class Meta:
        model=Rating
        fields=['recipe','user','author_name','rating']
    
    def get_author_name(self, obj):
        return obj.user.full_name

class ReviewSerializer(serializers.ModelSerializer):
    author_name=serializers.SerializerMethodField()
    created_at_date = serializers.SerializerMethodField()
    class Meta:
        model=Review
        fields=['recipe','user','author_name','content','created_at_date']
    
    def get_author_name(self, obj):
        return obj.user.full_name
    
    def get_created_at_date(self, obj):
        return obj.created_at.date()
    
   

class FavouriteSerializer(serializers.ModelSerializer):
    author_name=serializers.SerializerMethodField()
    recipe_title=serializers.SerializerMethodField()
    recipe_ingredients=serializers.SerializerMethodField()
    recipe_image_url=serializers.SerializerMethodField()
    recipe_cooking_time=serializers.SerializerMethodField()
    class Meta:
        model=Favourite
        fields=['id','recipe','author_name','recipe_title','recipe_cooking_time','recipe_ingredients','recipe_image_url']  
    def get_author_name(self, obj):
        return obj.recipe.author.full_name
    def get_recipe_title(self,obj):
        return obj.recipe.title
    def get_recipe_ingredients(self,obj):
        return obj.recipe.ingredients.count()
    def get_recipe_cooking_time(self,obj):
        return obj.recipe.cooking_time
    def get_recipe_image_url(self,obj):
        if 'request' in self.context:
            return self.context['request'].build_absolute_uri(obj.recipe.image.image.url) 
        return None
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ingredient
        fields="__all__"

    def validate(self, attrs):
        name=attrs.get('name')
        filterName=Ingredient.objects.filter(name);
        if filterName is not None:
            return serializers.ValidationError("Ingredient already exists");
        
class TagSerializer(serializers.ModelSerializer):
    class meta:
        model=Tag
        fields="__all__"


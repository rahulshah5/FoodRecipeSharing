
from rest_framework import viewsets,status,generics
from rest_framework.generics import ListAPIView
from FoodRecipeSharingApp.serializers import *
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework_simplejwt.tokens import RefreshToken
from FoodRecipeSharingApp.renderers import UserRenderer
from django.db.models import Q
from FoodRecipeSharingApp.models import *
from rest_framework.parsers import MultiPartParser
from django.http import QueryDict
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django.db.models import Avg
from .collaborative_filtering_algorithm import get_recommended_recipes
from django.db.models import F

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegisterViewSet(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user=serializer.save()
            token=get_tokens_for_user(user)
            return Response({'msg':'User succesfully registered!','token':token},status=status.HTTP_200_OK)
        return Response(serializers.errors)
    
    @permission_classes([IsAuthenticated])
    @authentication_classes([TokenAuthentication])
    def patch(self, request):
        # Get the current user
        user = request.user  # Assuming the user is authenticated

        # Use UserRegisterSerializer with instance=user to update the user details
        serializer = UserRegisterSerializer(instance=user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'User details updated successfully!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginViewSet(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request):
        serializers=UserLoginSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            email=serializers.data.get('email')
            password=serializers.data.get('password')
            user=authenticate(email=email,password=password)
            if user is not None:
                print(user)
                token=get_tokens_for_user(user)
                return Response({'msg':'login success','token':token},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':'email or password is not valid'}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    renderer_classes=[UserRenderer]
    
 
    def post(self, request):
        # Get the refresh token from the request headers
        refresh_token = request.headers.get('AUTHORIZATION').split(' ')[1]
        print('token')
        print(refresh_token)
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'msg':'Logged out successfully!'},status=status.HTTP_200_OK)
        else:
            return Response({'msg':"token unidentified"},status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = request.data['old_password']
            new_password = request.data['new_password']

            # Check if the old password matches
            if not user.check_password(old_password):
                return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        serializers=UserProfileSerializer(request.user)
        userid=request.user.id
        user_recipe=Recipe.objects.filter(author=userid)
        ud=RecipeSerializer(user_recipe,many=True)
        
        res={
            'user':serializers.data,
            'recipes':ud.data
        }
        return Response(res,status=status.HTTP_200_OK)
      
# ALL RECIPES
class RecipeViewset(viewsets.ModelViewSet):
    allowed_methods = ['get','delete']
    serializer_class = RecipeSerializer
    filter_backends = [SearchFilter]
    search_fields = ['category__id']  # Define the field for filtering
    
    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')  # Get the category ID from query parameters
        queryset = Recipe.objects.all()

        if category_id:
            queryset = queryset.filter(category__id=category_id)  # Filter recipes by category ID
        
        return queryset
    
    # @authentication_classes([TokenAuthentication])
    # @permission_classes([IsAuthenticated])
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
        
    #     # Check permissions here if needed
    #     if not self.request.user.is_authenticated or self.request.user != instance.author:
    #         return Response({"error": "You do not have permission to delete this recipe."},
    #                         status=status.HTTP_403_FORBIDDEN)
    #     print(instance)
    #     self.perform_destroy(instance)
    #     return Response({"msg": "Recipe deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# POST RECIPES
class RecipePostView(APIView):
    allowed_methods=['post','patch']
    renderer_classes=[UserRenderer]
    parser_classes=(MultiPartParser,)

    @authentication_classes([TokenAuthentication])
    @permission_classes([IsAuthenticated])
    def post(self,request):
        userid=request.user.id
        request.data["author"]=userid
        print(request.data)
        qd=request.data
        
        # getting data's of foreign field data
        categoryName=request.data.get('category')
        ingredientName = qd.getlist('ingredients[]')
        tagsName = qd.getlist('tags[]')


        # retriving pk for category
        category_queryset=Category.objects.filter(name=categoryName.lower())
        categoryId=category_queryset.first().pk
        

        # initalizing list for ingredient id and tag id
        ingId=[]
        tagID=[]

        # uppercase
        ingredientName=[x.upper() for x in ingredientName]

        # retriving pk for ingredient and adding it to list
        for ing in ingredientName:          
            qset,created=Ingredient.objects.get_or_create(name=ing)    
            ingId.append(qset.pk)


        # retriving pk for ingredient and adding it to list   
        for tg in tagsName:
            qset,created=Tag.objects.get_or_create(name=tg)
            tagID.append(qset.pk)

        recipe_image = request.data.get('image')
        recipe_image_id = RecipeImage(image=recipe_image)
        recipe_image_id.save()


        initial_values = {
            'title': 'test',
            'description': 'test',
            'author':'0',
            'category': 'dinner',
            'ingredients': ['2', '3'],
            'cooking_time': '34',
            'difficulty_level': 'Easy',
            'tags': ['2', '3'],
            # Include other variables as needed
        }

        # Create new QueryDict 
        data = QueryDict('', mutable=True)
        data.update(initial_values)

        # Update specific values
        data['title'] = request.data.get('title')  
        data['description'] = request.data.get('description')  
        data['cooking_time'] = request.data.get('cooking_time')  
        data['difficulty_level'] = request.data.get('difficulty_level')  
        data['category'] = categoryId  
        data.setlist('tags', tagID)  
        data.setlist('ingredients', ingId)
        data['author']=userid
        data['image']=recipe_image_id.id

        serializer=RecipeSerializer(data=data)

        # validation 
        if serializer.is_valid():
            data=serializer.save()
            data=serializer.data
            return Response({'msg':'Recipe Succesfully posted',"data":data},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
          
# VIEW CATEGORY
class CategoryViewset(viewsets.ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

# VIEW AND POST RATING
class RatingViewset(viewsets.ModelViewSet):
    serializer_class = RatingSerializer

    def get_queryset(self):
        user_country = self.request.query_params.get('country')
        recipe_id = self.request.query_params.get('recipe')
        
        if user_country == "ALL":
            queryset = Rating.objects.filter(recipe=recipe_id)
        else:
            queryset = Rating.objects.all().filter(recipe_id=recipe_id, user__country=user_country)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        recipe_id = self.request.query_params.get('recipe')

        # Calculate average rating for the recipe
        avg_rating = queryset.aggregate(Avg('rating'))['rating__avg']
        
        # Serialize queryset
        serializer = self.get_serializer(queryset, many=True)
        
        # Create response data
        response_data = {
            'ratings': serializer.data,
            'average_rating': avg_rating if avg_rating else 0.0,  # Set to 0 if no ratings found
        }

        return Response(response_data)
    
    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
    
        serializer=RatingSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        country=request.data['country']
        request.data['country']=country.upper()
        if serializer.is_valid():
            instance=serializer.save()
            recipe_instance = Recipe.objects.get(id=request.data['recipe'])
            recipe_instance.update_average_rating()

            return Response({'msg':'created',"data":RatingSerializer(instance).data},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)

# VIEW AND POST REVIEW
class ReviewViewset(viewsets.ModelViewSet):
    
    serializer_class=ReviewSerializer

    def get_queryset(self):
         #  /api/reveiw/?recipe=<recipe_id>
        user_country = self.request.query_params.get('country')
        recipe_id = self.request.query_params.get('recipe')
        if user_country=="ALL":
            queryset= Review.objects.filter(recipe=recipe_id)
        else:
            queryset=Review.objects.all().filter(recipe=recipe_id,user__country=user_country)
        return queryset


    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
        serializer=ReviewSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        if serializer.is_valid():
            instance=serializer.save()
            return Response({'msg':'created',"data":ReviewSerializer(instance).data},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)

# VIEW AND POST FAVOURITE

class FavouriteViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FavouriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favourite.objects.filter(user=user)


    def create(self, request, *args, **kwargs):
        serializer = FavouriteSerializer(data=request.data)
        userid = request.user.id
        recipe_id = request.data.get('recipe')
        request.data['user']=userid
        existing_favorite = Favourite.objects.filter(user=userid, recipe_id=recipe_id).first()

        if existing_favorite:
            return Response({"msg": "This recipe is already in your favorites."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Added to favorites"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeStepViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeStepSerializer

    def get_queryset(self):
        recipe_id = self.request.query_params.get("recipe")
        return RecipeStep.objects.filter(recipe_name=recipe_id)

    def create(self, request, *args, **kwargs):
        data = request.data.get('items', request.data)
        many = isinstance(data, list)
        userId=self.request.user
       
        for i in data:
            recipe_name=i.get("recipe_name")
            recipe=Recipe.objects.get(id=recipe_name)
        
            if recipe.author!=userId:
                return Response({"error":"you are not allowed"})

        
        serializer = self.get_serializer(data=data, many=many)
        if serializer.is_valid():
            serializer.save()
            # Serialize the data and return it as JSON
            serialized_data = serializer.data
            return Response({"msg": "added all", "data": serialized_data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecipeImageViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeImageSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        recipe_id = self.request.query_params.get('recipe')
        try:
            obj = RecipeImage.objects.get(recipe_id=recipe_id)
            return [obj]
        except RecipeImage.DoesNotExist:
            return []

    def create(self, request, *args, **kwargs):
        serializer = RecipeImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Image added"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # Get the existing image instance
        instance = self.get_object()
        
        # Update the instance's data with the request data
        serializer = RecipeImageSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Image updated", "data": serializer.data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchViewSet(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        query = self.request.data.get('query', '')  
        if not isinstance(query, list):
            query = [query]
        print(query)
        # Use icontains to perform case-insensitive substring matching
        object_list = list(set(Recipe.objects.filter(Q(title__icontains=query[0]) | Q(tags__name__icontains=query[0]) | Q(ingredients__name__icontains=query[0])).order_by('-id')))
        
        return object_list

class RecipeListByCategory(ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        category_name = self.kwargs.get('category_name')
        return Recipe.objects.filter(category_name=category_name)
    
class RecommendationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def list(self, request):
        user_id = request.user.id
        recommended_recipes = get_recommended_recipes(user_id)

        serialized_recipes = self.get_serializer(recommended_recipes, many=True)
        return Response(serialized_recipes.data, status=status.HTTP_200_OK)


class HighRatedRecipes(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    allowed_methods = ['get']

    def get_queryset(self):
        country = self.request.query_params.get('country')
        
        if country!="all":
            country = country.upper()
            users = User.objects.filter(country=country)
            ratings = Rating.objects.filter(user__in=users)
            recipes_with_avg_ratings = (
                Recipe.objects.filter(id__in=ratings.values_list('recipe', flat=True))
                .annotate(avg_rating=Avg('rating__rating'))
                .order_by('-avg_rating')[:2]
            )
            if recipes_with_avg_ratings.exists() :
                return recipes_with_avg_ratings
            else:
                return Recipe.objects.all().order_by('-average_rating')[:2]
        else:
            return Recipe.objects.all().order_by('-average_rating')[:2]


class SimilarRecipes(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    allowed_methods = ['get']

    def get_queryset(self):
        recipe_id = self.request.query_params.get('recipe_id')
        ingredients = Recipe.objects.filter(id=recipe_id).values_list('ingredients__name', flat=True)
        similar_recipes = Recipe.objects.filter(ingredients__name__in=ingredients).exclude(id=recipe_id).distinct()
        return similar_recipes

            
            

from rest_framework import viewsets,status,generics
from FoodRecipeSharingApp.models import Recipe, Category,Rating,Review,Favourite
from FoodRecipeSharingApp.serializers import *
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from FoodRecipeSharingApp.renderers import UserRenderer
from django.db.models import Q


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
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


class UserLoginViewSet(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request):
        serializers=UserLoginSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            email=serializers.data.get('email')
            password=serializers.data.get('password')
            user=authenticate(email=email,password=password)
            if user is not None:
                token=get_tokens_for_user(user)
                return Response({'msg':'login success','token':token},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':'email or password is not valid'}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    renderer_classes=[UserRenderer]
    
    def post(self, request):
        # Get the refresh token from the request headers
        refresh_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        print('token')
        print(refresh_token)
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'msg':'Logged out successfully!'},status=status.HTTP_200_OK)
        else:
            return Response({'msg':"token unidentified"},status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        serializers=UserProfileSerializer(request.user)
        return Response(serializers.data,status=status.HTTP_200_OK)
      
# ALL RECIPES
class RecipeViewset(viewsets.ModelViewSet):
    allowed_methods=['get']
    queryset=Recipe.objects.all()
    serializer_class=RecipeSerializer

# POST RECIPES
class RecipePostView(APIView):
    allowed_methods=['post','patch']
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]


    def post(self,request):
        userid=request.user.id
        serializer=RecipeSerializer(data=request.data)
        request.data["author"]=userid

        # getting data's of foreign field data
        categoryName=request.data['category']
        ingredientName=request.data['ingredients']
        tagsName=request.data['tags']

        # retriving pk for category
        category_queryset=Category.objects.filter(name=categoryName.lower())
        categoryId=category_queryset.first().pk
        

        # initalizing list for ingredient id and tag id
        ingId=[]
        tagID=[]

        # uppercase
        ingredientName=[x.upper() for x in ingredientName]
        print(ingredientName)

        # retriving pk for ingredient and adding it to list
        for ing in ingredientName:          
            qset,created=Ingredient.objects.get_or_create(name=ing)    
            ingId.append(qset.pk)
           
                

        print(ingId)

        # retriving pk for ingredient and adding it to list   
        for tg in tagsName:
            qset,created=Tag.objects.get_or_create(name=tg)
            tagID.append(qset.pk)

        
        print(tagID)

        # setting id's for serializer
        request.data['tags']=tagID
        request.data['category']=categoryId
        request.data['ingredients']=ingId



        # validation 
        if serializer.is_valid():
            data=serializer.save()
            return Response({'msg':'Recipe Succesfully posted',"data":RecipeSerializer(data).data},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
          
# VIEW CATEGORY
class CategoryViewset(viewsets.ReadOnlyModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

# VIEW AND POST RATING
class RatingViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=RatingSerializer

    def get_queryset(self):
        #  /api/ratings/?recipe=<recipe_id>
        recipe_id = self.request.query_params.get('recipe')
        queryset = Rating.objects.filter(recipe_id=recipe_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return Response({"error":"user is not authenticated"})

        serializer=RatingSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        if serializer.is_valid():
            instance=serializer.save()
            return Response({'msg':'created',"data":RatingSerializer(instance).data},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)

# VIEW AND POST REVIEW
class ReviewViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReviewSerializer

    def get_queryset(self):
         #  /api/reveiw/?recipe=<recipe_id>
        recipe_id=self.request.query_params.get('recipe')
        queryset=Review.objects.filter(recipe=recipe_id)
        return queryset

    
    def create(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return Response({'error':"user is not authenticated"})
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
    permission_classes=[IsAuthenticated]
    serializer_class=FavouriteSerializer

    def get_queryset(self):
        user=self.request.user
        query=Favourite.objects.filter(user=user)
        return query
    
    
    def create(self, request, *args, **kwargs):
        serializer=FavouriteSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"Added to favourite"})
        else:
            return Response(serializer.errors)


class RecipeStepViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = RecipeStep.objects.all()
    serializer_class = RecipeStepSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get('items', request.data)
        many = isinstance(data, list)
        userId=self.request.user
       
        for i in data:
            r=i.get("recipe_name")
            recipe=Recipe.objects.get(id=r)
        
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

        # Use icontains to perform case-insensitive substring matching
        object_list = list(set(Recipe.objects.filter(Q(title__icontains=query[0]) | Q(tags__name__icontains=query[0]) | Q(ingredients__name__icontains=query[0])).order_by('-id')))
        
        return object_list

    

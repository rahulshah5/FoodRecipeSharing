
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
      
    
class RecipeViewset(viewsets.ModelViewSet):
    allowed_methods=['get']
    queryset=Recipe.objects.all()
    serializer_class=RecipeSerializer


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
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg':'Recipe Succesfully posted'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
          

class CategoryViewset(viewsets.ReadOnlyModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer


class RatingViewset(viewsets.ModelViewSet):
    queryset=Rating.objects.all()
    serializer_class=RatingSerializer

    @permission_classes([permissions.IsAuthenticated])
    def create(self, request, *args, **kwargs):
        serializer=RatingSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'created'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)


class ReviewViewset(viewsets.ModelViewSet):
    queryset=Review.objects.all()
    serializer_class=ReviewSerializer


    @permission_classes([permissions.IsAuthenticated])
    def create(self, request, *args, **kwargs):
        serializer=ReviewSerializer(data=request.data)
        user=request.user.id
        request.data['user']=user
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'created'},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)


class FavouriteViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        user=self.request.user
        query=Favourite.objects.filter(user=user)
        return query
    
    serializer_class=FavouriteSerializer


class RecipeStepViewSet(viewsets.ModelViewSet):
    queryset=RecipeStep.objects.all()
    serializer_class=RecipeStepSerializer

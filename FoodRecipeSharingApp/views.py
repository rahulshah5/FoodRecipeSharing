
from rest_framework import viewsets,status,generics
from FoodRecipeSharingApp.models import Recipe, Category,Rating,Review,Favourite
from FoodRecipeSharingApp.serializers import *
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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
    queryset=Recipe.objects.all()
    serializer_class=RecipeSerializer
    # def create(self, request, *args, **kwargs):
    #     serializers=self.get_serializer(data=request.data)
    #     if serializers.is_valid():
    #         serializers.save()
    #         return Response({'msg':'Recipe Posted succesfully'},status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializers.error,status=status.HTTP_400_BAD_REQUEST)



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

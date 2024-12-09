from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from  . models import *

class auto_register_login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if the user already exists
        user = CustomUser.objects.get(username=username, password=password)
        if user is not None:
            # Generate the JWT token for the user
            refresh = RefreshToken.for_user(user)
            # Return tokens in the JSON response
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=200)
        else:
            # Automatically register the user
            user = CustomUser.objects.create(username=username, password=password)
            user.save()
            # Generate the JWT token for the new user
            refresh = RefreshToken.for_user(user)
            # Return tokens in the JSON response
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=200)
    
       

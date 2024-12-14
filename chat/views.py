from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from  . models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import *

class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Validate inputs
        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username or email already exists
        if CustomUser.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = CustomUser(username=username, email=email)
        user.set_password(password)  # Hash the password
        user.save()

        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.exclude(id=request.user.id).exclude(is_superuser=True)
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture":user.profile_picture if user.profile_picture else None
            }
            for user in users
        ]
        return Response(user_data)
    



class FollowRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        to_user = CustomUser.objects.get(id=to_user_id)
        if FollowRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({"error": "Follow request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        follow_request = FollowRequest.objects.create(from_user=request.user, to_user=to_user)
        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, follow_request_id):
        follow_request = FollowRequest.objects.get(id=follow_request_id, to_user=request.user)
        status_choice = request.data.get("status")
        if status_choice not in ["accepted", "rejected"]:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        follow_request.status = status_choice
        follow_request.save()

        if status_choice == "accepted":
            # Add to followers
            Follower.objects.create(user=request.user, follower=follow_request.from_user)

        return Response({"message": f"Follow request {status_choice}."}, status=status.HTTP_200_OK)
    

    
class FollowersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        followers = user.followers.all()
        data = [
            {
                "id": follower.follower.id,
                "username": follower.follower.username
            } 
            for follower in followers
            ]
        return Response(data)

class FollowingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        following = user.following.all()
        data = [
            {
                "id": follow.user.id, 
                "username": follow.user.username
            } 
            for follow in following
            ]
        return Response(data)

    

class PostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        posts = Post.objects.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       


class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       
    
       

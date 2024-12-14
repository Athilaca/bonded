from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListAPIView.as_view(), name="user_list"),
    path('follow-request/<int:to_user_id>/', FollowRequestAPIView.as_view(), name="follow_request"),
    path('follow-request/<int:follow_request_id>/', FollowRequestAPIView.as_view(), name="update_follow_request"),
    path('followers/<int:user_id>/', FollowersAPIView.as_view(), name="followers"),
    path('following/<int:user_id>/', FollowingAPIView.as_view(), name="following"),
    path("posts/", PostAPIView.as_view(), name="post_list_create"),
    path("posts/<int:post_id>/comments/", CommentAPIView.as_view(), name="add_comment"),
   

]

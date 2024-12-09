from django.urls import path
from .views import *

urlpatterns = [
    path('', auto_register_login.as_view(), name='login'),  # Login URL
   

]

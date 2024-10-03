from django.urls import path
from .views import process_usernames, home, index

urlpatterns = [
    path('home/', home, name='home'),  # Home Page
    path('process/', process_usernames, name='process_usernames'),  # Process page
    path('', index, name='index'),  # Base URL points to the home page
]
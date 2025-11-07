from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),          # ✅ this is the home
    path('news/', views.home, name='news_home') # optional: your search results
]

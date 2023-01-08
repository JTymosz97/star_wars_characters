from django.urls import path
from characters_explorer import views


urlpatterns = [
    path('', views.index, name='home'),
]
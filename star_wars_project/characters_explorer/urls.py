from django.urls import path
from characters_explorer import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('collections', views.Collections.as_view(), name='collections'),
    path('collections/<int:pk>/<int:load_num>', views.CollectionDetails.as_view(),
         name='collection_details')
]

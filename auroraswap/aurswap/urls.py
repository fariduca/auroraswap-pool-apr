from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('apr/', views.getPoolAPR, name='get_apr')
]
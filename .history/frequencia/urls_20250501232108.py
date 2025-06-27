from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [
    path('', views.index, name='index'),
    # Outras URLs...
]

﻿from django.urls import path
from . import views

app_name = 'professores'

urlpatterns = [
    path('', views.ProfessorListView.as_view(), name='professor_list'),
    path('novo/', views.ProfessorCreateView.as_view(), name='professor_create'),
    path('<int:pk>/', views.ProfessorDetailView.as_view(), name='professor_detail'),
    path('<int:pk>/editar/', views.ProfessorUpdateView.as_view(), name='professor_update'),
    path('<int:pk>/excluir/', views.ProfessorDeleteView.as_view(), name='professor_delete'),
]

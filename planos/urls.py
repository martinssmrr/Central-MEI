from django.urls import path
from . import views

app_name = 'planos'

urlpatterns = [
    path('', views.PlanoListView.as_view(), name='lista'),
]
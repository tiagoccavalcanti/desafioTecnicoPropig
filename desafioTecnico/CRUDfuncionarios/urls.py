from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path('', views.get_funcionarios, name='get_all_funcionarios'),
    path('gestao/', views.funcionario_manager, name='gestao_funcionarios'),
    path('<int:id>/', views.funcionario_by_id, name='funcionario_by_id'),
    path('login/', views.login, name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('manage/', views.user_management, name='user_management'),
    path('role-test/', views.role_test, name='role_test'),
    path('profils/', views.profils_list, name='profils_list'),
    path('profils/<int:pk>/modifier/', views.profil_update, name='profil_update'),
    path('profils/ajouter/', views.profil_create, name='profil_create'),
]

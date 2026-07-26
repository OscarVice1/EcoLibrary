from django.urls import path
from . import views

urlpatterns = [
    path("registro/", views.register_view, name="register"),
    path("iniciar-sesion/", views.login_view, name="login"),
    path("cerrar-sesion/", views.logout_view, name="logout"),
]

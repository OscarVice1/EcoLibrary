from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet

router = DefaultRouter()
router.register(r"libros", BookViewSet)


urlpatterns = [
    path("", views.home, name="home"),
    path("detalles/<int:book_id>/", views.book_detail, name="details"),
    path(
        "agregar-favorito/<int:book_id>/favorito/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path(
        "mis-libros-favoritos", views.favorites_books_view, name="favorites_books_view"
    ),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]

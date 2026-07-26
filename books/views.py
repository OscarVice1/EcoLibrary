from django.shortcuts import render, get_object_or_404, redirect
from typing import Set, List, Type
from .models import Book, Favorite
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from .utils import get_book_data_from_api


from rest_framework import viewsets, permissions
from .serializers import BookSerializer


# Create your views here.
def _favorites_books(user: User) -> Set[int | None]:
    """
        Search the favorites book of the current user.
    Args:
        user (User): The user in the current sesion.

    Returns:
        Set[int | NONE]: id's of the favorites book of the current user or none.
    """
    favorites_id: Set[int | None] = set()
    if user.is_authenticated:
        favorites_id = set(
            Favorite.objects.filter(user=user).values_list("book_id", flat=True)
        )

    return favorites_id


def home(request: HttpRequest) -> HttpResponse:
    """
    Render the home page with a list of all books.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the 'books/home.html' template with the
        context containing the list of books ordered by creation date.
    """
    books: QuerySet[Book] = Book.objects.all().order_by("publication_date")
    favorites_id: Set[int] = _favorites_books(request.user)
    context = {"books": books, "favorites_id": favorites_id}
    return render(request, "books/home.html", context)


def book_detail(request: HttpRequest, book_id: int) -> HttpResponse:
    """
    Render the detail page for a specific book.

    Args:
        request (HttpRequest): The incoming HTTP request.
        book_id (int): The primary key (ID) of the book to retrieve.

    Returns:
        HttpResponse: Renders the 'books/detail.html' template with the
        requested book object. Raises Http404 if the book does not exist.
    """
    book: Book = get_object_or_404(Book, id=book_id)
    external_data = get_book_data_from_api(book.title)

    context = {"book": book, "external_data": external_data}

    return render(request, "books/details.html", context)


@login_required
def toggle_favorite(request: HttpRequest, book_id: int) -> HttpResponse:
    """
    Toggle the current user's book favorite state.

    Args:
        request: The incoming HTTP request.
        book_id: The ID of the book to toggle favorite status.

    Returns:
        Redirect to the previous page or home.
    """

    book: Book = get_object_or_404(Book, id=book_id)

    is_favorite: bool = Favorite.objects.filter(user=request.user, book=book).exists()

    if is_favorite:
        Favorite.objects.filter(user=request.user, book=book).delete()
        messages.info(request, f"'{book.title}' quitado de favoritos")
    else:
        Favorite.objects.create(user=request.user, book=book)
        messages.success(request, f"'{book.title}' agregado a favoritos")

    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def favorites_books_view(request: HttpRequest) -> HttpResponse:
    """
        Render the favorite book page of the current user.
    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the 'books/favorites_book.html' with all the favorites books of user
    """
    favorites_books = Favorite.objects.filter(user=request.user).select_related("book")

    return render(
        request, "books/favorites_books.html", {"favorites_books": favorites_books}
    )


class BookViewSet(viewsets.ModelViewSet):
    """
    API Endpoint that allows books to be viewed or edited.

    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Attributes:
        queryset (QuerySet): The list of all books, ordered by publication date.
        serializer_class (BookSerializer): The serializer class used to convert
                                           Book instances to JSON.
    """

    queryset: QuerySet[Book] = Book.objects.all().order_by("publication_date")
    serializer_class: Type[BookSerializer] = BookSerializer

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Instantiates and returns the list of permissions that this view requires.

        - For 'list' and 'retrieve' actions (GET): Allows access to any user (AllowAny).
        - For 'create', 'update', and 'destroy' actions: Requires the user to be an
          administrator (IsAdminUser).

        Returns:
            List[permissions.BasePermission]: A list of permission instances.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes: List[Type[permissions.BasePermission]] = [
                permissions.AllowAny
            ]
        else:
            permission_classes: List[Type[permissions.BasePermission]] = [
                permissions.IsAdminUser
            ]

        return [permission() for permission in permission_classes]

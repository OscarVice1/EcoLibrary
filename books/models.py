from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint


class Book(models.Model):
    """
    Represents a book in the library catalog.

    Attributes:
        title (str): The title of the book. Must be unique.
        author (str): The author of the book.
        category (str): The category or genre of the book.
        description (str): A short summary or description of the book.
        publication_date (datetime): The date and time when the book was published or added.
        image (ImageField): An optional cover image for the book.
    """

    title = models.CharField(
        max_length=200, verbose_name="Titulo", null=False, blank=False
    )
    author = models.CharField(
        max_length=200, verbose_name="Autor", null=False, blank=False
    )
    category = models.CharField(
        max_length=200, verbose_name="Categoria", null=False, blank=False
    )
    description = models.TextField(
        verbose_name="Descripción breve", null=False, blank=False
    )
    publication_date = models.DateTimeField(auto_created=True, null=False, blank=False)

    image = models.ImageField(
        upload_to="books/",
        null=True,
        blank=True,
        verbose_name="Portada",
    )

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        constraints = [UniqueConstraint(fields=["title"], name="unique_title")]

    def __str__(self) -> str:
        """
        Returns the string representation of the book (its title).
        """
        return self.title


class Favorite(models.Model):
    """
    Represents a relationship between a User and a Book that they have marked as favorite.

    Attributes:
        user (User): The user who marked the book as favorite.
        book (Book): The book marked as favorite.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="favorited_by"
    )

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        constraints = [
            UniqueConstraint(fields=["user", "book"], name="unique_user_book_favorite")
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the favorite relationship.
        Format: "username - book title"
        """
        return f"{self.user.username} - {self.book.title}"

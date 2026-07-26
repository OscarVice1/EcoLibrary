from django.contrib import admin
from .models import Book, Favorite


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "description", "publication_date")
    list_filter = ("title", "author")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "book")
    list_filter = ("user",)

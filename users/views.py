from django.shortcuts import render, redirect
from typing import Any
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


def register_view(request: HttpRequest) -> HttpResponse:
    """
    Register a new user and log them in.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Redirects to the home page on successful registration,
        or renders the registration form with errors if validation fails.
    """

    if request.method == "POST":
        form: CustomUserCreationForm = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            messages.success(request, "Registrado con éxito")
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Errores en el formulario")
    else:
        form = CustomUserCreationForm()

    context: dict[str, Any] = {
        "form": form,
    }
    return render(request, "users/register.html", context)


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Authenticate and log in a user.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Redirects to the home page on successful login,
        or renders the login form with errors if authentication fails.
    """
    if request.method == "POST":
        form: AuthenticationForm = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user: User = form.get_user()
            messages.success(request, "Sesión iniciada")
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    context: dict[str, Any] = {
        "form": form,
    }
    return render(request, "users/login.html", context)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Log out the current user.

    Args:
        request (HttpRequest): The incomming HTTP request
    Returns:
        HttpResponse: Redirect to home page after logout.
    """
    logout(request)
    messages.info(request, "Sesión cerrada")
    return redirect("home")

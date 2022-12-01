from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    """Класс формы регистрации."""

    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    """Класс формы смены пароля."""

    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')

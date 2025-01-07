from django.contrib.auth import login
from django.views.generic import CreateView

from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib import messages

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.request.session.cycle_key()
        messages.success(
            self.request,
            f"Welcome {user.username} you have successfully created an account!Please login to proceed."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        for error in form.errors.get('__all__', []):
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        success_url = reverse_lazy('users:login')
        print(f"Redirecting to: {success_url}")
        return success_url

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        print(f"User logged in: {user}")
        messages.success(self.request, f"Welcome, {user.username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        for error in form.errors.get('__all__', []):
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        success_url = reverse_lazy('projects:start')
        print(f"Redirecting to: {success_url}")
        return success_url


class CustomLogoutView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse_lazy('users:login'))

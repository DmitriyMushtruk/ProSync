import json
from .forms import UserRegistrationForm

from django.views import View
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.request.session.cycle_key()
        messages.success(
            self.request,
            f"Welcome {user.username} you have successfully created an account! \n Please login to proceed."
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


class UserDataUpdateView(View):
    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            if 'avatar-file' in request.FILES:
                user.avatar = request.FILES['avatar-file']
            if 'email' in request.POST:
                user.email = request.POST['email']
            user.save()
            messages.success(request, 'Successfully updated.')
            return JsonResponse({'success': True, 'message': 'Successfully updated.'}, status=200)
        except Exception as e:
            print(f"Error updating user data: {e}")
            messages.error(request, 'Failed to update user data.')
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)


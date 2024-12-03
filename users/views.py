from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print(form.errors)
            return redirect('users:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:home')  # Перенаправление после успешного логина
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

def home_view(request):
    return render(request, 'users/home.html')

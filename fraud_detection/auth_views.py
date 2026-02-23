from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please wait for admin approval.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    if not request.user.is_approved and not request.user.is_staff:
        messages.warning(request, 'Your account is pending approval.')
        return redirect('pending_approval')
    return render(request, 'fraud_detection/dashboard.html')

def pending_approval(request):
    if request.user.is_approved:
        return redirect('dashboard')
    return render(request, 'registration/pending_approval.html')

@user_passes_test(lambda u: u.is_staff)
def user_approval_list(request):
    pending_users = CustomUser.objects.filter(is_approved=False, is_staff=False)
    return render(request, 'admin/user_approval_list.html', {'pending_users': pending_users})

@user_passes_test(lambda u: u.is_staff)
def approve_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.approve()
        messages.success(request, f'User {user.username} has been approved.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('user_approval_list')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')
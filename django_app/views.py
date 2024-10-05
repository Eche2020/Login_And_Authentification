from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from .form import RegisterForm
from .form import ContactForm
from django.contrib.sessions.models import Session
from django.utils import timezone


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')  #redirect users after login into the site
        else:
            form = RegisterForm()
        return render(request, 'accounts/register.html', {'form':form})
    else:
        return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        # if statement checks if the authentification was successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            # check if user with given username exists
            if User.objects.filter(username=username).exists():
                error_message = "invalid password!"
            else:
                error_message = "user does not exists!"
            return render(request, 'accounts/login.html',  {'error':error_message})
    else:
        return render(request, "accounts/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')
    else:
        return redirect('home')
    

# Home view
# using the decorator
@login_required
def home_view(request):
    return render(request, 'auth1_app/home.html')

# protected View
class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login/'
    # 'next' - to redirect URL
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return render(request, 'registration/protected.html')



#Review page view function
def review_view(request):
    return render(request, 'django_app/review.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send_email()
            return redirect('contact-success')
    else:
        form = ContactForm()
    return render(request, 'django_app/contact.html', {'form':form})

#define the contact_success_view function
def contact_success_view(request):
    return render(request, 'django_app/contact_success.html')


# code to give list of users logged in using the sessions module
def get_logged_in_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id:
            user_ids.append(user_id)
    return User.objects.filter(id__in=user_ids)


def logged_in_users_view(request):
    logged_in_users = get_logged_in_users()
    return render(request,  'auth1_app/logged_in_users.html', {'users': logged_in_users})
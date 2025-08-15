from django.contrib import messages
from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import redirect, render


def _render_register_form(request, username='', email='', **kwargs):
    context = {
        'username': username,
        'email': email,
        **kwargs
    }
    return render(request, 'accounts/register.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        terms_agreed = request.POST.get('termsCheck') == 'on'

        storage = messages.get_messages(request)
        storage.used = True


        validation_passed = True
        
        if not terms_agreed:
            messages.error(request, 'You must agree to the terms and conditions')
            validation_passed = False

        if not username or not email or not password:
            messages.error(request, 'All fields are required')
            validation_passed = False

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            validation_passed = False

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            validation_passed = False

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            validation_passed = False

        if not validation_passed:
            return _render_register_form(request, username, email)

        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error during registration: {str(e)}')
            return _render_register_form(request, username, email)

    return _render_register_form(request)

def login(request):
    error = None  
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM auth_user  WHERE username='{username}' AND password='{password}'")
            user = cursor.fetchone()

            if user:
                request.session['user_id'] = user[0]
                request.session['username'] = user[4]
                return redirect('home')
            else:
                error = "Invalid username or password"

    return render(request, 'accounts/login.html', {'error': error})


def listview(request):
    context = {
         
    }
    return render(request, 'listview.html', context)
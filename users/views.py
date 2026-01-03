from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.conf import settings
from .utils import send_brevo_email


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow login without being authenticated
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    else:
        return Response({"error": "Invalid Credentials"}, status=400)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until verified
            user.save()
            username = form.cleaned_data.get('username')
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email_sent = send_brevo_email(
                subject=subject,
                html_content=message,
                to_email=user.email,
            )

            if email_sent:
                messages.success(
                    request,
                    "Check your email to activate your account."
                )
            else:
                messages.error(
                    request,
                    "Account created, but email could not be sent."
                )

            return redirect("login")

    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def activate(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'users/activation_message.html', {'success': True})
    else:
        return render(request, 'users/activation_message.html', {'success': False})


def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            profile = p_form.save(commit=False)
            if p_form.cleaned_data.get('remove_image'):
                if profile.image and profile.image.name != 'default.jpg':
                    profile.image.delete(save=False)
                    profile.image = 'default.jpg'
            p_form.save()
            messages.success(request, f'your profile is updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

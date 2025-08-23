from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .validators import validate_email
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError



class UserRegisterForm(UserCreationForm):
	email = forms.EmailField(validators = [validate_email])

	class Meta:
		model = User
		fields = ['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username','email']

class ProfileUpdateForm(forms.ModelForm):
	remove_image = forms.BooleanField(required=False, label='Remove profile picture')
	
	class Meta:
		model = Profile
		fields = ['image']

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "Your account is inactive. Please check your email to verify your account.",
                code='inactive'
            )
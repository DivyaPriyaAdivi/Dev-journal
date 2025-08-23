from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm
from django.contrib.auth.models import User
# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
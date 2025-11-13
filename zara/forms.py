# zara/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}))

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Contraseña actual", widget=forms.PasswordInput(attrs={"class":"form-control"}))
    new_password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={"class":"form-control"}))
    new_password2 = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput(attrs={"class":"form-control"}))

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Correo institucional", widget=forms.EmailInput(attrs={"class":"form-control"}))

class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={"class":"form-control"}))
    new_password2 = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput(attrs={"class":"form-control"}))

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroForm(UserCreationForm):
    rol = forms.ChoiceField(
        choices=Perfil.Rol.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    nombre_mostrar = forms.CharField(
        max_length=120, required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Cómo quieres que te vean"})
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "rol", "nombre_mostrar")

    def save(self, commit=True):
        user = super().save(commit)
        perfil = user.perfil  # creado por signal
        perfil.rol = self.cleaned_data["rol"]
        perfil.nombre_mostrar = self.cleaned_data.get("nombre_mostrar") or user.username
        if commit:
            perfil.save()
        return user

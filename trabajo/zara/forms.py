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

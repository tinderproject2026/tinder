from django import forms
from .models import Profile

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = [ 'name', 'username', 'password', 'birth_date', 'gender', 'city', 'bio', 'photo', ]
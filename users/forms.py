from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'telephone']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input'}),
        }

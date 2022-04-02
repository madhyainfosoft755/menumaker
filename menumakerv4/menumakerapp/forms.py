from django import forms
from menumakerapp.models import CustomAdmin



class CustomAdminForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs = {'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    cpassword = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}),label = "Confirm Password")
    class Meta:
        model = CustomAdmin
        fields = ['username' ,'password']

 

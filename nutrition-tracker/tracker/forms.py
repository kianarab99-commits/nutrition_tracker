from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Meal, UserProfile, Article

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal_type', 'food_name', 'calories', 'carbohydrates', 'protein', 'fat']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chicken Salad'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'carbohydrates': forms.NumberInput(attrs={'class': 'form-control'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class GoalsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['daily_calorie_goal', 'daily_protein_goal', 'daily_carbs_goal', 'daily_fat_goal']
        widgets = {
            'daily_calorie_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_protein_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_carbs_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_fat_goal': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BMIForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height', 'weight']
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Height in cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Weight in kg'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
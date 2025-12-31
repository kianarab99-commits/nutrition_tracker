from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Meal, UserProfile, Article
from .forms import RegistrationForm, MealForm, GoalsForm, BMIForm, ArticleForm

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Nutrition Tracker.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard view"""
    today = timezone.now().date()
    
    # Get today's meals
    meals_today = Meal.objects.filter(user=request.user, date=today).order_by('meal_type')
    
    # Get today's nutritional summary
    summary = Meal.get_daily_summary(request.user, today)
    
    # Get user profile with goals
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate progress percentages
    progress = {}
    if profile.daily_calorie_goal > 0:
        progress['calories'] = min(100, (summary['total_calories'] / profile.daily_calorie_goal) * 100)
    else:
        progress['calories'] = 0
    
    if profile.daily_protein_goal > 0:
        progress['protein'] = min(100, (summary['total_protein'] / profile.daily_protein_goal) * 100)
    else:
        progress['protein'] = 0
    
    if profile.daily_carbs_goal > 0:
        progress['carbs'] = min(100, (summary['total_carbs'] / profile.daily_carbs_goal) * 100)
    else:
        progress['carbs'] = 0
    
    if profile.daily_fat_goal > 0:
        progress['fat'] = min(100, (summary['total_fat'] / profile.daily_fat_goal) * 100)
    else:
        progress['fat'] = 0
    
    # Generate warning messages
    warnings = []
    if summary['total_calories'] > profile.daily_calorie_goal:
        warnings.append("⚠️ Your calorie intake exceeds your daily limit.")
    elif summary['total_calories'] < profile.daily_calorie_goal * 0.5:
        warnings.append("⚠️ Your calorie intake is very low today.")
    
    if summary['total_protein'] < profile.daily_protein_goal * 0.7:
        warnings.append("⚠️ Your protein intake is lower than recommended.")
    
    if summary['total_carbs'] > profile.daily_carbs_goal:
        warnings.append("⚠️ Your carbohydrate intake exceeds your daily goal.")
    
    # Get last 7 days of data for charts
    week_data = []
    for i in range(6, -1, -1):  # Last 7 days including today
        date = today - timedelta(days=i)
        daily = Meal.get_daily_summary(request.user, date)
        week_data.append({
            'date': date.strftime('%a'),
            'calories': daily['total_calories'],
            'protein': daily['total_protein'],
            'carbs': daily['total_carbs'],
            'fat': daily['total_fat'],
        })
    
    context = {
        'meals_today': meals_today,
        'summary': summary,
        'profile': profile,
        'progress': progress,
        'warnings': warnings,
        'week_data': week_data,
        'today': today,
    }
    
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_meal(request):
    """Add a new meal entry"""
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.user = request.user
            meal.save()
            messages.success(request, 'Meal added successfully!')
            return redirect('dashboard')
    else:
        form = MealForm()
    
    return render(request, 'tracker/add_meal.html', {'form': form})

@login_required
def delete_meal(request, meal_id):
    """Delete a meal entry"""
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    meal.delete()
    messages.success(request, 'Meal deleted successfully!')
    return redirect('dashboard')

@login_required
def goals(request):
    """Set and update daily nutrition goals"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = GoalsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goals updated successfully!')
            return redirect('dashboard')
    else:
        form = GoalsForm(instance=profile)
    
    return render(request, 'tracker/goals.html', {'form': form})

@login_required
def bmi_calculator(request):
    """BMI calculator view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    bmi = None
    category = None
    
    if request.method == 'POST':
        form = BMIForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            
            # Calculate BMI
            bmi = profile.calculate_bmi()
            category = profile.get_bmi_category()
            
            if bmi:
                messages.success(request, f'BMI calculated: {bmi} ({category})')
            return redirect('bmi')
    else:
        form = BMIForm(instance=profile)
        # Calculate current BMI if data exists
        bmi = profile.calculate_bmi()
        category = profile.get_bmi_category()
    
    # BMI interpretation
    interpretation = {
        'Underweight': 'Consider consulting a healthcare provider.',
        'Normal': 'Great! Maintain your healthy weight.',
        'Overweight': 'Consider a balanced diet and exercise.',
        'Obese': 'Consult with a healthcare provider.',
    }
    
    context = {
        'form': form,
        'bmi': bmi,
        'category': category,
        'interpretation': interpretation.get(category, ''),
    }
    
    return render(request, 'tracker/bmi.html', context)

@login_required
def articles(request):
    """Articles/blog section"""
    articles_list = Article.objects.filter(is_published=True).order_by('-created_at')
    
    # Check if user is admin/staff (can create articles)
    can_create = request.user.is_staff
    
    if request.method == 'POST' and can_create:
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article published successfully!')
            return redirect('articles')
    else:
        form = ArticleForm()
    
    context = {
        'articles': articles_list,
        'form': form,
        'can_create': can_create,
    }
    
    return render(request, 'tracker/articles.html', context)
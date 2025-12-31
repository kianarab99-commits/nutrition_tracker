from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class UserProfile(models.Model):
    """Extended user profile for nutrition goals"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Daily goals
    daily_calorie_goal = models.IntegerField(default=2000, validators=[MinValueValidator(0)])
    daily_protein_goal = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    daily_carbs_goal = models.IntegerField(default=300, validators=[MinValueValidator(0)])
    daily_fat_goal = models.IntegerField(default=70, validators=[MinValueValidator(0)])
    
    # BMI data (optional)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def calculate_bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            bmi = self.weight / (height_m ** 2)
            return round(bmi, 1)
        return None
    
    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.calculate_bmi()
        if not bmi:
            return None
        
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class Meal(models.Model):
    """Meal entries for users"""
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    food_name = models.CharField(max_length=200)
    
    # Nutritional values
    calories = models.IntegerField(validators=[MinValueValidator(0)])
    carbohydrates = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Carbs (g)")
    protein = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Protein (g)")
    fat = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Fat (g)")
    
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'meal_type']
    
    def __str__(self):
        return f"{self.meal_type}: {self.food_name} ({self.calories} cal)"
    
    @classmethod
    def get_daily_summary(cls, user, date):
        """Get daily nutritional summary for a user"""
        meals = cls.objects.filter(user=user, date=date)
        
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbohydrates for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        
        return {
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'meal_count': meals.count(),
        }

class Article(models.Model):
    """Nutrition articles for the blog section"""
    CATEGORIES = [
        ('nutrition', 'Nutrition Basics'),
        ('meals', 'Meal Planning'),
        ('healthy', 'Healthy Habits'),
        ('recipes', 'Recipes'),
        ('fitness', 'Fitness & Nutrition'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES, default='nutrition')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Optional image
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def excerpt(self):
        """Get first 150 characters as excerpt"""
        return self.content[:150] + "..." if len(self.content) > 150 else self.content
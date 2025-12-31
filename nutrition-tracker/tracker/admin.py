from django.contrib import admin
from .models import Meal, UserProfile, Article

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'food_name', 'calories', 'date')
    list_filter = ('meal_type', 'date', 'user')
    search_fields = ('food_name', 'user__username')
    ordering = ('-date', 'meal_type')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_calorie_goal', 'daily_protein_goal', 'height', 'weight')
    search_fields = ('user__username', 'user__email')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'is_published')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'title': ('title',)}
from django.contrib import admin
from .models import *

register = admin.site.register


@admin.action(description='Пересохранить')
def save_recipe(modeladmin, request, queryset):
    for recipe in queryset:
        recipe.save()


class ProfileAdmin(admin.ModelAdmin):
    list_display_links = ('user',)
    list_display = ('user', 'avatar')


register(Profile, ProfileAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'preparation_time', 'cooking_time', 'difficulty', 'get_author', 'likes')
    list_display_links = ('title', 'category')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

    def get_author(self, obj):
        return obj.author

    get_author.short_description = 'Автор'


register(Recipe, RecipeAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


register(Category, CategoryAdmin)


class StepAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'step_number')
    list_display_links = ('recipe', 'step_number')
    search_fields = ('recipe', 'step_number')


register(Step, StepAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'kcal', 'p', 'f', 'c')
    list_display_links = ('name',)


register(Product, ProductAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'quantity', 'unit')
    list_display_links = ('recipe',)


register(Ingredient, IngredientAdmin)

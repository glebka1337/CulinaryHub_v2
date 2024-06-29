from django.urls import path
from .views import *
from .htmx_views import *


urlpatterns = [
    path('', RecipeListView.as_view(), name='index'),
    path('recipes/<slug:category_slug>', RecipeListView.as_view(), name='category_recipes'),
    path('users/register/', register,name='register'),
    path('users/login/', login_user, name='login'),
    path('users/logout/', logout_user,name='logout'),
    path('users/profile/', profile,name='profile'),
    path('users/profile/<str:profile_name_slug>', user_profile_view, name='user_profile_view'),
    path('recipes/<slug:category_slug>/<slug:recipe_slug>/', recipe_view, name='recipe_view'),
    path('add_recipe/', RecipeFormView.as_view(), name='add_recipe'),
    path('add_ingredients/', add_ingredients, name='add_ingredients'),
    path('add_steps/', add_steps, name='add_steps'),
    path('add_favorite/', add_favorite, name='add_favorite'),
    path('remove_favorite/', remove_favorite, name='remove_favorite'),
    path('add_subscriber/', add_subscriber, name='add_subscriber'),
    path('remove_subscriber/', remove_subscriber, name='remove_subscriber'),
    path('product_search/', product_search, name='product_search'),
    path('delete_product/', delete_product, name='delete_product'),
    path('calculate_calories/', calculate_calories, name='calculate_calories'),
    path('profile/change_password/', PasswordChangeView.as_view(), name='change_password'),
    path('recipe_search/', recipe_search, name='recipe_search'),
]

htmx_urlpatterns = [
    path('check_username/', check_username, name='check_username'),
    path('validate_password/', validate_password, name='validate_password'),
    path('product_search_htmx', product_search_htmx, name='product_search_htmx'),
    path('get_search/', get_search, name='get_search'),
    path('get_recipe_search/', get_recipe_search, name='get_recipe_search'),
]
urlpatterns += htmx_urlpatterns
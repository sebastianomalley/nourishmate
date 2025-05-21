from django.urls import path
from . import views
from .views import FoodLogUpdateView, FoodLogDeleteView 
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("register/", views.register, name="register"),
    path('', views.home, name='home'),
    path('logs/', views.food_log_list, name='food_log_list'),
    path('add-to-grocery/', views.add_to_grocery_list, name='add_to_grocery_list'),
    path('grocery/', views.grocery_list, name='grocery_list'),
    path('grocery/toggle/<int:item_id>/', views.toggle_purchased, name='toggle_purchased'),
    path('grocery/delete/<int:item_id>/', views.delete_grocery_item, name='delete_grocery_item'),
    path('grocery/update-category/<int:item_id>/', views.update_grocery_category, name='update_grocery_category'),
    path('summary/', views.nutrition_summary, name='nutrition_summary'),
    path('logs/<int:pk>/edit/', FoodLogUpdateView.as_view(), name='food_log_edit'),
    path('logs/<int:pk>/delete/', FoodLogDeleteView.as_view(), name='food_log_delete'),
    path('pantry/', views.pantry_list, name='pantry_list'),
    path('pantry/add/', views.add_pantry_item, name='add_pantry_item'),
    path('pantry/edit/<int:pk>/', views.edit_pantry_item, name='edit_pantry_item'),
    path('pantry/delete/<int:pk>/', views.delete_pantry_item, name='delete_pantry_item'),
    path('pantry/increase/<int:pk>/', views.increase_quantity, name='increase_quantity'),
    path('pantry/decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
    path('toggle-supplement/<str:slot>/', views.toggle_supplement, name='toggle_supplement'),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("api/autocomplete/", views.ingredient_autocomplete, name="ingredient_autocomplete"),
    path("api/nutrition/", views.ingredient_nutrition, name="ingredient_nutrition"),
    path("recipes/save/<int:recipe_id>/", views.save_recipe, name="save_recipe"),
    path("recipes/saved/", views.saved_recipes, name="saved_recipes"),
    path('recipes/saved/delete/<int:recipe_id>/', views.delete_saved_recipe, name='delete_saved_recipe'),
    path('recipes/', views.combined_recipe_view, name='recipe_search'),
]

"""
Django admin configuration.
"""

from django.contrib import admin
from .models import FoodLog, GroceryItem, PantryItem

# Register FoodLog with default admin options
admin.site.register(FoodLog)

@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for GroceryItem.
    Displays key fields and purchase status.
    """
    list_display = (
        'name',
        'quantity',
        'purchased',
        'added_on',
    )

@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for PantryItem.
    Enables filtering by unit and user and search by item name.
    """
    list_display = (
        'name',
        'quantity',
        'unit',
        'user',
        'added_on',
    )
    list_filter = (
        'unit',
        'user',
    )
    search_fields = (
        'name',
    )

"""
Django models for application.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ('fruit', 'Fruit'),
    ('vegetable', 'Vegetable'),
    ('protein', 'Protein'),
    ('grain', 'Grain'),
    ('dairy', 'Dairy'),
    ('fish', 'Fish'),
    ('frozen', 'Frozen'),
    ('dessert', 'Dessert'),
    ('wine', 'Wine'),
    ('other', 'Other'),
]

QUANTITY_UNITS = [
        ('piece', 'Piece(s)'),
        ('slice', 'Slice(s)'),
        ('fruit', 'Fruit'),
        ('g', 'Grams'),
        ('oz', 'Ounces'),
        ('cup', 'Cups'),
        ('serving', 'Serving'),
    ]

class FoodLog(models.Model):
    """
    Log entry for a single food item consumed by a user.
    """
    food_name = models.CharField(max_length=100)
    
    quantity_amount = models.FloatField(null=True, blank=True)
    quantity_unit = models.CharField(max_length=20, choices=QUANTITY_UNITS, blank=True, null=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date_logged = models.DateField(default=timezone.now)

    calories = models.FloatField(default=0.0) # kcal
    protein = models.FloatField(default=0.0)  # grams
    carbs = models.FloatField(default=0.0)    # grams
    sugars = models.FloatField(default=0.0)   # grams
    fiber = models.FloatField(default=0.0)    # grams
    fat = models.FloatField(default=0.0)      # grams
    saturated_fat = models.FloatField(default=0.0)  # grams
    cholesterol = models.FloatField(default=0.0)    # mg
    sodium = models.FloatField(default=0.0)         # mg
    potassium = models.FloatField(default=0.0)      # mg
    calcium = models.FloatField(default=0.0)        # mg
    iron = models.FloatField(default=0.0)           # mg
    vitamin_a = models.FloatField(default=0.0)      # mcg
    vitamin_c = models.FloatField(default=0.0)      # mg
    vitamin_d = models.FloatField(default=0.0)      # mcg
    vitamin_b12 = models.FloatField(default=0.0)    # mcg
    magnesium = models.FloatField(default=0.0)      # mg
    zinc = models.FloatField(default=0.0)           # mg

    def __str__(self):
        return f"{self.food_name} ({self.quantity_amount} {self.quantity_unit}) on {self.date_logged}"


class GroceryItem(models.Model):
    """
    An item a user has added to their grocery shopping list.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    added_on = models.DateTimeField(auto_now_add=True)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

class PantryItem(models.Model):
    """
    A single pantry item for a user.
    Tracks unit, quantity, and when it was added.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.FloatField(default=1)
    unit = models.CharField(max_length=20, choices=[
        ('piece', 'Piece(s)'),
        ('slice', 'Slice(s)'),
        ('fruit', 'Fruit'),
        ('g', 'Grams'),
        ('oz', 'Ounces'),
        ('cup', 'Cups'),
        ('serving', 'Serving'),
        ],
        blank=True,
    )
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
class SupplementLog(models.Model):
    """
    Records when a user takes their supplements (morning, afternoon, and/or evening).
    """
    TIME_SLOTS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_of_day = models.CharField(max_length=10, choices=TIME_SLOTS)

    def __str__(self):
        return f"{self.user.username} - {self.time_of_day} supplement on {self.date}"

class SavedRecipe(models.Model):
    """
    A recipe saved by a user for quick access later.
    Each user can save a particular recipe only once.
    """
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    spoonacular_id = models.CharField(max_length=50)
    title          = models.CharField(max_length=255)
    image_url      = models.URLField()
    source_url     = models.URLField()
    saved_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "spoonacular_id")

    def __str__(self):
        return f"{self.title} (saved by {self.user.username})"
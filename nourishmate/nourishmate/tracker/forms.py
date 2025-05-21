"""
Forms for NourishMate app.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import localdate
from .models import FoodLog, PantryItem
from datetime import date
from django.core.validators import MinValueValidator



class FoodLogForm(forms.ModelForm):
    """
    ModelForm for FoodLog entries.  
    -Makes nutrition fields optional.  
    -Defaults date_logged to today for new entries.  
    -Validates that date_logged is not in the future.
    """
    class Meta:
        model = FoodLog
        fields = [
            'food_name',
            'quantity_amount',
            'quantity_unit',
            'category',
            'date_logged',
            'calories',
            'protein',
            'carbs',
            'sugars',
            'fiber',
            'fat',
            'saturated_fat',
            'cholesterol',
            'sodium',
            'potassium',
            'calcium',
            'iron',
            'vitamin_a',
            'vitamin_c',
            'vitamin_d',
            'vitamin_b12',
            'magnesium',
            'zinc',
        ]
        widgets = {
            'food_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_amount': forms.NumberInput(attrs={
                'placeholder': 'e.g. 1.0',
                'step': '0.1',
                'min': '0',
                'class': 'form-control'
            }),
            'quantity_unit': forms.Select(attrs={'class': 'form-select'}),            
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date_logged': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'calories': forms.NumberInput(attrs={'placeholder': 'e.g. 120 kcal', 'class': 'form-control'}),
            'protein': forms.NumberInput(attrs={'placeholder': 'e.g. 5g', 'class': 'form-control'}),
            'carbs': forms.NumberInput(attrs={'placeholder': 'e.g. 15g', 'class': 'form-control'}),
            'sugars': forms.NumberInput(attrs={'placeholder': 'e.g. 4g', 'class': 'form-control'}),
            'fiber': forms.NumberInput(attrs={'placeholder': 'e.g. 3g', 'class': 'form-control'}),
            'fat': forms.NumberInput(attrs={'placeholder': 'e.g. 8g', 'class': 'form-control'}),
            'saturated_fat': forms.NumberInput(attrs={'placeholder': 'e.g. 2g', 'class': 'form-control'}),
            'cholesterol': forms.NumberInput(attrs={'placeholder': 'e.g. 30mg', 'class': 'form-control'}),
            'sodium': forms.NumberInput(attrs={'placeholder': 'e.g. 200mg', 'class': 'form-control'}),
            'potassium': forms.NumberInput(attrs={'placeholder': 'e.g. 300mg', 'class': 'form-control'}),
            'calcium': forms.NumberInput(attrs={'placeholder': 'e.g. 100mg', 'class': 'form-control'}),
            'iron': forms.NumberInput(attrs={'placeholder': 'e.g. 1.5mg', 'class': 'form-control'}),
            'vitamin_a': forms.NumberInput(attrs={'placeholder': 'e.g. 500mcg', 'class': 'form-control'}),
            'vitamin_c': forms.NumberInput(attrs={'placeholder': 'e.g. 20mg', 'class': 'form-control'}),
            'vitamin_d': forms.NumberInput(attrs={'placeholder': 'e.g. 10mcg', 'class': 'form-control'}),
            'vitamin_b12': forms.NumberInput(attrs={'placeholder': 'e.g. 2.4mcg', 'class': 'form-control'}),
            'magnesium': forms.NumberInput(attrs={'placeholder': 'e.g. 50mg', 'class': 'form-control'}),
            'zinc': forms.NumberInput(attrs={'placeholder': 'e.g. 3mg', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional_fields = [
            'calories', 'protein', 'carbs', 'sugars', 'fiber', 'fat', 'saturated_fat',
            'cholesterol', 'sodium', 'potassium', 'calcium', 'iron',
            'vitamin_a', 'vitamin_c', 'vitamin_d', 'vitamin_b12',
            'magnesium', 'zinc'
        ]
        for field in optional_fields:
            self.fields[field].required = False

        self.fields['quantity_unit'].choices = [('', '--- Select Unit ---')] + list(self.fields['quantity_unit'].choices)

        if not self.instance.pk:
            today = date.today()
            self.initial['date_logged'] = today
            self.fields['date_logged'].widget.attrs.update({
                'value': today.isoformat()
            })


    def clean_date_logged(self):
        """
        Ensure that date_logged is not a future date.
        """
        date = self.cleaned_data.get('date_logged')
        if date and date > localdate():
            raise forms.ValidationError("You can’t log food for a future date.")
        return date
    
    def clean(self):
        """
        Validation for non-negative numbers.
        """
        cleaned_data = super().clean()
        numeric_fields = [
            'quantity_amount', 'calories', 'protein', 'carbs', 'sugars', 'fiber', 
            'fat', 'saturated_fat', 'cholesterol', 'sodium', 'potassium', 'calcium', 
            'iron', 'vitamin_a', 'vitamin_c', 'vitamin_d', 'vitamin_b12', 'magnesium', 'zinc'
        ]
        
        for field in numeric_fields:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                raise ValidationError({field: f"{field.replace('_', ' ').capitalize()} cannot be negative."})
        
        return cleaned_data
    
class PantryItemForm(forms.ModelForm):
    """
    ModelForm for PantryItem entries.
    """
    class Meta:
        model = PantryItem
        fields = ['name', 'quantity', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }
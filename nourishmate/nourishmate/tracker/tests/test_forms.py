"""
Tests for FoodLogForm, focusing on date validation.
Ensures that future dates are rejected and today’s date is accepted.
"""

from datetime import date, timedelta
from django.test import TestCase
from tracker.forms import FoodLogForm

class FoodLogFormTest(TestCase):
    """
    TestCase for validating the FoodLogForm behavior.
    """

    def test_future_date_rejected(self):
        """
        The form should be invalid if `date_logged` is set to a future date.
        """
        tomorrow = date.today() + timedelta(days=1)
        form = FoodLogForm(data={
            'food_name': 'Apple',
            'quantity_amount': 1,
            'quantity_unit': 'piece',
            'category': 'fruit',
            'date_logged': tomorrow.isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn(
            "future date", 
            form.errors['date_logged'][0].lower()
        )

    def test_today_date_accepted(self):
        """
        The form should be valid when `date_logged` is today's date.
        """
        today = date.today().isoformat()
        form = FoodLogForm(data={
            'food_name': 'Banana',
            'quantity_amount': 1,
            'quantity_unit': 'piece',
            'category': 'fruit',
            'date_logged': today,
        })
        self.assertTrue(form.is_valid())

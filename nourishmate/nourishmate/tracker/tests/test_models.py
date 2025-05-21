"""
Tests for the FoodLog model, verifying its string representation.
"""

from django.test import TestCase
from django.utils import timezone
from tracker.models import FoodLog

class FoodLogModelTest(TestCase):
    """
    TestCase for the FoodLog model, ensuring __str__ includes
    the food name and unit.
    """

    def test_str(self):
        """
        The __str__ method should include the food name and unit.
        """
        log = FoodLog.objects.create(
            food_name='Carrot',
            quantity_amount=2,
            quantity_unit='piece',
            category='vegetable',
            date_logged=timezone.localdate()
        )
        string = str(log)
        self.assertIn('Carrot', string)
        self.assertIn('piece', string)

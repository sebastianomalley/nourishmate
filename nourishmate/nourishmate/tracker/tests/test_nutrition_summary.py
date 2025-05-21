"""
Tests for the Nutrition Summary view, verifying calorie totals over different date ranges.
"""

from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localdate
from tracker.models import FoodLog
from .test_views import create_and_login_user

class NutritionSummaryTests(TestCase):
    """
    TestCase for the nutrition_summary view, ensuring that totals
    are calculated correctly for 'today' and custom date ranges.
    """

    def setUp(self):
        """
        Create and log in a test user, then create three days of FoodLog entries
        with varying calorie values.
        """
        self.client, self.user = create_and_login_user(self)
        base = localdate()
        for i, calories in enumerate([100, 200, 300]):
            FoodLog.objects.create(
                food_name=f"Item{i}",
                quantity_amount=1,
                quantity_unit="piece",
                category="other",
                date_logged=base - timedelta(days=i),
                calories=calories
            )

    def test_today_range(self):
        """
        When range = today, only today's log should be in totals.
        """
        url = reverse("nutrition_summary") + "?range=today"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["totals"]["calories"], 100)

    def test_last_3_days_range(self):
        """
        When using a custom range of the last three days, all three logs should be summed.
        """
        start = (localdate() - timedelta(days=2)).isoformat()
        end = localdate().isoformat()
        url = (
            reverse("nutrition_summary")
            + f"?range=custom&start_date={start}&end_date={end}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["totals"]["calories"], 600)

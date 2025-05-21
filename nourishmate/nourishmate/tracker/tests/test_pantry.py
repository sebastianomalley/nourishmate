"""
Tests for the Pantry functionality: adding items and adjusting quantities.
"""

from django.test import TestCase
from django.urls import reverse
from tracker.models import PantryItem
from .test_views import create_and_login_user

class PantryTests(TestCase):
    """
    TestCase for pantry list and quantity adjustment views,
    verifying that items are created for the correct user
    and that quantity increment/decrement works.
    """

    def setUp(self):
        """
        Create and log in a test user before each test.
        """
        self.client, self.user = create_and_login_user(self)

    def test_add_and_list_pantry(self):
        """
        Posting a new pantry item should redirect to the pantry list
        and the item should be associated with the logged-in user.
        """
        response = self.client.post(
            reverse("add_pantry_item"),
            {"name": "Rice", "quantity": 1, "unit": "cup"},
        )
        self.assertRedirects(response, reverse("pantry_list"))
        self.assertTrue(
            PantryItem.objects.filter(name="Rice", user=self.user).exists()
        )

    def test_increase_decrease_quantity(self):
        """
        Posting to increase_quantity should increase the item's quantity by 1,
        and posting to decrease_quantity should decrease it by 1, but not below.
        """
        item = PantryItem.objects.create(
            user=self.user, name="Flour", quantity=1, unit="g"
        )

        # Increase quantity
        resp_inc = self.client.post(reverse("increase_quantity", args=[item.pk]))
        self.assertRedirects(resp_inc, reverse("pantry_list"))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        # Decrease quantity
        resp_dec = self.client.post(reverse("decrease_quantity", args=[item.pk]))
        self.assertRedirects(resp_dec, reverse("pantry_list"))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

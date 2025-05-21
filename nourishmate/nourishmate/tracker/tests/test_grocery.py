"""
Tests for the Grocery List functionality, ensuring items are added
correctly and the user is redirected as expected.
"""

from django.test import TestCase
from django.urls import reverse
from tracker.models import GroceryItem
from .test_views import create_and_login_user

class GroceryListTests(TestCase):
    """
    TestCase for the add_to_grocery_list view, verifying that
    multiple items can be added and redirection works properly.
    """

    def setUp(self):
        """
        Create and log in a test user before each test.
        """
        self.client, _ = create_and_login_user(self)

    def test_add_to_grocery(self):
        """
        Posting multiple grocery items should create them in the database
        and redirect to the URL specified by 'next' without fetching the page.
        """
        data = {
            "food_name": ["Apple", "Banana"],
            "quantity": ["1 piece", "2 pieces"],
            "category": ["fruit", "fruit"],
            "next": "/somewhere/",
        }
        response = self.client.post(reverse("add_to_grocery_list"), data)
        self.assertRedirects(response, "/somewhere/", fetch_redirect_response=False)
        self.assertEqual(GroceryItem.objects.count(), 2)

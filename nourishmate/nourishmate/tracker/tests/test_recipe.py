"""
Tests for the combined recipe search view, covering both general
search mode and smart mode.
"""

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from .test_views import create_and_login_user

# Sample data for mocking API responses
MOCK_SEARCH_LIST = [{"id": 42, "title": "Test Recipe", "image": "url"}]
MOCK_INFO = {"nutrition": {"nutrients": []}}

class RecipeViewTests(TestCase):
    """
    TestCase for the recipe_search view.
    """

    def setUp(self):
        """
        Create and log in a test user before each test.
        """
        self.client, _ = create_and_login_user(self)

    @patch("tracker.views.requests.get")
    def test_general_search(self, mock_get):
        """
        When mode = search and an ingredients query is provided,
        the view should call Spoonacular complexSearch endpoint
        and populate 'results'.
        """
        # Mock the complexSearch API call.
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": MOCK_SEARCH_LIST}

        response = self.client.get(
            reverse("recipe_search") + "?mode=search&ingredients=test"
        )
        self.assertEqual(response.status_code, 200)
        # The first result in context should match mock.
        self.assertEqual(response.context["results"][0]["id"], 42)

    @patch("tracker.views.requests.get")
    def test_smart_mode(self, mock_get):
        """
        When mode = smart, the view should
          -Call findByIngredients...returning a list.
          -Then optionally fetch nutrition info.
          -And include smart_results.
        """
        # First call returns findByIngredients list.
        # Second call returns nutrition info.
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = [MOCK_SEARCH_LIST, MOCK_INFO]

        response = self.client.get(reverse("recipe_search") + "?mode=smart")
        self.assertEqual(response.status_code, 200)
        # Ensure smart_results is present.
        self.assertIn("smart_results", response.context)

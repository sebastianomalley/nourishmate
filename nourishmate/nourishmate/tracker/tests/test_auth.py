"""
Tests to ensure that unauthenticated users are redirected
to the login page when attempting to access protected views.
"""

from django.test import TestCase
from django.urls import reverse

# URLs that require authentication.
PROTECTED = [
    reverse("food_log_list"),
    reverse("nutrition_summary"),
    reverse("pantry_list"),
    reverse("recipe_search"),
]

class AuthRedirectTests(TestCase):
    """
    Verify that each protected URL issues a 302 redirect
    to the login page when accessed without authentication.
    """
    def test_protected_redirects(self):
        for url in PROTECTED:
            response = self.client.get(url)
            # Unauthenticated access should redirect (302).
            self.assertEqual(response.status_code, 302)
            # Direct the user to the login page.
            self.assertIn("/login/", response["Location"])

"""
Tests for the save and delete recipe endpoints, covering both AJAX
and non-AJAX flows.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tracker.models import SavedRecipe

class RecipeSaveDeleteTests(TestCase):
    """
    TestCase for the save_recipe and delete_saved_recipe views.
    """

    def setUp(self):
        """
        Create a test user and log them in for each test.
        """
        self.user = User.objects.create_user(username='bob', password='pass')
        self.client.login(username='bob', password='pass')

    def test_save_recipe_ajax(self):
        """
        POST to save_recipe with the AJAX header.
        """
        url = reverse('save_recipe', args=[12345])
        response = self.client.post(
            url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # AJAX requests should return 200 OK with JSON.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})
        # And the SavedRecipe should have been created.
        self.assertTrue(
            SavedRecipe.objects.filter(
                user=self.user,
                spoonacular_id=12345
            ).exists()
        )

    def test_save_recipe_nonajax(self):
        """
        POST to save_recipe without the AJAX header.
        """
        url = reverse('save_recipe', args=[67890])
        response = self.client.post(url)
        # Non-AJAX should redirect.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('saved_recipes'))
        # And the SavedRecipe should have been created.
        self.assertTrue(
            SavedRecipe.objects.filter(
                user=self.user,
                spoonacular_id=67890
            ).exists()
        )

    def test_delete_saved_recipe(self):
        """
        POST to delete_saved_recipe.
        """
        sr = SavedRecipe.objects.create(
            user=self.user,
            spoonacular_id=111,
            title="Test",
            image_url="",
            source_url=""
        )
        url = reverse('delete_saved_recipe', args=[sr.id])
        response = self.client.post(url)
        # Deletion should redirect back to list.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('saved_recipes'))
        # And the object should no longer exist.
        self.assertFalse(
            SavedRecipe.objects.filter(id=sr.id).exists()
        )

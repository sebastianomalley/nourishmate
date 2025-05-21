"""
Tests for the FoodLog views, covering list display, creation, update, deletion,
and pagination.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from tracker.models import FoodLog

def create_and_login_user(testcase):
    """
    Helper to create a new user on the given TestCase and log them in.
    """
    user = User.objects.create_user("tester", "x@x.com", "pass")
    testcase.client.login(username="tester", password="pass")
    return testcase.client, user

class FoodLogListViewTest(TestCase):
    """
    Tests for the food_log_list view.
    """

    def setUp(self):
        # Create a test user.
        self.user = User.objects.create_user(username='testuser', password='pass')
        # Log that user in.
        self.client.login(username='testuser', password='pass')
        # Create one log to see it show up.
        self.log = FoodLog.objects.create(
            food_name='Egg',
            quantity_amount=1,
            quantity_unit='piece',
            category='protein',
            date_logged=timezone.localdate()
        )

    def test_get_logs_page(self):
        """
        GET on food_log_list should return status 200,
        include the form, and display existing logs.
        """
        response = self.client.get(reverse('food_log_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertContains(response, 'Egg')

    def test_post_creates_new_log_and_redirects(self):
        """
        POST valid data to food_log_list should create a new FoodLog
        and redirect (302) back to the list.
        """
        data = {
            'food_name': 'Toast',
            'quantity_amount': 2,
            'quantity_unit': 'slice',
            'category': 'grain',
            'date_logged': timezone.localdate().isoformat(),
        }
        response = self.client.post(reverse('food_log_list'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FoodLog.objects.count(), 2)

class FoodLogDeleteQuerystringTest(TestCase):
    """
    Tests that deleting a FoodLog preserves the querystring
    in its redirect back to the list.
    """

    def setUp(self):
        # Create/login.
        self.user = User.objects.create_user("deleter", "d@d.com", "pass")
        self.client.login(username="deleter", password="pass")
        # Create a log to delete.
        self.log = FoodLog.objects.create(
            food_name="ToBeDeleted",
            quantity_amount=1,
            quantity_unit="unit",
            category="other",
            date_logged=timezone.localdate()
        )

    def test_delete_redirect_preserves_query(self):
        """
        POSTing to delete URL with a querystring should redirect
        back to the list with the same querystring.
        """
        url = reverse("food_log_delete", args=[self.log.pk]) + "?page=3&sort=calories_asc"
        response = self.client.post(url, follow=False)
        expected = reverse("food_log_list") + "?page=3&sort=calories_asc"
        self.assertRedirects(response, expected)

class FoodLogPaginationLinksTest(TestCase):
    """
    Tests that pagination links in the food_log_list view include
    existing query parameters.
    """

    def setUp(self):
        # Create/login.
        self.user = User.objects.create_user("pager", "p@p.com", "pass")
        self.client.login(username="pager", password="pass")
        # Create 12 logs to require pagination (10 per page).
        today = timezone.localdate()
        for i in range(12):
            FoodLog.objects.create(
                food_name=f"Item {i}",
                quantity_amount=1,
                quantity_unit="unit",
                category="other",
                date_logged=today
            )

    def test_pagination_links_keep_querystring(self):
        """
        GET page 2 with sort and category selected.  Should produce
        pagination links that preserve those.
        """
        resp = self.client.get(
            reverse("food_log_list") + "?page=2&sort=date_asc&category=other"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '?page=1&amp;sort=date_asc&amp;category=other')
        self.assertContains(resp, '?page=2&amp;sort=date_asc&amp;category=other')

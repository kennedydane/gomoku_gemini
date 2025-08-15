from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        """
        Tests that a user can be created with a display_name.
        """
        user = User.objects.create_user(
            username="testuser",
            password="password",
            display_name="Test User",
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.display_name, "Test User")

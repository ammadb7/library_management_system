# tests/test_services/test_auth.py
# Unit tests for AuthService - uses mock to avoid real DB calls

import os
import sys

# Add the project root directory to sys.path to allow imports from 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from unittest.mock import patch, MagicMock
from app.services.auth import AuthService
from app.models.user import User


class TestAuthService(unittest.TestCase):
    """Tests for the AuthService class."""

    def setUp(self):
        """Reset session before each test."""
        AuthService.logout()

    # ── login() ───────────────────────────────────────────────────────────────
    @patch("app.services.auth.UserRepository.find_by_credentials")
    def test_login_success(self, mock_find):
        """Valid credentials should log in and set current user."""
        mock_find.return_value = User(id=1, username="admin", role="admin")

        result = AuthService.login("admin", "admin123")

        self.assertTrue(result)
        self.assertIsNotNone(AuthService.get_current_user())
        self.assertEqual(AuthService.get_current_user().username, "admin")

    @patch("app.services.auth.UserRepository.find_by_credentials")
    def test_login_failure(self, mock_find):
        """Wrong credentials should return False and not set a user."""
        mock_find.return_value = None

        result = AuthService.login("wrong", "wrong")

        self.assertFalse(result)
        self.assertIsNone(AuthService.get_current_user())

    def test_login_empty_username(self):
        """Empty username should fail immediately without DB call."""
        result = AuthService.login("", "password")
        self.assertFalse(result)

    def test_login_empty_password(self):
        """Empty password should fail immediately without DB call."""
        result = AuthService.login("admin", "")
        self.assertFalse(result)

    # ── logout() ──────────────────────────────────────────────────────────────
    @patch("app.services.auth.UserRepository.find_by_credentials")
    def test_logout_clears_session(self, mock_find):
        """Logout should clear the current user."""
        mock_find.return_value = User(id=1, username="admin", role="admin")
        AuthService.login("admin", "admin123")

        AuthService.logout()

        self.assertFalse(AuthService.is_logged_in())
        self.assertIsNone(AuthService.get_current_user())

    # ── is_admin() ────────────────────────────────────────────────────────────
    @patch("app.services.auth.UserRepository.find_by_credentials")
    def test_is_admin_true_for_admin_role(self, mock_find):
        mock_find.return_value = User(id=1, username="admin", role="admin")
        AuthService.login("admin", "pass")
        self.assertTrue(AuthService.is_admin())

    @patch("app.services.auth.UserRepository.find_by_credentials")
    def test_is_admin_false_for_librarian(self, mock_find):
        mock_find.return_value = User(id=2, username="lib", role="librarian")
        AuthService.login("lib", "pass")
        self.assertFalse(AuthService.is_admin())

    def test_is_admin_false_when_not_logged_in(self):
        self.assertFalse(AuthService.is_admin())


class TestUserModel(unittest.TestCase):
    """Tests for the User dataclass."""

    def test_is_admin_returns_true_for_admin(self):
        user = User(id=1, username="admin", role="admin")
        self.assertTrue(user.is_admin())

    def test_is_admin_returns_false_for_librarian(self):
        user = User(id=2, username="lib", role="librarian")
        self.assertFalse(user.is_admin())


if __name__ == "__main__":
    unittest.main()

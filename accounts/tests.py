from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import User


class UserModelTest(TestCase):
    """Database tests for custom User model."""

    def test_create_user_with_defaults(self):
        u = User.objects.create_user(username="testuser", password="pass12345")
        self.assertEqual(u.role, "facility")
        self.assertEqual(u.status, "pending")

    def test_user_roles_work(self):
        u = User.objects.create_user(
            username="admin1",
            password="pass12345",
            role="national_admin",
            status="active",
        )
        self.assertEqual(u.role, "national_admin")
        self.assertEqual(u.status, "active")
        self.assertEqual(u.get_role_display(), "National/System Administrator")

    def test_all_roles_are_valid(self):
        roles = ['facility', 'logistics', 'county_admin', 'national_admin', 'monitoring']
        for i, role in enumerate(roles):
            u = User.objects.create_user(
                username=f"user{i}",
                password="pass12345",
                role=role,
            )
            self.assertEqual(u.role, role)


class SecurityTest(TestCase):
    """Security tests — password hashing, auth protection."""

    def test_password_is_hashed(self):
        u = User.objects.create_user(username="testuser", password="pass12345")
        # Password should NOT be stored in plain text
        self.assertNotEqual(u.password, "pass12345")
        # But should still verify correctly
        self.assertTrue(u.check_password("pass12345"))

    def test_admin_url_requires_login(self):
        client = Client()
        r = client.get('/admin/')
        # Should redirect to login, not return 200
        self.assertNotEqual(r.status_code, 200)

    def test_login_page_loads(self):
        client = Client()
        r = client.get('/admin/login/')
        self.assertEqual(r.status_code, 200)


class RolePermissionTest(TestCase):
    """Test that role assignments affect system state correctly."""

    def test_superuser_created_correctly(self):
        u = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="pass12345",
        )
        self.assertTrue(u.is_superuser)
        self.assertTrue(u.is_staff)

    def test_pending_user_status(self):
        u = User.objects.create_user(username="pending", password="pass12345")
        self.assertEqual(u.status, "pending")

    def test_can_update_user_status(self):
        u = User.objects.create_user(username="testuser", password="pass12345")
        u.status = "active"
        u.save()
        u.refresh_from_db()
        self.assertEqual(u.status, "active")
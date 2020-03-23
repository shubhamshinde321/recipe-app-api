from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):

    def test_create_user(self):
        """Test Creation of user"""
        email = "shubham.shinde@gmailcom"
        password = 'shubham123'

        user = get_user_model().objects.create_user(
                email=email,
                password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Tests normalized email of new user"""
        email = 'shubhma.shinde@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email, 'shubham123')

        self.assertEqual(user.email, email.lower())

    def test_invalid_email(self):
        "test wehter user eneters invalid email raises value error"
        with self.assertRaises(ValueError):
            email = ''
            password = 'shubha123'
            get_user_model().objects.create_user(
                    email, password
            )

    def test_create_new_superuser(self):
        """Test Creating new super user"""
        user = get_user_model().objects.create_super_user(
            'shubham.shinde321@gmail.com',
            "shubham123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

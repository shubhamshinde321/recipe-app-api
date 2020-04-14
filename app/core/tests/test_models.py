from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='shubham.test@gmail.com', password='shubham'):
    """Creates a sample user"""
    return get_user_model().objects.create_user(email, password)


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
        user = get_user_model().objects.create_superuser(
            'shubham.shinde321@gmail.com',
            "shubham123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='test',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Mango',
        )

        self.assertEqual(str(ingredient), ingredient.name)

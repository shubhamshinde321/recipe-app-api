from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    """Test publicly available ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to access this endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test ingredients can be retrieved by authorized user only"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='shubham.test@gmail.com',
            password='shubham',
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Mango')
        Ingredient.objects.create(user=self.user, name='Apple')

        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_user(self):
        """Test api returns ingredient for authenticated user"""
        self.user2 = get_user_model().objects.create(
            email='shubham2.test@gmail.com',
            password='shubham2',
        )
        Ingredient.objects.create(user=self.user2, name='Chikoo')
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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

    def test_create_ingredient_successfully(self):
        """Test ingredients are created successfully"""
        payload = {'name': 'cabbage'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_invalid_ingredient(self):
        """Test for invalid ingredients"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingredient assigend to recipe"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='CoCo Powder'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Red chilly Powder'
        )
        recipe1 = Recipe.objects.create(
            title='Choclate Milkshake',
            time_minutes=4,
            price=2.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_ingredeints_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='coCo Powder',
        )
        Ingredient.objects.create(
            user=self.user,
            name='Chilly Powder'
        )
        recipe1 = Recipe.objects.create(
            title='Demo Recipe 1',
            time_minutes=10,
            price=8.02,
            user=self.user
        )
        recipe1.ingredients.add(ingredient1)
        recipe2 = Recipe.objects.create(
            title='Demo project 2',
            time_minutes=54,
            price=10.23,
            user=self.user
        )
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    """Test the publicliy available tag api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retreiving user"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Test authorized user tag api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='shubham.shinde@gmail.com',
            password='shubham',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tag(self):
        """Test for retrieve tag"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='demo')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test retrieve tag data only for authenticated user"""
        self.user2 = get_user_model().objects.create(
            email='shubham.test@gmail.com',
            password='shubham2',
        )
        Tag.objects.create(user=self.user2, name='mango')
        tag = Tag.objects.create(user=self.user, name='apple')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successfully(self):
        """Test creating a tag"""
        payload = {'name': 'demo_tag'}
        self.client.post(TAGS_URL, payload)

        user_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(user_exists)

    def test_create_tag_invalid(self):
        """Test create invalid tag"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtering tags by those assigned to recipe"""
        tag1 = Tag.objects.create(user=self.user, name='Tikka')
        tag2 = Tag.objects.create(user=self.user, name='Sweet')
        recipe1 = Recipe.objects.create(
            title='Chicken tikka',
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe1.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag1 = Tag.objects.create(user=self.user, name='Choclate')
        Tag.objects.create(user=self.user, name='Salty')
        recipe1 = Recipe.objects.create(
            title='Chicken',
            time_minutes=30,
            price=6.52,
            user=self.user,
        )
        recipe1.tags.add(tag1)
        recipe2 = Recipe.objects.create(
            title='Mutton kebab',
            time_minutes=10,
            price=2.20,
            user=self.user
        )
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

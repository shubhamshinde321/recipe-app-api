from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
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

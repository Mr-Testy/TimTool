from django.test import TestCase
from .models import Bucketlist
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse
from user.models import User

class ModelTestCase(TestCase):
    """This class defines the test suite for the bucketlist model."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="nerd")
        self.bucketlist_name = "Write world class code"
        self.bucketlist = Bucketlist(name=self.bucketlist_name, owner=user)

    def test_model_can_create_a_bucketlist(self):
        """Test the bucketlist model can create a bucketlist."""
        old_count = Bucketlist.objects.count()
        self.bucketlist.save()
        new_count = Bucketlist.objects.count()
        self.assertNotEqual(old_count, new_count)


# Define this after the ModelTestCase
class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""

        userNerd = User.objects.create(username="nerd")
        userLolilol = User.objects.create(username="lolilol")

        # Initialize client and force it to use authentication
        self.client = APIClient()
        self.client.force_authenticate(user=userNerd)
        self.new_client = APIClient()
        self.new_client.force_authenticate(user=userLolilol)
        self.no_client = APIClient()

        # Since user model instance is not serializable, use its Id/PK
        self.bucketlist_data_nerd = {'name': 'Go to Ibiza', 'owner': userNerd.id}
        self.response = self.client.post(
            reverse('create'),
            self.bucketlist_data_nerd,
            format="json")

        self.bucketlist_data_lolilol = {'name': 'Go to Madrid', 'owner': userLolilol.id}
        self.response = self.client.post(
            reverse('create'),
            self.bucketlist_data_lolilol,
            format="json")

        # Retrieve created bucketlist
        self.bucketlists = Bucketlist.objects.all()

    def test_authentication_is_enforced(self):
        """Test that the api has user authentication."""
        response = self.no_client.get(
            reverse('details',
            kwargs={'pk': self.bucketlists.first().pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_create_a_bucketlist(self):
        """Test the api has bucket creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization."""
        response = self.new_client.get(
            reverse('details',
            kwargs={'pk': self.bucketlists.first().pk}), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_get_a_bucketlist(self):
        """Test the api can get a given bucketlist."""
        response = self.client.get(
            reverse('details',
            kwargs={'pk': self.bucketlists.get(name='Go to Ibiza').id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.bucketlists.get(name='Go to Ibiza'))

    def test_api_can_update_bucketlist(self):
        """Test the api can update a given bucketlist."""
        change_bucketlist = {'name': 'Something new'}
        res = self.client.put(
            reverse('details', kwargs={'pk': self.bucketlists.first().id}),
            change_bucketlist, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_bucketlist(self):
        """Test the api can delete a bucketlist."""
        response = self.client.delete(
            reverse('details', kwargs={'pk': self.bucketlists.first().id}),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
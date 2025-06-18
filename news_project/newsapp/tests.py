from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from newsapp.models import Journalist, Publisher, Newsletter

User = get_user_model()


class NewsletterCreateTest(TestCase):
    """
    Test case for verifying that a Journalist can create a Newsletter.
    """

    def setUp(self):
        """
        Set up a test Journalist with a related Publisher before each test.
        """
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.user = User.objects.create_user(username="journalist", password="testpass")
        self.journalist = Journalist.objects.create(user=self.user, publisher=self.publisher)

    def test_journalist_can_create_newsletter(self):
        """
        Test if a logged-in Journalist can successfully create a Newsletter.
        """
        self.client.login(username="journalist", password="testpass")
        response = self.client.post(reverse('newsletter_create'), {
            'title': 'Test Newsletter',
            'content': 'This is a test newsletter.',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after success
        newsletter = Newsletter.objects.first()
        self.assertIsNotNone(newsletter)
        self.assertEqual(newsletter.title, 'Test Newsletter')
        self.assertEqual(newsletter.publisher, self.publisher)

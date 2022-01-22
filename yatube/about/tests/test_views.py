from django.test import TestCase, Client
from django.urls import reverse

TECH_URL = reverse('about:tech')
ABOUT_URL = reverse('about:author')


class PostPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/tech.html': TECH_URL,
            'about/author.html': ABOUT_URL
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

from http import HTTPStatus
from django.test import TestCase, Client


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_for_all_client(self):
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK)

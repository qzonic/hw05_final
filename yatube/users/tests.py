from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class UserTest(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_user_create(self):
        data = {
            'username': 'test-user',
            'password1': 'Adret324',
            'password2': 'Adret324'
        }
        self.guest.post(
            '/auth/signup/',
            data=data,
            follow=True
        )
        self.assertTrue(
            User.objects.filter(username='test-user').exists())

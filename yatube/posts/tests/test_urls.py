from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PostURLTests, cls).setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Это единственная тестовая группа'
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.second_user = User.objects.create_user(username='SecondHasNoName')
        cls.post = Post.objects.create(
            text='Это текст тестового поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_pages_for_all_users(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-group/',
            'posts/profile.html': '/profile/HasNoName/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_for_not_author(self):
        response = self.second_authorized_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_post_edit_page_for_author(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_guest(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_create_for_authorized_client(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

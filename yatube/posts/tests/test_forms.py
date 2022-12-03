from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание'
        )
        cls.second_group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-group-2',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст, добавленный из формы',
            'group': self.group.id,
            'author': self.authorized_client,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse(
                                 'posts:profile',
                                 kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        form_data = {
            'text': 'Исправленный текст из формы',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(self.post.text,
                            Post.objects.get(id=self.post.id).text)
        self.assertEqual(Post.objects.get(id=self.post.id).text,
                         form_data.get('text'))


class CommentTestForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            text='New post',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_create_comment(self):
        data = {
            'post': self.post.id,
            'author': self.user,
            'text': 'Test comment'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=data,
            follow=True
        )
        self.assertTemplateUsed(response, 'users/login.html')

    def test_add_comment(self):
        data = {
            'post': self.post.id,
            'author': self.user,
            'text': 'Test comment'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=data,
            follow=True
        )
        comment = response.context.get('comments')[0]
        self.assertEqual(comment.text, 'Test comment')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

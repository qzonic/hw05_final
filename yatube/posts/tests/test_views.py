from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, Follow


User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PostViewsTest, cls).setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.second_user = User.objects.create_user(username='NoName')
        cls.third_user = User.objects.create_user(username='NoNameUser')
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-group-1',
            description='Это первая тестовая группа'
        )
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
        cls.post = Post.objects.create(
            text='Это текст первого тестового поста',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.second_authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.third_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)
        self.third_authorized_client.force_login(self.third_user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            '/unexisting-page/': 'core/404.html'
        }

        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_list_profile_pages_show_correct_context(self):
        pages_names_templates = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'page_obj',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'post'
        }

        for reverse_name, ctx in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                if ctx != 'post':
                    post = response.context.get(ctx)[0]
                else:
                    post = response.context.get(ctx)
                self.assertEqual(
                    post.text, 'Это текст первого тестового поста')
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.author, self.user)
                self.assertTrue('/media/posts/small' in post.image.url)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        post = response.context.get('post')
        self.assertEqual(post.text, 'Это текст первого тестового поста')
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

    def test_post_edit_show_correct_context(self):
        pages_ctx = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField
            },
            reverse('posts:post_create'): {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField
            }
        }

        for page, ctx in pages_ctx.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                for i, expected in ctx.items():
                    form_field = response.context.get('form').fields.get(i)
                    self.assertIsInstance(form_field, expected)

    def test_post_create(self):
        form_data = {
            'text': 'Запись, добавленная через формы',
            'group': self.group.id,
            'author': self.authorized_client
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        pages_names_templates = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'page_obj'
        }

        for reverse_name, ctx in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context.get(ctx)[0]
                self.assertEqual(post.text, form_data.get('text'))
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.author, self.user)

    def test_cache(self):
        post_for_delete = Post.objects.create(
            text='Test cache',
            author=self.user
        )
        first_response = self.authorized_client.get('/')
        old_posts = first_response.content
        Post.objects.filter(text='Test cache').delete()
        second_response = self.authorized_client.get('/')
        new_posts = second_response.content
        self.assertEqual(old_posts, new_posts)
        cache.clear()
        third_response = self.authorized_client.get('/')
        third_posts = third_response.content
        self.assertNotEqual(old_posts, third_posts)

    def test_follow_and_unfollow(self):
        self.second_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username})
        )
        follow = Follow.objects.get(
            user=self.second_user.id,
            author=self.user.id
        )
        self.assertEqual(follow.author, self.user)
        self.assertEqual(follow.user, self.second_user)

        self.second_authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username})
        )
        follow = Follow.objects.filter(
            user=self.second_user.id,
            author=self.user.id
        ).exists()
        self.assertFalse(follow)

    def test_new_post_in_follow_page(self):
        Post.objects.create(
            text='Test follow post',
            author=self.user,
        )
        Post.objects.create(
            text='Test follow post from NoName',
            author=self.second_user,
        )
        self.second_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username})
        )
        self.third_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.second_user.username})
        )
        second_response = self.second_authorized_client.get(
            reverse('posts:follow_index')
        )
        third_response = self.third_authorized_client.get(
            reverse('posts:follow_index')
        )
        post_exist = second_response.context.get('page_obj')[0]
        post_unexist = third_response.context.get('page_obj')[0]
        self.assertEqual(post_exist.text, 'Test follow post')
        self.assertNotEqual(post_unexist.text, 'Test follow post')


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PostPaginatorTest, cls).setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-group-1',
            description='Это первая тестовая группа'
        )
        for i in range(1, 13):
            Post.objects.create(
                text=f'Это текст {i} тестового поста',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        pages_names_templates = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'page_obj'
        }
        for reverse_name, ctx in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[ctx]), 10)

    def test_second_page_contains_three_records(self):
        pages_names_templates = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'page_obj',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'page_obj'
        }
        for reverse_name, ctx in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context[ctx]), 2)

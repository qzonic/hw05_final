from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, который имеет больше 15 символов',
            group=cls.group
        )

    def test_post_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post.__str__()
        str_post = 'Тестовый пост, который имеет больше 15 символов'[:15]
        self.assertEqual(post, str_post)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = self.group.__str__()
        str_group = 'Тестовая группа'
        self.assertEqual(group,
                         str_group)

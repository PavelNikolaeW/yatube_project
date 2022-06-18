from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='lorem ipsum dolor sit',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        self.assertEqual('lorem ipsum dol', str(post))


class GroupModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание группы',
        )

    def test_models_have_correct_object_names(self):
        group = GroupModelTest.group
        self.assertEqual('Тестовая группа', str(group))

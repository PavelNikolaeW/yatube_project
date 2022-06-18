from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='www',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.post1 = Post.objects.create(
            text='Тестовый пост1',
            author=cls.user1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostURLTests.user)

    def test_pages_guest_client(self):
        urls = [
            '/',
            '/profile/auth/',
            '/posts/1/',
            '/group/www/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_guest_client(self):
        urls = [
            '/create/',
            '/posts/1/edit/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_not_found_pages(self):
        url = '/kek_gfdhgfxhgcbvnbn/'
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_auth_client(self):
        urls = [
            '/',
            '/create/',
            '/group/www/',
            '/profile/auth/',
            '/posts/1/',
            '/posts/1/edit/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_auth_client(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/posts/2/edit/': 'posts/access_denied.html',
            '/group/www/': 'posts/group_list.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address, template=template):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

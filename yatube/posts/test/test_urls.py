from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
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
        self.post_id = PostURLTests.post.id
        self.post1_id = PostURLTests.post1.id
        self.username = PostURLTests.user.username
        self.username1 = PostURLTests.user1.username
        cache.clear()

    def test_pages_guest_client(self):
        urls = [
            '/',
            '/profile/auth/',
            f'/posts/{self.post_id}/',
            '/group/www/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_guest_client(self):
        urls = [
            '/create/',
            f'/posts/{self.post_id}/edit/',
            f'/posts/{self.post_id}/comment/',
            '/follow/',
            f'/profile/{self.username}/follow/',
            f'/profile/{self.username}/unfollow/'
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
            f'/posts/{self.post_id}/',
            f'/posts/{self.post_id}/edit/',
            '/follow/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_auth_client(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            f'/posts/{self.post1_id}/edit/': 'posts/access_denied.html',
            '/group/www/': 'posts/group_list.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address, template=template):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_redirect_auth_client(self):
        urls = {
            f'/profile/{self.username1}/follow/':
                f'/profile/{self.username1}/',
            f'/profile/{self.username1}/unfollow/':
                f'/profile/{self.username1}/',
            f'/posts/{self.post_id}/comment/':
                f'/posts/{self.post_id}/',
        }

        for url, redirect in urls.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

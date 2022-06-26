import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from django.conf import settings

from ..models import Post, Group, Follow

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewsTests(TestCase):

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

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostViewsTests.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        post_id = PostViewsTests.post.id
        post1_id = Post.objects.create(
            text='Тестовый пост1',
            author=PostViewsTests.user1,
        ).id
        group_slug = PostViewsTests.group.slug
        username = PostViewsTests.user.username
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': group_slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[username]): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=[post_id]): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=[post1_id]): 'posts/access_denied.html',
            reverse(
                'posts:post_edit',
                args=[post_id]): 'posts/create_post.html',
        }

        for url, template in templates_pages_names.items():
            with self.subTest(url=url, template=template):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_guest_client(self):
        post_id = PostViewsTests.post.id
        group_slug = PostViewsTests.group.slug
        username = PostViewsTests.user.username
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': group_slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[username]): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=[post_id]): 'posts/post_detail.html',
        }

        for url, template in templates_pages_names.items():
            with self.subTest(url=url, template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.author.username, PostViewsTests.user.username)
        self.assertEqual(post.group.title, PostViewsTests.group.title)

    def test_context_post_detail(self):
        post_id = PostViewsTests.post.id
        response = self.auth_client.get(reverse(
            'posts:post_detail',
            args=[post_id])
        )
        post = response.context['post']
        self.assertEqual(post.pk, post_id)

    def test_form_create_post(self):
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field, excected in form_fields.items():
            form_field = response.context['form'].fields[field]
            self.assertIsInstance(form_field, excected)

    def test_form_edit_post(self):
        post_id = PostViewsTests.post.id
        response = self.auth_client.get(reverse(
            'posts:post_edit',
            args=[post_id]
        ))
        context_post_id = response.context['post_id']
        self.assertEqual(post_id, context_post_id)


class PaginatorViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='www',
            description='Тестовое описание группы'
        )
        Post.objects.bulk_create([Post(
            text=f'тестовый пост {n}',
            author=cls.user,
            group=cls.group
        ) for n in range(10)])
        Post.objects.bulk_create([Post(
            text=f'тестовый пост {n}',
            author=cls.user,
        ) for n in range(5)])

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PaginatorViewsTests.user)
        cache.clear()

    def test_paginator_first_page(self):
        group_slug = PaginatorViewsTests.group.slug
        username = PaginatorViewsTests.user.username
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': group_slug}),
            reverse(
                'posts:profile',
                args=[username])
        ]
        for url in urls:
            with self.subTest(url=url):
                response_first_page = self.auth_client.get(url)
                response_second_page = self.auth_client.get(url + '?page=2')
                self.assertEqual(
                    len(response_first_page.context['page_obj']),
                    10
                )
                if url not in '/group/www/':
                    self.assertEqual(
                        len(response_second_page.context['page_obj']),
                        5
                    )

    def test_context_group(self):
        response = self.auth_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'www'}
        ))
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 10)
        for post in posts:
            with self.subTest(post_group=post.group):
                self.assertEqual(post.group, PaginatorViewsTests.group)

    def test_context_profile(self):
        response = self.auth_client.get(reverse(
            'posts:profile',
            args=[PaginatorViewsTests.user.username]
        ))
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 10)
        for post in posts:
            with self.subTest(post_author=post.author):
                self.assertEqual(
                    post.author.username,
                    PaginatorViewsTests.user.username
                )


class CommentViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(CommentViewsTests.user)
        self.comment_data = {
            'text': 'comment'
        }

    def test_guest_client_add_comment(self):
        response = self.guest_client.get(reverse(
            'posts:add_comment',
            args=[CommentViewsTests.post.id]
        ))
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_auth_client_add_comment(self):
        response = self.auth_client.post(
            reverse(
                'posts:add_comment',
                args=[CommentViewsTests.post.id]
            ),
            data=self.comment_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[CommentViewsTests.post.id]
        ))
        response = self.auth_client.get(reverse(
            'posts:post_detail',
            args=[CommentViewsTests.post.id]
        ))
        self.assertContains(response, self.comment_data['text'])


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='auth1')

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(FollowTests.user)
        self.username = FollowTests.user.username
        self.username1 = FollowTests.user1.username

    def test_follow(self):
        self.auth_client.get(
            reverse('posts:profile_follow', args=[self.username1])
        )
        self.assertTrue(
            Follow.objects.filter(
                user=FollowTests.user,
                author=FollowTests.user1
            )
        )
        self.auth_client.get(
            reverse('posts:profile_unfollow', args=[self.username1])
        )
        self.assertFalse(
            Follow.objects.filter(
                user=FollowTests.user,
                author=FollowTests.user1
            )
        )
        self.auth_client.get(
            reverse('posts:profile_follow', args=[self.username])
        )
        self.assertFalse(
            Follow.objects.filter(
                user=FollowTests.user,
                author=FollowTests.user
            )
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImgUpload(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.auth_client.force_login(self.user)
        Group.objects.create(
            title='Тестовая группа',
            slug='www',
        )
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_img_upload(self):
        image = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x01\x00'
                b'\x01\x00\x00\x00\x00\x21\xf9\x04'
                b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
                b'\x00\x00\x01\x00\x01\x00\x00\x02'
                b'\x02\x4c\x01\x00\x3b'
            ),
            content_type='image/gif'
        )
        post_data = {
            "text": "Test post",
            "group": 1,
            "image": image
        }
        self.auth_client.post(reverse('posts:post_create'), post_data)
        urls = [
            reverse('posts:index'),
            reverse('posts:profile', args=[self.user.username]),
            reverse('posts:group_list', kwargs={'slug': 'www'}),
            reverse('posts:post_detail', args=[1]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertContains(response, '<img class="card-img my-2"')

    def test_not_allowed_file(self):
        image = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'kek'
            ),
            content_type='text/txt'
        )
        post_data = {
            "text": "Test post",
            "group": 1,
            "image": image
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            post_data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            'form',
            'image',
            "Загрузите правильное изображение. Файл, который вы "
            "загрузили, поврежден или не является изображением."
        )

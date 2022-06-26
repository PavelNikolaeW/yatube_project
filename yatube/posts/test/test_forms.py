import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post, Comment

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='test test',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # удалить временную папку
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostFormTests.user)

    def test_create_post_auth_client(self):
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'test text',
            'author': PostFormTests.user,
            'image': image
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=[PostFormTests.user.username]
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data['text']))

    def test_create_post_guest_client(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'test text',
            'author': PostFormTests.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(post_count, Post.objects.count())
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_change_post_auth_client(self):
        post_id = PostFormTests.post.id
        form_data = {
            'text': 'change text',
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', args=[post_id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[post_id]
        ))
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.text, form_data['text'])

    def test_change_post_guest_client(self):
        post_id = PostFormTests.post.id
        form_data = {
            'text': 'change text',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=[post_id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post_id}/edit/'
        )
        post = Post.objects.get(id=post_id)
        self.assertNotEqual(post.text, form_data['text'])


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='test test',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(CommentFormTest.user)

    def test_create_comment_auth_client(self):
        comment_count = Comment.objects.count()
        post_id = CommentFormTest.post.id
        comment_data = {
            'post': CommentFormTest.post,
            'author': CommentFormTest.user,
            'text': 'test comment'
        }
        response = self.auth_client.post(
            reverse('posts:add_comment', args=[post_id]),
            data=comment_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=[post_id]
            )
        )
        self.assertTrue(Comment.objects.filter(text='test comment'))

    def test_create_comment_guest_client(self):
        comment_count = Comment.objects.count()
        post_id = CommentFormTest.post.id
        comment_data = {
            'post': CommentFormTest.post,
            'text': 'test comment'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[post_id]),
            data=comment_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post_id}/comment/'
        )

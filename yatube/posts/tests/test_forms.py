import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'HasNoName'})
COMMENT_URL = reverse('posts:add_comment', kwargs={'post_id': 1})
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='first',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group,
            image=uploaded
        )
        cls.edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )
        cls.detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 2'
            ).exists())

    def test_edit_post(self):
        """Валидная форма создает отредактированную запись в Post."""
        response_1 = self.authorized_client.get(self.edit_url)
        form = response_1.context['form']
        data = form.initial
        data['text'] = 'Тестовый пост 2 редактированный'
        response = self.authorized_client.post(self.edit_url, data)
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(
            Post.objects.get(id=self.post.pk).text,
            'Тестовый пост 2 редактированный'
        )

    def test_create_post_image(self):
        """Валидная форма создает запись в Post."""
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
            'text': 'Тестовый пост с картинкой',
            'image': uploaded
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост с картинкой'
            ).exists())

    def test_comment_post(self):
        """После успешной отправки комментарий появляется на странице поста"""
        comments_count = Comment.objects.count()
        post_1_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': 1}
        )
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            COMMENT_URL,
            post_id=self.post.id,
            data=form_data,
            follow=True)
        response = self.authorized_client.get(
            post_1_detail_url,
            follow=True)
        self.assertContains(response, form_data['text'])
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post_id=self.post.id
            ).exists())

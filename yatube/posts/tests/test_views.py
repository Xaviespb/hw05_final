from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User, Follow

INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'HasNoName'})
GROUP_1_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug-1'})
GROUP_2_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug-2'})
DETAIL_URL = reverse('posts:post_detail', kwargs={'post_id': 13})
FOLLOW_URL = reverse('posts:follow_index')


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.posts_obj = []
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug-1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        for i in range(0, 12):
            cls.posts_obj.append(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group_1
            ))
        for i in range(12, 14):
            cls.posts_obj.append(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group_2,
                image=cls.uploaded
            ))
        cls.posts = Post.objects.bulk_create(cls.posts_obj)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': INDEX_URL,
            'posts/group_list.html': GROUP_1_URL,
            'posts/profile.html': PROFILE_URL,
            'posts/post_detail.html': DETAIL_URL,
            'posts/create_post.html': CREATE_URL,
            'posts/follow.html': FOLLOW_URL,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(INDEX_URL)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост 13')
        self.assertTrue(first_object.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(GROUP_2_URL)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост 13')
        self.assertTrue(first_object.image)
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group_2)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост 13')
        self.assertTrue(first_object.image)
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(DETAIL_URL))
        self.assertEqual(response.context.get('post').text, 'Тестовый пост 12')
        self.assertTrue(response.context.get('post').image)

    def test_create_post_pages_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_pages_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Проверяем паджинатор
    def test_index_page_contains_10(self):
        '''На страницу index выводится по 10 постов'''
        response = self.client.get(INDEX_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_page_contains_4(self):
        '''На вторую страницу index выводится 4 поста'''
        response = self.client.get(INDEX_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_page_contains_10(self):
        '''На страницу group_list выводится 10 постов'''
        response = self.client.get(GROUP_1_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_page_contains_2(self):
        '''На вторую страницу group_list выводится 2 поста'''
        response = self.client.get(GROUP_1_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_profile_page_contains_10(self):
        '''На страницу profile выводится 10 постов'''
        response = self.client.get(PROFILE_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_contains_4(self):
        '''На вторую страницу profile выводится 4 поста'''
        response = self.client.get(PROFILE_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_cash_index(self):
        '''Тестирование кэширование старницы index'''
        response = self.client.get(INDEX_URL)
        Post.objects.all().delete()
        self.assertTrue(response.content)

    def test_follow_auth(self):
        ''' Авторизированный пользователь может подписываться и отписываться
        '''
        following = User.objects.create(username='following')
        profile_url_following = reverse('posts:profile_follow',
                                        kwargs={'username': 'following'})
        self.authorized_client.post(
            profile_url_following,
            follow=True)
        self.assertTrue(
            Follow.objects.filter(user=self.user,
                                  author=following
                                  ).exists())
        profile_url_unfollow = reverse('posts:profile_unfollow',
                                       kwargs={'username': 'following'})
        self.authorized_client.post(
            profile_url_unfollow,
            follow=True)
        self.assertFalse(
            Follow.objects.filter(user=self.user,
                                  author=following
                                  ).exists())

    def test_new_follow_post(self):
        """ Новая запись пользователя появляется в ленте тех, кто на него
            подписан и не появляется в ленте тех, кто не подписан на него.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user,
                              author=following)
        post = Post.objects.create(author=following,
                                   text='Новый тестовый пост для подписчиков')
        response = self.authorized_client.get(
            FOLLOW_URL,
            follow=True)
        self.assertIn(post, response.context['page_obj'].object_list)

        self.client.logout()
        unfollow_user = User.objects.create_user(
            username='user_unfollow',
        )
        authorized_unfollow_client = Client()
        authorized_unfollow_client.force_login(unfollow_user)
        response_2 = authorized_unfollow_client.get(
            FOLLOW_URL,
            follow=True)
        self.assertNotIn(post, response_2.context['page_obj'].object_list)

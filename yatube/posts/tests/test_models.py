from django.test import TestCase

from ..models import Group, Post, User, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.comment = Comment.objects.create(
            post=self.post,
            text='Тестовый коммент',
            author=self.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = self.comment
        string_group = group.__str__()
        string_post = post.__str__()
        string_comment = comment.__str__()
        self.assertEqual(string_post, 'Тестовый пост')
        self.assertEqual(string_group, 'Тестовая группа')
        self.assertEqual(string_comment, 'Тестовый коммент')

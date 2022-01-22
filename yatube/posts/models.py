import textwrap as tw

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """ Модель для сообществ """
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = "Group"

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """ Модель для хранения постов """
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='groups_posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = "Post"
        ordering = ('-pub_date', 'pk')

    def __str__(self) -> str:
        return tw.shorten(str(self.text), 15)


class Comment(models.Model):
    """ Модель для хранения комментариев """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField('Дата публикации комментария',
                                   auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = "Comment"


class Follow(models.Model):
    """ Модель для хранения подписок """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

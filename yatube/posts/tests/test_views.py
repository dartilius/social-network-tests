from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()
LIMIT = 10
REMAINS = 6


class ViewsTests(TestCase):
    """Класс тестирования страниц."""

    @classmethod
    def setUpClass(cls):
        """Метод с фикстурами."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        for i in range(15):
            cls.new_post1 = Post.objects.create(
                author=cls.user,
                text=f'Текст поста {i + 1}',
                group=cls.group
            )


    def setUp(self):
        """Метод с фикстурами."""
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # Создаем пользователя
        self.auth_user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.auth_user)
        # авторизуем автора поста
        self.author = Client()
        self.author.force_login(ViewsTests.user)
        # соотношение view к шаблону
        self.views_tempaltes = {
            'posts:index': 'posts/index.html',
            'posts:group_posts': 'posts/group_list.html',
            'posts:profile': 'posts/profile.html',
            'posts:post_detail': 'posts/post_detail.html',
            'posts:post_create': 'posts/create_post.html',
            'posts:post_edit': 'posts/create_post.html'
        }
        # аргументы принимаемые view функцией
        self.views_kwargs = {
            'posts:index': '',
            'posts:group_posts': {'slug': ViewsTests.group.slug},
            'posts:profile': {'username': ViewsTests.user.username},
            'posts:post_detail': {'post_id': ViewsTests.post.pk},
            'posts:post_create': '',
            'posts:post_edit': {'post_id': ViewsTests.post.pk},
        }

    def test_views_uses_correct_templates(self):
        """Проверяем что view функции используют нужный шаблон."""
        for view, template in self.views_tempaltes.items():
            with self.subTest(field=view):
                response = self.author.get(
                    reverse(view, kwargs=self.views_kwargs[view])
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    f'{view} использует несоответствующий шаблон.'
                )

    def test_first_page_paginator(self):
        """Проверяем что на первой странице отображается 10 постов."""
        views = ('posts:index', 'posts:group_posts', 'posts:profile')
        for view in views:
            response = self.author.get(
                reverse(view, kwargs=self.views_kwargs[view])
            )
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(
                len(response.context['page_obj']),
                LIMIT,
                f'Пагинатор отображает неправильное '
                f'количество постов на странице {view}.'
            )

    def test_second_page_paginator(self):
        """Проверяем пагинатор на второй странице."""
        views = ('posts:index', 'posts:group_posts', 'posts:profile')
        for view in views:
            response = self.author.get(
                reverse(view, kwargs=self.views_kwargs[view]) + '?page=2'
            )
            self.assertEqual(
                len(response.context['page_obj']),
                REMAINS,
                f'Пагинатор отображает неправильное '
                f'количество постов на второй странице {view}.'
            )

    def test_context_pages(self):
        """Проверяем контексты страниц index, group, profile."""
        views = ('posts:index', 'posts:group_posts', 'posts:profile')
        for view in views:
            response = self.author.get(
                reverse(view, kwargs=self.views_kwargs[view])
            )
            first_object = response.context['posts'][0]
            self.assertEqual(
                first_object.text,
                'Тестовый пост',
                f'{view} отображает пост с неправильным текстом.'
            )
            self.assertEqual(
                first_object.group,
                ViewsTests.group,
                f'{view} отображает пост с неправильной группой.'
            )
            self.assertEqual(
                first_object.author,
                ViewsTests.user,
                f'{view} отображает пост с неправильным автором.'
            )

    def test_post_detail_context(self):
        """Проверка контекста страницы поста."""
        response = self.author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': ViewsTests.post.pk}
            )
        )
        self.assertEqual(
            response.context['post'].text,
            'Тестовый пост',
            'Страница поста отображает пост с неправильным текстом.'
        )
        self.assertEqual(
            response.context['post'].author,
            ViewsTests.user,
            'Страница поста отображает неправильного автора.'
        )
        self.assertEqual(
            response.context['post'].group,
            ViewsTests.group,
            'Страница поста отображает неправильную группу.'
        )

    def test_create_post_context(self):
        """Проверка контекста страницы создания поста."""
        response = self.author.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_context(self):
        """Проверка контекста страницы редактирования поста."""
        response = self.author.get(
            reverse('posts:post_edit', kwargs={'post_id': ViewsTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_home_page_after_create_new_post(self):
        """Проверяем появился ли пост на главной странице."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['posts'][0], last_post)

    def test_profile_page_after_create_new_post(self):
        """Проверяем появился ли пост на странице пользователя."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': ViewsTests.user.username}
            )
        )
        self.assertEqual(response.context['posts'][0], last_post)

    def test_group_page_after_create_new_post(self):
        """Проверяем появился ли пост на странице группы."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': ViewsTests.group.slug}
            )
        )
        self.assertEqual(response.context['posts'][0], last_post)

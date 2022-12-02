from django.contrib.auth import get_user_model
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
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
        cls.index_url = reverse('posts:index')
        cls.group_url = reverse(
            'posts:group_posts',
            kwargs={'slug': ViewsTests.group.slug}
        )
        cls.profile_url = reverse(
            'posts:profile',
            kwargs={'username': ViewsTests.user.username}
        )
        cls.post_detail_url = reverse(
            'posts:post_detail',
            kwargs={'post_id': ViewsTests.post.pk}
        )
        cls.pots_create_url = reverse('posts:post_create')
        cls.post_edit_url = reverse(
            'posts:post_edit',
            kwargs={'post_id': ViewsTests.post.pk}
        )
        cls.urls_templates = {
            ViewsTests.post_edit_url: 'posts/create_post.html',
            ViewsTests.pots_create_url: 'posts/create_post.html',
            ViewsTests.post_detail_url: 'posts/post_detail.html',
            ViewsTests.profile_url: 'posts/profile.html',
            ViewsTests.group_url: 'posts/group_list.html',
            ViewsTests.index_url: 'posts/index.html'
        }

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

    def test_views_uses_correct_templates(self):
        for url, template in ViewsTests.urls_templates.items():
            response = self.author.get(url)
            self.assertTemplateUsed(response, template)

    def test_first_page_paginator(self):
        """Проверяем что на первой странице отображается 10 постов."""
        views = (
            ViewsTests.index_url,
            ViewsTests.group_url,
            ViewsTests.profile_url
        )
        for view in views:
            response = self.author.get(view)
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(
                len(response.context['page_obj']),
                LIMIT,
                f'Пагинатор отображает неправильное '
                f'количество постов на странице {view}.'
            )

    def test_second_page_paginator(self):
        """Проверяем пагинатор на второй странице."""
        views = (
            ViewsTests.index_url,
            ViewsTests.group_url,
            ViewsTests.profile_url
        )
        for view in views:
            response = self.author.get(view + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                REMAINS,
                f'Пагинатор отображает неправильное '
                f'количество постов на второй странице {view}.'
            )

    def test_context_pages(self):
        """Проверяем контексты страниц index, group, profile."""
        views = (
            ViewsTests.index_url,
            ViewsTests.group_url,
            ViewsTests.profile_url
        )
        for view in views:
            response = self.author.get(view)
            first_object = response.context['posts'][0]
            self.assertEqual(
                first_object.text,
                'Текст поста 15',
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
        response = self.author.get(ViewsTests.post_detail_url)
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
        response = self.author.get(ViewsTests.pots_create_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_edit_post_context(self):
        """Проверка контекста страницы редактирования поста."""
        response = self.author.get(ViewsTests.post_edit_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(
            response.context['is_edit'],
            'View функция передала направильный контекст is_edit'
        )

    def test_home_page_after_create_new_post(self):
        """Проверяем появился ли пост на главной странице."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(ViewsTests.index_url)
        self.assertEqual(response.context['posts'][0], last_post)

    def test_profile_page_after_create_new_post(self):
        """Проверяем появился ли пост на странице пользователя."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(ViewsTests.profile_url)
        self.assertEqual(response.context['posts'][0], last_post)

    def test_group_page_after_create_new_post(self):
        """Проверяем появился ли пост на странице группы."""
        last_post = Post.objects.create(
            author=ViewsTests.user,
            text='Это самый новый пост',
            group=ViewsTests.group
        )
        response = self.authorized_client.get(ViewsTests.group_url)
        self.assertEqual(response.context['posts'][0], last_post)

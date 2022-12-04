from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
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
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Текст длинна которого больше 15 символов'
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
        self.author.force_login(StaticURLTests.user)

    def test_pages(self):
        """Проверка доступности страниц."""
        pages = (
            '/',
            f'/group/{StaticURLTests.group.slug}/',
            f'/posts/{StaticURLTests.post.pk}/',
            f'/profile/{StaticURLTests.user.username}/',
        )
        for page in pages:
            response = self.guest_client.get(page)
            self.assertEqual(
                response.status_code,
                200,
                f'Cтраница {page} отдает неправильный статус код.'
            )

    def test_page_templates(self):
        """Проверяем что страницы с правильными шаблонами."""
        pages = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/posts/{StaticURLTests.post.pk}/': 'posts/post_detail.html',
            f'/profile/{StaticURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{StaticURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for page, template in pages.items():
            response = self.author.get(page)
            self.assertTemplateUsed(
                response,
                template,
                f'{page} использует неправильныый шаблон'
            )

    def test_post_edit_for_author(self):
        """Проверка доступности редактирования поста для автора."""
        response = self.author.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertEqual(
            response.status_code,
            200,
            'Страница редактирования отдает неправильный '
            'статус код для автора.'
        )

    def test_post_edit_for_not_author(self):
        """Проверка переадресации со страницы редактирования поста
        на страницу поста для пользователей не являющихся автором."""
        response = self.authorized_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertRedirects(response, f'/posts/{StaticURLTests.post.pk}/')

    def test_post_edit_guest(self):
        """Проверка переадресации со страницы редактирования поста
        для гостя на страницу авторизации."""
        response = self.guest_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{StaticURLTests.post.pk}/edit/'
        )

    def test_create_post(self):
        """Проверка страницы создания поста."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(
            response.status_code,
            200,
            'Страница создания поста выдает неправильный статус код.'
        )

    def test_guest_create_post(self):
        """Проверка переадресации co страницы
        создания поста для гостя на авторизацию."""
        resource = self.guest_client.get('/create/')
        self.assertRedirects(resource, '/auth/login/?next=/create/')

    def test_unexisting_page(self):
        """Проверка недоступной страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            404,
            'Недоступная страница выдает неправильный статус код.'
        )

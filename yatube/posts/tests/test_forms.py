from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class FormsTests(TestCase):
    """Класс тестирования форм."""

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

    def setUp(self):
        """Метод с фикстурами."""
        self.guest_client = Client()
        self.author = Client()
        # Авторизуем пользователя
        self.author.force_login(FormsTests.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_form(self):
        """Проверяем что записи создаются корректно."""
        count = Post.objects.count()
        form_data = {
            'text': 'Мы сделали новую запись!',
            'group': FormsTests.group.pk
        }
        response = self.author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': FormsTests.user.username}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=FormsTests.user,
                group=form_data['group']
            ).count()
        )

    def test_edit_form(self):
        """Проверяем что запись в базе данных изменилась."""
        form_data = {
            'text': 'Мы изменили новую запись!',
            'group': FormsTests.group.pk
        }
        count = Post.objects.count()
        response = self.author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': FormsTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        # проверяем что новой записи не создалось
        self.assertEqual(Post.objects.count(), count)
        # проверяем что запись изменилась
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=FormsTests.user,
                group=form_data['group']
            ).count()
        )
        # проверяем что сработал редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': FormsTests.post.pk}
            )
        )

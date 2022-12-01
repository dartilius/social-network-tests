from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Класс тестирования моделей."""

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

    def test_models_have_correct_object_names_short(self):
        """Проверяем, что у моделей с текстом
        короче 15 символов корректно работает __str__."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:15],
            'В модели Post неправильно работает метод __str__'
            'при длинне текста меньше 15 символов.'
        )

    def test_models_have_correct_object_names_long(self):
        """Тест метода __str__ в модели Post с длинным текстом."""
        self.assertEqual(
            str(PostModelTest.post_2),
            PostModelTest.post_2.text[:15],
            'В модели Post неправильно работает метод __str__'
            'при длинне текста больше 15 символов.'
        )

    def test_models_have_correct_object_names_groups(self):
        """Тест метода __str__ в модели Group."""
        self.assertEqual(
            str(PostModelTest.group),
            PostModelTest.group.title,
            'В модели Group неправильно работает метод __str__.'
        )

    def test_posts_have_correct_verbose_name(self):
        """Тест verbose_name в можели Post."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value,
                    f'Поле {field} модели Post имеет '
                    f'некорректный verbose_name.'
                   )

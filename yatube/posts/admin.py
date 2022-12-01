from django.contrib import admin

from posts.models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """Модель поста для отображения его в админ панели."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Модель группы для отображения ее в админ панели."""

    list_display = ('pk', 'title', 'slug', 'description')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)

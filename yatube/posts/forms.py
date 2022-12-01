from django import forms

from posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_text(self):
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError('Заполните поле text')

        return data

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
            'group',
            'image'
        ]
        labels = {
            'text': _('Пост'),
            'group': _('Группа'),
        }
        help_texts = {
            'text': _('Текст поста.'),
            'group': _('Группа, к которой будет относиться пост.'),
        }

    def clean_text(self):
        """Валидатор который проверяет наличие текста в публикации"""
        data = self.cleaned_data['text']

        if not data:
            raise forms.ValidationError(
                _('В посте должен быть текст.'),
                code='min_len_error'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

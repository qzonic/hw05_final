from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].required = True

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа, к которой будет относиться пост'),
            'image': ('Картинка для поста')
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа '
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

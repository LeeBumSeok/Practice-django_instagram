from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'image')

        def __init__(self, *args, **kwargs):
            super(PostForm, self).__init__(*args, **kwargs)
            self.fields['image'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

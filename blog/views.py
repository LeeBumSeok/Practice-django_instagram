# -*- coding: utf-8 -*-

from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, UserForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django import forms
from django.http import HttpResponseRedirect, HttpResponse


# Create your views here.


def post_list(request):
    posts = Post.objects.filter(
        published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        author = Post.objects.get(pk=pk)
        if author.author == User.objects.get(username=request.user.get_username()):
            author = Post.objects.get(pk=pk)
            form = PostForm(instance=post)
            return render(request, 'blog/post_edit.html', {'form': form})
        else:
            return redirect('warning')


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(
        published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    author = Post.objects.get(pk=pk)
    if author.author == User.objects.get(username=request.user.get_username()):
        post.delete()
        return redirect('post_list')
    else:
        return redirect('warning')


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if str(comment.author) == str(User.objects.get(username=request.user.get_username())):
        comment.approve()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        return redirect('warning')


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if str(comment.author) == str(User.objects.get(username=request.user.get_username())):
        comment.delete()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        return redirect('warning')


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(
                username=request.POST["username"], password=request.POST['password1'])
            login(request, user)
            return redirect('/')
    return render(request, 'blog/registration/signup.html')


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post_like, post_like_created = post.like_set.get_or_create(
        user=request.user)

    if not post_like_created:
        post_like.delete()
        return redirect('/post/'+str(post.id))
    return redirect('/post/'+str(post.id))


def warning(request):
    return render(request, 'blog/warning.html')

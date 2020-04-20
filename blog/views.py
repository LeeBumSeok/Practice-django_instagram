# -*- coding: utf-8 -*-

from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Post, Comment, Follow
from .forms import PostForm, UserForm
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm, ProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.detail import DetailView
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic import ListView


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


def post_likelist(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/likelist.html')


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            temp = comment.author.pk
            comment.save()
            comment.approve()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if str(comment.author) == str(User.objects.get(username=request.user.get_username())):
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


class ProfileView(DetailView):
    context_object_name = 'profile_user'
    model = User
    template_name = 'blog/profile.html'


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


class ProfileUpdateView(View):
    def get(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        user_form = UserForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

        if hasattr(user, 'profile'):
            profile = user.profile
            profile_form = ProfileForm(initial={
                'nickname': profile.nickname,
                'profile_photo': profile.profile_photo,
            })
        else:
            profile_form = ProfileForm()

        return render(request, 'blog/profile_update.html', {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        u = User.objects.get(id=request.user.pk)
        user_form = UserForm(request.POST, instance=u)

        if user_form.is_valid():
            user_form.save()

        if hasattr(u, 'profile'):
            profile = u.profile
            profile_form = ProfileForm(
                request.POST, request.FILES, instance=profile)
        else:
            profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = u
            profile.save()

        return redirect('profile', pk=request.user.pk)


class UserList(ListView):
    model = User
    template_name = 'blog/user_list.html'


class Following(View):
    def get(self, request, *args, pk):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        else:
            user = request.user
            opponent = User.objects.get(pk=pk)

            if user != opponent:
                if not Follow.objects.filter(who=user):
                    Follow.objects.create(who=user)

                if not Follow.objects.filter(who=opponent):
                    Follow.objects.create(who=opponent)

            Iam = Follow.objects.get(who=user.id)
            Uare = Follow.objects.get(who=opponent.id)

            if str(opponent.id) not in Iam.following.split():
                Iam.following += f'{opponent.id} '
                Uare.followedBy += f'{user.id}'
                Iam.save()
                Uare.save()
        return HttpResponseRedirect(reverse('followlist'))


class Unfollow(View):

    def get(self, request, *args, pk):

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        else:
            user = request.user
            opponent = User.objects.get(pk=pk)

            if user != opponent:
                Iam = Follow.objects.get(who=user.id)
                Uare = Follow.objects.get(who=opponent.id)

                if str(opponent.id) in Iam.following.split():

                    Iam.following = Iam.following.replace(
                        f' {opponent.id} ', ' ')
                    Uare.followedBy = Uare.followedBy.replace(
                        f' {user.id} ', ' ')
                    Iam.save()
                    Uare.save()

            return HttpResponseRedirect(reverse('followlist'))


class FollowList(View):
    template_name = 'blog/follow_list'

    def get(self, request, *args, **kwargs):
        context = {}

        context['following_list'] = self.get_following_list()
        context['followed_list'] = self.get_followedBy_list()
        return render(request, 'blog/follow_list.html', context)


def get_following_list(self):
    user = self.request.user
    selected = Follow.objects.get(who=user.id)

    following_id = selected.following.split()
    following_id.remove('0')
    following_list = []
    for num in following_id:
        follower = User.objects.get(id=int(num))
        following_list.append(follower)

    return following_list

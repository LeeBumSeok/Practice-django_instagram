from django.contrib import admin
from .models import Post, Comment, Like, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)


class ProfileInline(admin.StackedInline):
    model = Profile
    con_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

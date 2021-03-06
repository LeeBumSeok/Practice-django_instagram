from django.urls import path
from . import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from .views import ProfileUpdateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    url(r'^drafts/$', views.post_draft_list, name='post_draft_list'),
    url(r'^post/(?P<pk>\d+)/publish/$', views.post_publish, name='post_publish'),
    url(r'^post/(?P<pk>\d+)/remove/$', views.post_remove, name='post_remove'),
    url(r'^post/(?P<pk>\d+)/comment/$',
        views.add_comment_to_post, name='add_comment_to_post'),
    url(r'^comment/(?P<pk>\d+)/approve/$',
        views.comment_approve, name='comment_approve'),
    url(r'^comment/(?P<pk>\d+)/remove/$',
        views.comment_remove, name='comment_remove'),
    path('warning', views.warning, name='warning'),
    path('like/<int:pk>/', views.post_like, name='post_like'),
    path('post/<int:pk>/likelist/', views.post_likelist, name='post_likelist'),
    url(r'^profile/(?P<pk>[0-9]+)/$',
        views.login_required(views.ProfileView.as_view()), name='profile'),
    path('follow/<int:pk>/', views.follow, name='follow'),
    url(r'^profile_update/$', login_required(ProfileUpdateView.as_view()),
        name='profile_update'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

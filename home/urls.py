from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings_view, name="settings"),
    path("upload", views.upload, name="upload"),
    path("follow", views.follow, name="follow"),
    path("search", views.search, name="search"),
    path("profile/<str:pk>", views.profile, name="profile"),
    path("like-post", views.like_post, name="like-post"),
    path('delete/<str:pk>/<uuid:post_id>/', views.delete_post, name='delete_post'),
    path("chat", views.chat, name="chat"),
    path('delete-chat/<str:chat_id>/', views.delete_chat, name='delete_chat'),
    path('chat/<str:currentUser>/', views.get_chat_log, name='chat_log'),
]


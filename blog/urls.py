from django.urls import path
from .views import (
    PostListView, 
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView
    )
from . import views

urlpatterns = [
    path('', PostListView.as_view(),name='Blog-home'),
    path('user/<str:username>', UserPostListView.as_view(),name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(),name='posts-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(),name='posts-update'),
    path('post/new/', PostCreateView.as_view(),name='posts-create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(),name='posts-delete'),
    path('about/',views.about,name='about-blog'),
]

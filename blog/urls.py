from django.urls import path
from .views import (
    PostListView, 
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    add_article,
    set_active_post
    )
from . import views

urlpatterns = [
    path('', PostListView.as_view(),name='Blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(),name='posts-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(),name='posts-update'),
    path('post/new/', PostCreateView.as_view(),name='posts-create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(),name='posts-delete'),
    path('about/',views.about,name='about-blog'),
    path('api/add-article/', views.add_article, name='add-article'),
    path('post/<int:pk>/set-active-post/', views.set_active_post, name='set-active-post')
]

from django.urls import path
from .views import (
    PostListView, 
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    add_article,
    set_active_post,
    canva_view,
    save_canva,
    get_canva,
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
    path('post/<int:pk>/set-active-post/', views.set_active_post, name='set-active-post'),
    path('post/<int:pk>/canva/', views.canva_view, name='canva-view'),
    path('api/post/<int:pk>/save-canva/', views.save_canva, name='save-canva'),
    path('api/post/<int:pk>/get-canva/', views.get_canva, name='get-canva'),
   
]

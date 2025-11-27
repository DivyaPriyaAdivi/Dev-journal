from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from .models import Post, ArticleReference
from rest_framework import generics, permissions
from .serializers import PostSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response



def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    paginate_by = 10

    def get_queryset(self):
        post = Post.objects.order_by("-date_posted")
        if self.request.user.is_authenticated:
            return post.filter(author=self.request.user)
        return post.none()


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'about'})


@login_required
def canva_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    return render(request, 'blog/canva.html', {'post': post})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def save_canva(request, pk):
    if request.method == 'PATCH':
        post = get_object_or_404(Post, pk=pk, author=request.user)
        canva_data = request.data.get('canva')
        post.canva = canva_data
        post.save()
        return Response({'message': 'canva data saved successfully!', 'canva': post.canva}, status=200)
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_canva(request, pk):
    if request.method == 'GET':
        post = get_object_or_404(Post, pk=pk, author=request.user)
        return Response({'canva': post.canva})


class PostCreateAPI(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_article(request):
    try:
        active_post = Post.objects.get(author=request.user, is_active=True)
    except Post.DoesNotExist:
        return Response({"error": "No active post found"}, status=400)

    title = request.data.get("title")
    url = request.data.get("url")
    note = request.data.get("note", "")

    if not url:
        return Response({"error": "URL is required"}, status=400)

    article = ArticleReference.objects.create(
        post=active_post,
        title=title or "Untitled",
        url=url,
        note=note
    )
    return Response({"success": True, "id": article.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_active_post(request, post_id):
    Post.objects.filter(author=request.user, is_active=True).update(is_active=False)
    try:
        post = Post.objects.get(id=post_id, author=request.user)
        post.is_active = True
        post.save()
        return Response({"success": True, "active_post": post.title})
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)


@login_required
def set_active_post(request, pk):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=pk, author=request.user)
        Post.objects.filter(author=request.user, is_active=True).update(is_active=False)
        post.is_active = not post.is_active
        post.save()

        return JsonResponse({"success": True, "is_active": post.is_active})

    return JsonResponse({"error": "Invalid request"}, status=400)

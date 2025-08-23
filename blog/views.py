from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, ArticleReference
from rest_framework import generics, permissions
from .serializers import PostSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework.response import Response

# Create your views here.
def home(request):
	context={
	'posts':Post.objects.all()
	}
	return render(request,'blog/home.html',context)

class PostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'     #<app>/<model>_<viewtype>.html
	ordering = ['-date_posted']
	paginate_by = 5

class UserPostListView(ListView):
	model = Post
	template_name = 'blog/user_post.html'
	context_object_name = 'posts'     #<app>/<model>_<viewtype>.html
	ordering = ['-date_posted']
	paginate_by = 5

	def get_queryset(self):
		user =get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
	model = Post

class PostCreateView(LoginRequiredMixin,CreateView):
	model = Post
	fields =['title','content']

	def form_valid(self,form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
	model = Post
	fields =['title','content']

	def form_valid(self,form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post=self.get_object()
		if self.request.user ==post.author:
			return True
		return False

class PostDeleteView(DeleteView):
	model = Post
	success_url='/'

	def test_func(self):
		post=self.get_object()
		if self.request.user ==post.author:
			return True
		return False



def about(request):
	return render(request,'blog/about.html',{'title':'about'})

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
def toggle_active_post(request, post_id):
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

        # unset all other active posts
        Post.objects.filter(author=request.user, is_active=True).update(is_active=False)

        # toggle current post
        post.is_active = not post.is_active
        post.save()

        return JsonResponse({"success": True, "is_active": post.is_active})

    return JsonResponse({"error": "Invalid request"}, status=400)
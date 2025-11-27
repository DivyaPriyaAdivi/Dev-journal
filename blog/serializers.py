from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'date_posted', 'author','canva']
        read_only_fields = ['author', 'date_posted']
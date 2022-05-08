from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import Group, Post


def index(request):
    posts = Post.objects.all().order_by('-pub_date')[:10]
    context = {
        "posts": posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        "group": group,
        'posts': posts
    }
    return render(request, 'posts/group_list.html', context)

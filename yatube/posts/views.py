from django.shortcuts import render
from django.http import HttpResponse


def index(request):
	return HttpResponse("Index")


def group_posts(request, group):
	return HttpResponse(f"group_posts {group}")
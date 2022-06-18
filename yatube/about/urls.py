from django.urls import path
from django.views.generic.base import TemplateView

app_name = 'about'

urlpatterns = [
    path(
        'tech/',
        TemplateView.as_view(template_name='about/tech.html'),
        name='tech'
    ),
    path(
        'author/',
        TemplateView.as_view(template_name='about/author.html'),
        name='author'
    ),
]

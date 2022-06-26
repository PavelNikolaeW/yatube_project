from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'path': request.path,
        'status': 404
    }
    return render(request, 'core/404.html', context=context, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html', status=403)


def server_error(request):
    return render(request, 'core/500.html', status=500)

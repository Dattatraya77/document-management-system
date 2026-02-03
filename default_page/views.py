from django.shortcuts import render


def default_page(request):
    context = {
        'title': 'Default Page'
    }
    return render(request, 'default_page.html', context)

from django.shortcuts import render


def index(request):
    my_dict = {'insert_me': 'Hello im from views !!!'}
    return render(request, 'characters_explorer/index.html', context=my_dict)

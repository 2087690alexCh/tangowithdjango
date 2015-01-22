from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    context_dict = {'boldmessage': "I am a bold font from the context"}
    return render(request, 'rango/index.html', context_dict)
    #return HttpResponse("<br>Rango says hey there world!</br> <a href='/rango/about'>About</a>")


def about(request):
    author = {'author': "Alex Chilikov"}
    return render(request, 'rango/about.html', author)
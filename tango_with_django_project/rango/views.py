from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("<br>Rango says hey there world!</br> <a href='/rango/about'>About</a>")

def about(request):
    return HttpResponse("<br>This tutorial has been put together by Alex Chilikov, 2087690"
                        "</br> <a href='/rango/'>Index</a>")
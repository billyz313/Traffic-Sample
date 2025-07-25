from django.shortcuts import render

version = 1.16  # versioning for js and css

def index(request):

    return render(request, 'index.html', {'version':version})


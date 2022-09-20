from django.shortcuts import render


def error_500_view(request):
    # we add the path to the 500.html file
    # here. The name of our HTML file is 404.html
    return render(request, '500.html')

from django.http import HttpResponse
from django.shortcuts import render

def home_page(request):
    context = {}
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT1")
    if 'warning' in request.session:
        context['warning'] = request.session['warning']
        del request.session['warning']
    if 'success' in request.session:
        context['success'] = request.session['success']
        del request.session['success']
    if 'info' in request.session:
        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        context['info'] = request.session['info']
        del request.session['info']
    if 'danger' in request.session:
        context['danger'] = request.session['danger']
        del request.session['danger']

    return render(request, "home-4.html", context)
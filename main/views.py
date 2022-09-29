from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import *




def index(request):
    context = {'temp': 1}
    return render(request, 'main/index.html', context)

def login(request):
    context = {'temp': 1}
    return render(request, 'main/login.html', context)

def signup(request):
    if request.method == "POST":
        user = User(username=request.POST['inputEmail'],
                    first_name=request.POST['inputFirstName'],
                    last_name=request.POST['inputLastName'],
                    email=request.POST['inputEmail'],
                    password=request.POST['inputPassword']
        )
        user.save()
        usuario = Usuario(user=user,
                          tipo=TipoUsuario.objects.get(pk=int(request.POST['inputType'])),
                          direccion=request.POST['inputAddress'],
                          telefono=request.POST['inputPhone'])
        usuario.save()
        return HttpResponseRedirect('/main/') ## Aquí va el index
    return render(request, 'main/signup.html', {'temp': 1})

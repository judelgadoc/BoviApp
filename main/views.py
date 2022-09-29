from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import *

# Create your views here.

def index(request):
    context = {'temp': 1}
    return render(request, 'main/index.html', context)

   
def login(request):
    try:
        del request.session['email_f']
    except:
        print("No hay seccion iniciada")   
    if request.method=='POST':
       email_f=request.POST['correo']
       contraseña=(request.POST['contra'])
       print(contraseña)
       veri=User.objects.filter(username=email_f,password=contraseña).exists()
       if veri ==True:
        request.session['email_f']=email_f
        return render(request,'main/index.html',{'email_f':email_f})
       else:
        messages.add_message(request, level=messages.WARNING,message='Nombre de usuario o Contraseña Incorrectos')
    return render(request,'main/login.html')
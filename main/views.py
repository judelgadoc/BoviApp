from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import *

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        context = {'user':request.user,'usuario':Usuario.objects.get(user=request.user),'breeds':RazaGanado.objects.all()}
    else:
        context = {'user':request.user}
    return render(request, 'main/index.html', context) 
    

def our_login(request):
    if request.method == "POST":
        email_f=request.POST['correo']
        password=(request.POST['contra'])
        rememberme = request.POST.get('inputRememberme', "off")
        print(rememberme)
        user = authenticate(username=email_f, password=password)
        if user is not None:
            login(request, user)
            if rememberme == "off":
                request.session.set_expiry(0)
            return HttpResponseRedirect('/')
        else:
            messages.add_message(request, level=messages.WARNING,message='Nombre de usuario o Contraseña Incorrectos')
    return render(request,'main/login.html')


def our_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def signup(request):
    if request.method == "POST":
        user = User(username=request.POST['inputEmail'],
                    first_name=request.POST['inputFirstName'],
                    last_name=request.POST['inputLastName'],
                    email=request.POST['inputEmail']
        )
        user.set_password(request.POST['inputPassword'])
        user.save()
        usuario = Usuario(user=user,
                          tipo=TipoUsuario.objects.get(pk=int(request.POST['inputType'])),
                          direccion=request.POST['inputAddress'],
                          telefono=request.POST['inputPhone'])
        usuario.save()
        return HttpResponseRedirect('/') ## Aquí va el url del index según urls.py, 
    return render(request, 'main/signup.html', {'temp': 1})


def new_cattle(request):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    if request.method == "POST":
        vaquita = CabezaGanado(customer_name=request.POST['inputCustomerName'],
                               peso_kg=float(request.POST['inputWeight']),
                               fecha_nacimiento=request.POST['inputBirthdate'],
                               tipo=TipoGanado.objects.get(pk=int(request.POST['inputType'])),
                               raza=RazaGanado.objects.get(pk=int(request.POST['inputBreed'])))
        vaquita.save()
        associated_estate = GanadoFinca(cabeza_ganado=vaquita,
                                        finca=Finca.objects.get(pk=int(request.POST['inputEstate'])),
                                        lote=int(request.POST['inputLot']),
                                        potrero=int(request.POST['inputPaddock']))
        associated_estate.save()
    breeds = RazaGanado.objects.all()
    cow_types = TipoGanado.objects.all()
    estates = Finca.objects.all().filter(usuario=Usuario.objects.get(user=request.user))
    print(estates)
    context = {'breeds': breeds, 'cow_types': cow_types, 'estates': estates}
    return render(request, 'main/new_cattle.html', context)


def new_estate(request):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    if request.method == "POST":
        finca = Finca(usuario=Usuario.objects.get(user=request.user),
                      nombre_finca=request.POST["inputEstateName"],
                      direccion=request.POST["inputAddress"],
                      telefono=request.POST["inputPhone"],
                      direccion_encargado=request.POST["inputStewardAddress"]
                      )
        finca.save()
    context = {'temp': 1}
    return render(request, 'main/new_estate.html', context)


def view_estate(request, estate_id):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    finca = Finca.objects.get(usuario=Usuario.objects.get(user=request.user), pk=estate_id)
    vaquitas = GanadoFinca.objects.all().filter(finca=estate_id)
    context = {"finca": finca, "vaquitas": vaquitas}
    return render(request, 'main/view_estate.html', context)


def my_estates(request):
    estates = Finca.objects.all().filter(usuario=Usuario.objects.get(user=request.user))
    context = {'estates': estates}
    return render(request, 'main/my_estates.html', context)


def buscar_vacas(request):
    razas = request.POST.get('raza')
    ganado=CabezaGanado.objects.filter(raza=razas)
    # ganado=CabezaGanado.objects.all()
    return render(request,"main/busqueda.html",{"vacas":ganado})


def actualizar(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            request.user.first_name=request.POST['inputFirstName']
            request.user.last_name=request.POST['inputLastName']
            request.user.set_password(request.POST['inputPassword'])
            request.user.save()
            usuario=Usuario.objects.get(user=request.user)
            usuario.direccion=request.POST['inputAddress']
            usuario.tipo=TipoUsuario.objects.get(pk=int(request.POST['inputType']))
            usuario.telefono=request.POST['inputPhone']
            usuario.save()
            return HttpResponseRedirect('/') ## Aquí va el url del index según urls.py, 
    context = {'user':request.user,'usuario':Usuario.objects.get(user=request.user)}    
    return render(request, 'main/actualizar.html',context)


def cattle_info(request):
    return HttpResponseRedirect('/')
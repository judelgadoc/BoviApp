from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context = {'user':request.user,'usuario':Usuario.objects.get(user=request.user),'breeds':RazaGanado.objects.all()}
    else:
        context = {'user':request.user}
    return render(request, 'main/index.html', context) 
    

def our_login(request):
    if request.user.is_authenticated:
        # Si ya inició sesión, redirigir al index
        return HttpResponseRedirect('/')
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
    if request.user.is_authenticated:
        # Si ya inició sesión, redirigir al index
        return HttpResponseRedirect('/')
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
    context = {'breeds': breeds, 'cow_types': cow_types, 'estates': estates}
    return render(request, 'main/new_cattle.html', context)


def new_estate(request):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    if request.method == "POST":
        print(request.POST)
        finca = Finca(usuario=Usuario.objects.get(user=request.user),
                      nombre_finca=request.POST["inputEstateName"],
                      direccion=request.POST["inputAddress"],
                      telefono=request.POST["inputPhone"],
                      direccion_encargado=request.POST["inputStewardAddress"]
                      )
        finca.save()
    context = {'user':request.user, 'usuario':Usuario.objects.get(user=request.user)}
    return render(request, 'main/new_estate.html', context)


def view_estate(request, estate_id):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    finca = Finca.objects.get(usuario=Usuario.objects.get(user=request.user), pk=estate_id)
    vaquitas = GanadoFinca.objects.all().filter(finca=estate_id)
    context = {"finca": finca, "vaquitas": vaquitas, 'user':request.user, 'usuario':Usuario.objects.get(user=request.user)}
    return render(request, 'main/view_estate.html', context)


def cattle_info(request, cattle_id=5):
    lista_contexto = []
    cabeza_de_ganado = CabezaGanado.objects.get(id=cattle_id)
    owner = GanadoFinca.objects.get(cabeza_ganado=cabeza_de_ganado).finca.usuario
    context = {
        "datos_vaca" : cabeza_de_ganado,
        "nombre_raza" : cabeza_de_ganado.raza.nombre_raza,
        "tipo_ganado" : cabeza_de_ganado.tipo.nombre_tipo,
        "owner": owner,
        "owner_fullname": owner.user.get_full_name(),
        'user':request.user,
        'usuario':Usuario.objects.get(user=request.user)
    }
    return render(request, "main/cattle_info.html", context)


def my_estates(request):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    estates = Finca.objects.all().filter(usuario=Usuario.objects.get(user=request.user))
    context = {'estates': estates, 'user':request.user, 'usuario':Usuario.objects.get(user=request.user)}
    return render(request, 'main/my_estates.html', context)


def buscar_vacas(request):
    razas = request.POST.get('raza')
    ganado=CabezaGanado.objects.filter(raza=razas)
    context = {"vacas":ganado,'user':request.user, 'usuario':Usuario.objects.get(user=request.user)}
    return render(request,"main/busqueda.html",context)


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


def update_cattle(request, cattle_id):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    vaquita = CabezaGanado.objects.get(pk=cattle_id)
    breeds = RazaGanado.objects.all()
    cow_types = TipoGanado.objects.all()
    estates = Finca.objects.all().filter(usuario=Usuario.objects.get(user=request.user))
    associated_estate = GanadoFinca.objects.get(cabeza_ganado=vaquita)
    if request.method == "POST":
        vaquita.customer_name = request.POST['inputCustomerName']
        vaquita.peso_kg = float(request.POST['inputWeight'])
        vaquita.fecha_nacimiento = request.POST['inputBirthdate']
        vaquita.tipo = TipoGanado.objects.get(pk=int(request.POST['inputType']))
        vaquita.raza = RazaGanado.objects.get(pk=int(request.POST['inputBreed']))
        associated_estate.delete()
        associated_estate = GanadoFinca(cabeza_ganado=vaquita,
                                        finca=Finca.objects.get(pk=int(request.POST['inputEstate'])),
                                        lote=int(request.POST['inputLot']),
                                        potrero=int(request.POST['inputPaddock']))
        vaquita.save()
        associated_estate.save()
        return HttpResponseRedirect('/cattle_info/%s' % cattle_id)
    context = {"vaquita": vaquita, 
    'breeds': breeds, 
    'cow_types': cow_types, 
    'estates': estates, 
    'birthdate': str(vaquita.fecha_nacimiento),
    'associated_estate': associated_estate}
    return render(request, 'main/update_cattle.html',context)


def update_estate(request, estate_id):
    if not request.user.is_authenticated or Usuario.objects.get(user=request.user).tipo != TipoUsuario.objects.get(pk=1):
        # Si no inició sesión o inició como un no-ganadero, redirigir al index
        return HttpResponseRedirect('/')
    estate = Finca.objects.get(pk=estate_id)
    if request.method == "POST":
        print(request.POST)
        estate.nombre_finca=request.POST["inputEstateName"]
        estate.direccion=request.POST["inputAddress"]
        estate.telefono=request.POST["inputPhone"]
        estate.direccion_encargado=request.POST["inputStewardAddress"]
        estate.save()
        return HttpResponseRedirect('/view_estate/%s' % estate_id)
    context = {"estate": estate}
    return render(request, 'main/update_estate.html', context)


def password_reset(request):
    if request.method == "POST":
        email = request.POST["inputEmail"]
        associated_users = User.objects.filter(username=email)
        if associated_users.exists():
            user = associated_users[0]
            subject = 'Recuperar contraseña'
            email_template_name = "main/password_reset_email.txt"
            c = {
                "email": email,
                "domain": settings.ALLOWED_HOSTS[0],
                "site_name": "BoviApp",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
                "protocol": "http"
            }
            email_to_send = render_to_string(email_template_name, c)
            send_mail(subject, email_to_send, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        return HttpResponseRedirect('/')
    context = {"temp": 1}
    return render(request, 'main/password_reset.html', context)


def password_reset_confirm(request, uidb64, token):
    context = {"uid": uidb64, "token": token}
    if request.method == "POST":
        user_pk = int(force_str(urlsafe_base64_decode(uidb64)))
        user = User.objects.get(pk=user_pk)
        user.set_password(request.POST['inputPassword'])
        user.save()
        return HttpResponseRedirect('/')
    return render(request, 'main/password_reset_confirm.html', context)
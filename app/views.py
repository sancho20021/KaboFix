from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.db import models
from django.contrib.auth.models import User

from app.models import Claim
from django.template.defaulttags import register


@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]


def indexRender(request, isAll):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='moders').exists():
            return redirect('/new')
        if request.method == 'GET':
            if isAll:
                claims = Claim.objects.all()
            else:
                claims = Claim.objects.filter(user=request.user)
            statusRus = dict()
            statusRus['new'] = 'На рассмотрении'
            statusRus['processed'] = 'В работе'
            statusRus['finished'] = 'Выполнена'
            return render(request, "index.html",
                          {'claims': claims, 'username': request.user.username, 'statusRus': statusRus, 'isAll': isAll})
        if request.method == 'POST':
            return redirect('/makeClaim')
    else:
        return redirect('/login')


def indexMy(request):
    return indexRender(request, False)


def indexAll(request):
    return indexRender(request, True)


def indexModerRender(request, status):
    if request.user.is_authenticated and request.user.groups.filter(name='moders').exists():
        if request.method == 'GET':
            claims = Claim.objects.all()
            if status == 'new':
                claims = Claim.objects.filter(status=status)
            if status == 'finished' or status == 'processed':
                claims = Claim.objects.filter(status=status, moder=request.user)
            section = status
            statusRus = dict()
            statusRus['new'] = 'На рассмотрении'
            statusRus['processed'] = 'В работе'
            statusRus['finished'] = 'Выполнена'
            return render(request, "indexModer.html",
                          {'claims': claims, 'username': request.user.username, 'section': section,
                           'statusRus': statusRus})
        if request.method == 'POST':
            claim = Claim.objects.get(pk=request.POST['claimId'])
            claim.moder = request.user
            if 'take' in request.POST:
                claim.status = 'processed'
            if 'finish' in request.POST:
                claim.status = 'finished'
            if 'open' in request.POST:
                claim.status = 'new'
            claim.save()
            return redirect(request.path_info)
    else:
        return redirect('/login')


def indexModerNew(request):
    return indexModerRender(request, 'new')


def indexModerProcessed(request):
    return indexModerRender(request, 'processed')


def indexModerFinished(request):
    return indexModerRender(request, 'finished')


def indexModerAll(request):
    return indexModerRender(request, 'all')


def makeClaim(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'makeClaim.html')
        if request.method == 'POST':
            claim = Claim()
            claim.user = request.user

            claim.name = request.POST.get('name', '')
            claim.house = request.POST.get('house', '')
            claim.text = request.POST.get('text', '')
            claim.status = 'new'
            if claim.house == '' or claim.name == '' or claim.text == '':
                return HttpResponse("Заполните все поля")
            claim.save()
            return redirect('/')
    else:
        return redirect('/login')


def loginPage(request):
    if request.method == 'GET':
        return render(request, 'loginPage.html')
    if request.method == 'POST':
        username = request.POST.get('login', '')
        password = request.POST.get('password', '')

        if username == '' or password == '':
            return HttpResponse("Заполните все поля")

        # проверяем правильность логина и пароля
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return HttpResponse("Логин или пароль неверен")


def register(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'register.html')
    if request.method == 'POST':
        username = request.POST.get('login', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if username == '' or email == '' or password == '':
            return HttpResponse("Введите все поля")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Логин занят")
        user = User.objects.create_user(username, email, password)
        user.save()
        login(request, user)
        return redirect('/')


def logout_page(request):
    logout(request)
    return redirect('/login')

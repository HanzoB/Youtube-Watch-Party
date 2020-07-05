import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import uuid
import random





def room(request,room):
    room_name = request.get_full_path().split('m/')[1]
    context = {'room_name': room_name}
    return render(request, 'index.html', context)


    context = {"username": username,"room_name": room_name}
    return render(request, 'index.html', context)


def homepage(request):
    return render(request, 'homepage.html')


def redirect_to_room(request):
    room_url = uuid.uuid4()
    return redirect("/room/" + str(room_url))




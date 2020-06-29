import requests
from django.shortcuts import render, redirect
from .models import Gen_room
from django.http import HttpResponse
from django.urls import reverse
from django.db import models
import uuid




def room(request,room):

    Room_ID = request.get_full_path().split("m/")[1]
    context = {'room_id': Room_ID}
    return render(request, 'index.html', context)


def homepage(request):
    return render(request, 'homepage.html')


def redirect_to_room(request):
    room_url = uuid.uuid4()
    return redirect("/room/" + str(room_url))




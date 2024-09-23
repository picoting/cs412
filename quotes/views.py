from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random

# Create your views here.

quotes = [
    "I sleep. I dream. I make up things that I would never say. I say them very quietly.",
    "A man takes his sadness down to the river and throws it in the river, but then he’s still left with the river. A man takes his sadness and throws it away, but he’s still left with his hands.",
    "You wanted to prove something, you wanted to start a war in my body, a revolution. I’m not brave anymore, darling. I’m not brave anymore.", 
]

images = [
    "quotes/images/siken-1.jpg",
    "quotes/images/siken-2.jpg",
    "quotes/images/siken-3.jpg"
]

def home(request):
    #select random quote
    random_quote = random.choice(quotes)

    #select random image
    random_image = random.choice(images)


    #time = time.ctime()

    return render(request, 'quotes/home.html', {'quote': random_quote, 'image': random_image, 'current_time': time.ctime()})
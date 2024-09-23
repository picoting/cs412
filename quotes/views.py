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

def show_all(request):
    quote_image_pairs = zip(quotes, images)
    return render(request, 'quotes/show_all.html', {'quote_image_pairs': quote_image_pairs, 'current_time': time.ctime()})

def about(request):
    person_info = {
        "name": "Richard Siken",
        "biography": """
        Richard Siken is an American poet, painter, and filmmaker. His poetry collection "Crush" won the 2004 Yale Series of Younger Poets competition, 
        and his work explores themes of love, obsession, and loss. His poems are known for their raw intensity and emotional depth.
        """
    }
    creator_info = {
        "name": "Ting Liu",
        "note": "Richard Siken is my favorite poet! I wanted to share some of his work with everyone :)"
    }
    return render(request, 'quotes/about.html', {'person_info': person_info, 'creator_info': creator_info, 'current_time': time.ctime()})

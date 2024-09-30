from django.shortcuts import render

import random

# Create your views here.

def main(request):
    restaurant_info = {
        'name': 'gufo',
        'address': '660 Cambridge St, Cambridge, MA 02141',
        'description': 'Gufo, a modern Italian restaurant from Boston’s Coda Restaurant Group (SRV, The Salty Pig, Gufo, Baleia). Located at 660 Cambridge Street in East Cambridge, Gufo (Italian for “owl”) offers weekday lunch, weekend brunch and nightly dinner service filled with warm hospitality, a charming ambiance, and a modern take on Italian cuisine coupled with a thoughtful and fun beverage program.',
        'brunch': 'Sat-Sun: 11:00 AM - 3 PM',
        'lunch': 'Mon-Fri: 11:00 AM - 3 PM',
        'din': 'Mon-Sun: 5:00 PM - 9:30 PM'
    }
    return render(request, 'restaurant/main.html', {'restaurant_info': restaurant_info})


def order(request):
    menu_items = [
        {'name': 'small plates', 'price': 6, 'description': 'select one!' ,'options': ['marinated castelvetrano olives', 'taleggio with fermented blueberry honey', 'white anchovies with aleppo + fennel pollen']},
        {'name': 'pasta', 'price': 23, 'description': 'mafaldine, roasted pepper pesto, smoked cultured cream, pine nuts'},
        {'name': 'bowl', 'price': 14, 'description': 'lettuces, fennel, olive, cara cara oranges, ricotta salata, walnut, roasted onion dressing'},
        {'name': 'pizza', 'price': 21, 'description': 'baby clams, tomato, oregano, fried garlic, chili'}
    ]

    daily_specials = [
        {'name': 'sandwich', 'price': 15, 'description': 'peperonata, mozzarella, garlic + chili, basil, arugula'},
        {'name': 'veg plate', 'price': 18, 'description': 'oyster mushrooms, meyer lemon, basil, peas, cured egg yolk'},
        {'name': 'plate', 'price': 37, 'description': 'lamb shank, cherry agrodolce, pistachio dukkah, chickpea polenta, herbs'}
    ]

    daily_special = random.choice(daily_specials)

    return render(request, 'restaurant/order.html', {'menu_items': menu_items, 'daily_special': daily_special})

def confirmation(request):

        if request.method == 'POST':

            menu_prices = {
                'small plates': 6,
                'pasta': 23,
                'bowl': 14,
                'pizza': 21,
                'sandwich': 15,
                'veg plate': 18,
                'plate': 37
            }

            selected_items = request.POST.getlist('items')
            daily_special = request.POST.get('daily_special')

            total_cost = 0
            items_with_prices = []

            for item in selected_items:
                if item in menu_prices:
                    item_price = menu_prices[item]
                    items_with_prices.append({'name': item, 'price': item_price})
                    total_cost += item_price

            if daily_special:
                daily_special_price = menu_prices[daily_special]
                items_with_prices.append({'name': 'SPECIAL: '+ daily_special, 'price': daily_special_price})
                total_cost += daily_special_price

            return render(request, 'restaurant/confirmation.html', {
                'items_with_prices': items_with_prices,
                'total_cost': total_cost
            })
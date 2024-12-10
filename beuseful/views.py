"""
Ting Liu
tinglliu@bu.edu
views for buseful
""" 
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Avg
from math import floor
from django.core.exceptions import PermissionDenied

from .models import Profile, Service, Order
from .forms import *

from django.http import HttpResponse


# PROFILE VIEWS
class ProfileListView(ListView):
    """
    list of all the existing profiles
    """
    model = Profile
    template_name = 'beuseful/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        queryset = Profile.objects.exclude(username='')
        print("Profiles in queryset:", [profile.username for profile in queryset])
        return queryset



class ProfileDetailView(DetailView):
    """
    detailed view of a specific profile
    """
    model = Profile
    template_name = "beuseful/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if not username: #i was getting an issue w reverse for empty username
            raise ValueError("The 'username' parameter is missing.")
        return get_object_or_404(Profile, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        user_profile = self.request.user.profile if self.request.user.is_authenticated else None

        context['is_own_profile'] = user_profile == profile #you can only view your own follower/following lists

        context['is_following'] = ( #check if logged in user follows the profile
            user_profile.following.filter(id=profile.id).exists()
            if user_profile and user_profile != profile
            else False
        )

        # seller average off of reviews (if they are a seller )
        seller_reviews = profile.received_reviews.filter(order__service__seller=profile)
        seller_avg_rating = seller_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # buyer average (all profiles have this)
        buyer_reviews = profile.received_reviews.filter(order__buyer=profile)
        buyer_avg_rating = buyer_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # add the number of stars that need to filled out of 5 for the rating lol
        context['seller_avg_rating'] = seller_avg_rating
        context['seller_filled_stars'] = range(floor(seller_avg_rating))  # filled
        context['seller_empty_stars'] = range(5 - floor(seller_avg_rating))  # empty

        #same thing for buyer
        context['buyer_avg_rating'] = buyer_avg_rating
        context['buyer_filled_stars'] = range(floor(buyer_avg_rating))
        context['buyer_empty_stars'] = range(5 - floor(buyer_avg_rating))

        context['seller_reviews'] = seller_reviews
        context['buyer_reviews'] = buyer_reviews

        return context


class CreateProfileView(CreateView):
    """
    view for making a new profile
    """
    model = Profile
    form_class = CreateProfileForm
    template_name = 'beuseful/create_profile_form.html'

    def get_success_url(self):
        return reverse('activity_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        user_form = UserCreationForm(self.request.POST) #take the user create form
        profile_form = self.form_class(data=self.request.POST, files=self.request.FILES)

        print("FILES Received:", self.request.FILES)  # Debug request.FILES

        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            print("User Form Errors:", user_form.errors)
            print("Profile Form Errors:", profile_form.errors)
            return self.form_invalid(user_form, profile_form)

    def form_valid(self, user_form, profile_form):
        user = user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.username = user.username #profile username is the same as user username (1-to-1)
        if 'profile_picture' in self.request.FILES:
            profile.profile_picture = self.request.FILES['profile_picture']  # explicitly save the file? dk if i need this but
        profile.save()
        login(self.request, user)
        return super().form_valid(profile_form)

    def form_invalid(self, user_form, profile_form):
        context = self.get_context_data()
        context['user_form'] = user_form
        context['form'] = profile_form
        return self.render_to_response(context)

#follower/following views
def toggle_follow(request, username):
    target_profile = get_object_or_404(Profile, username=username)

    if request.user.profile == target_profile:
        # prevent users from following themselves
        return redirect('profile_detail', username=username)

    if target_profile.followers.filter(id=request.user.profile.id).exists():
        # have the unfollow for following
        target_profile.followers.remove(request.user.profile)
    else:
        # follow option for followers that you dont follow
        target_profile.followers.add(request.user.profile)

    # go back to profile view
    return redirect('profile_detail', username=username)

class FollowerListView(ListView):
    """
    view to show followers
    """
    model = Profile
    template_name = "beuseful/follower_list.html"
    context_object_name = "followers"

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(Profile, username=username)
        
        # only allow the logged-in user to view their own followers
        if profile != self.request.user.profile:
            raise PermissionDenied("You are not authorized to view this page.")
        
        return profile.followers.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile  # current logged in user

        # list of their followers
        followers = self.get_queryset()
        follower_data = [
            {
                'follower': follower,
                'is_following': profile.following.filter(id=follower.id).exists()
            }
            for follower in followers
        ]

        context['profile'] = profile
        context['follower_data'] = follower_data
        return context

class FollowingListView(ListView):
    """
    view to show following
    """
    model = Profile
    template_name = "beuseful/following_list.html"
    context_object_name = "following"

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(Profile, username=username)
        if profile != self.request.user.profile:
            raise PermissionDenied("You can only view your own following list.")
        return profile.following.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context

# SERVICE VIEWS
class CreateServiceView(CreateView):
    """
    view for seller to create a new service
    """
    model = Service
    form_class = CreateServiceForm
    template_name = 'beuseful/create_service.html'

    def form_valid(self, form):
        service = form.save(commit=False)
        if not hasattr(self.request.user, 'profile'):
            raise ValueError("Logged-in user does not have an associated profile.")
        service.seller = self.request.user.profile
        service.save()
        return super().form_valid(form)

    def get_success_url(self):
        if not hasattr(self.request.user, 'profile') or not self.request.user.profile.username:
            raise ValueError("Logged-in user does not have an associated profile or a valid username.")
        return reverse_lazy('profile_detail', kwargs={'username': self.request.user.profile.username})

#browsing service view
def browse_services(request):
    # get category filter from query parameters
    category_filter = request.GET.get('category', None)
    
    # fetch all services or filter by category
    if category_filter:
        services = Service.objects.filter(category=category_filter).order_by('-id')  # sort by time (newest first)
    else:
        services = Service.objects.all().order_by('-id')  # default sort by time
    
    # pass categories to template for filtering options
    categories = dict(Service.CATEGORY_CHOICES)

    return render(request, 'beuseful/browse_services.html', {
        'services': services,
        'categories': categories,
        'selected_category': category_filter,  # keep track of current filter
    })

# ORDER VIEWS
def place_order(request, service_id):
    """
    view for buyer to place a new order
    """
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == "POST":
        form = CreateOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.service = service
            order.seller = service.seller
            order.buyer = request.user.profile
            order.save()
            messages.success(request, "Your order has been placed!")
            return redirect('profile_detail', username=service.seller.username)
    else:
        form = CreateOrderForm()
    
    return render(request, 'beuseful/place_order.html', {'form': form, 'service': service})


def manage_orders(request):
    """
    view for sellers to see/manage all of their recieved orders
    """
    orders = Order.objects.filter(seller=request.user.profile)

    # add a flag to check if the seller has reviewed the order
    for order in orders:
        seller_has_reviewed = order.reviews.filter(reviewer=request.user.profile).exists()
        order.seller_has_reviewed = seller_has_reviewed  # Attach the flag to the order object

    return render(request, 'beuseful/manage_orders.html', {'orders': orders})


def update_order_status(request, order_id):
    """
    seller can update the status of a single order
    """
    order = get_object_or_404(Order, id=order_id, seller=request.user.profile)
    
    if request.method == "POST":
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated!")
            return redirect('manage_orders')
    else:
        form = OrderUpdateForm(instance=order)
    
    return render(request, 'beuseful/update_order_status.html', {'form': form, 'order': order})

#@login_required
def my_orders(request):
    """
    view for buyer to see tthe status of all their placed orders
    """
    orders = Order.objects.filter(buyer=request.user.profile)

    # add a flag for each order to check if the user has left a review
    for order in orders:
        user_has_reviewed = order.reviews.filter(reviewer=request.user.profile).exists()
        order.user_has_reviewed = user_has_reviewed  # Attach the flag to the order object

    return render(request, 'beuseful/my_orders.html', {'orders': orders})


def leave_review(request, order_id):
    """
    view for either party to leave a review regarding an order
    """
    order = get_object_or_404(Order, id=order_id)

    # ensure the order is completed
    if order.status != "Completed":
        messages.error(request, "You can only leave a review for completed orders.")
        return redirect('my_orders')

    # ensure the logged-in user is the buyer or seller of the order
    if request.user.profile not in [order.buyer, order.service.seller]:
        messages.error(request, "You are not authorized to review this order.")
        return redirect('my_orders')

    # prevent duplicate reviews for the same order and user
    existing_review = Review.objects.filter(order=order, reviewer=request.user.profile).first()
    if existing_review:
        messages.error(request, "You have already left a review for this order.")
        return redirect('my_orders')

    if request.method == "POST":
        form = CreateReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.reviewer = request.user.profile
            # Set the reviewee (opposite of the reviewer)
            review.reviewee = order.service.seller if request.user.profile == order.buyer else order.buyer
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('my_orders')
    else:
        form = CreateReviewForm()

    return render(request, 'beuseful/leave_review.html', {'form': form, 'order': order})

# DEFAULT VIEW
class DefaultView(TemplateView):
    """
    default view for non oauth-ed users... redirects to my activty for logged in users
    """
    template_name = 'beuseful/default.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('activity_page')
        return super().get(request, *args, **kwargs)


# CUSTOM LOGOUT VIEW
class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']

#ABOUT PAGE VIEW
class AboutPageView(TemplateView):
    template_name = "beuseful/about.html"

#ORDERS VIEWS/CLASSES
class MyOrdersView(ListView):
    """
    view for getting the list of orders a buyer as made
    """
    model = Order
    template_name = 'beuseful/my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # fetch orders where the logged-in user is the buyer
        return Order.objects.filter(buyer=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()

        # add a flag to each order indicating if the user has left a review
        for order in orders:
            order.user_has_reviewed = order.reviews.filter(reviewer=self.request.user.profile).exists()

        context['orders'] = orders
        return context
    
class ManageOrdersView(ListView):
    """
    view for getting the list of orders a seller has recieved
    """
    model = Order
    template_name = 'beuseful/manage_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # fetch orders for the services provided by the logged-in seller
        return Order.objects.filter(service__seller=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()

        # add a flag to each order indicating if the seller has left a review
        for order in orders:
            order.user_has_reviewed = order.reviews.filter(reviewer=self.request.user.profile).exists()

        context['orders'] = orders
        return context

#REVIEW VIEWS
class ViewReview(DetailView):
    """
    view for clicking into a reviewed order and seeing the order detail + reviews left
    """
    model = Order
    template_name = "beuseful/view_review.html"
    context_object_name = "order"

    def dispatch(self, request, *args, **kwargs):
        print(f"Accessing ViewReview: {request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'  ])
        print(f"Retrieved Order: {order}")
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        # fetch the review for this order 
        review = order.reviews.first()
        context['review'] = review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        # fetch reviews
        buyer_to_seller_review = order.reviews.filter(reviewer=order.buyer).first()
        seller_to_buyer_review = order.reviews.filter(reviewer=order.seller).first()

        context['buyer_to_seller_review'] = buyer_to_seller_review
        context['seller_to_buyer_review'] = seller_to_buyer_review
        return context

#dashboard view
def activity_page(request):
    """
    view for personal activity page
    """
    user_profile = request.user.profile

    # fetch recent orders (limit to 5 for brevity)
    recent_orders = Order.objects.filter(buyer=user_profile).order_by('-date_ordered')[:5]

    # fetch recent reviews written by the user
    recent_reviews = Review.objects.filter(reviewer=user_profile).order_by('-date')[:5]

    # fetch user's services if they are a seller
    services = user_profile.services.all() if user_profile.is_seller else None

    # get average rating if the user is a seller
    avg_rating = None
    if user_profile.is_seller:
        avg_rating = Review.objects.filter(reviewee=user_profile).aggregate(Avg('rating'))['rating__avg']

    context = {
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'services': services,
        'avg_rating': avg_rating,
        'is_seller': user_profile.is_seller,
    }
    return render(request, 'beuseful/activity_page.html', context)

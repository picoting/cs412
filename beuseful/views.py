from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Avg
from math import floor
from django.http import JsonResponse

from .models import Profile, Service, Order
from .forms import *


# PROFILE VIEWS
class ProfileListView(ListView):
    model = Profile
    template_name = 'beuseful/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        queryset = Profile.objects.exclude(username='')
        print("Profiles in queryset:", [profile.username for profile in queryset])
        return queryset



class ProfileDetailView(DetailView):
    model = Profile
    template_name = "beuseful/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if not username:
            raise ValueError("The 'username' parameter is missing.")
        return get_object_or_404(Profile, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        user_profile = self.request.user.profile if self.request.user.is_authenticated else None

        context['is_own_profile'] = user_profile == profile

        context['is_following'] = (
            user_profile.following.filter(id=profile.id).exists()
            if user_profile and user_profile != profile
            else False
        )

        # Calculate Seller Average Rating (if they are a seller)
        seller_reviews = profile.received_reviews.filter(order__service__seller=profile)
        seller_avg_rating = seller_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Calculate Buyer Average Rating
        buyer_reviews = profile.received_reviews.filter(order__buyer=profile)
        buyer_avg_rating = buyer_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Add star information to the context
        context['seller_avg_rating'] = seller_avg_rating
        context['seller_filled_stars'] = range(floor(seller_avg_rating))  # Whole stars
        context['seller_empty_stars'] = range(5 - floor(seller_avg_rating))  # Remaining stars

        context['buyer_avg_rating'] = buyer_avg_rating
        context['buyer_filled_stars'] = range(floor(buyer_avg_rating))  # Whole stars
        context['buyer_empty_stars'] = range(5 - floor(buyer_avg_rating))  # Remaining stars

        context['seller_reviews'] = seller_reviews
        context['buyer_reviews'] = buyer_reviews

        return context


class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'beuseful/create_profile_form.html'

    def get_success_url(self):
        return reverse('profile_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        user_form = UserCreationForm(self.request.POST)
        profile_form = self.get_form()

        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            return self.form_invalid(user_form, profile_form)

    def form_valid(self, user_form, profile_form):
        user = user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.username = user.username
        profile.save()
        login(self.request, user)
        return super().form_valid(profile_form)

    def form_invalid(self, user_form, profile_form):
        context = self.get_context_data()
        context['user_form'] = user_form
        context['form'] = profile_form
        return self.render_to_response(context)

#follower/following vews
def toggle_follow(request, username):
    target_profile = get_object_or_404(Profile, username=username)

    if request.user.profile == target_profile:
        # Prevent users from following themselves
        return redirect('profile_detail', username=username)

    if target_profile.followers.filter(id=request.user.profile.id).exists():
        # If already following, unfollow
        target_profile.followers.remove(request.user.profile)
    else:
        # If not following, follow
        target_profile.followers.add(request.user.profile)

    # Redirect back to the profile detail view
    return redirect('profile_detail', username=username)


# SERVICE VIEWS
class CreateServiceView(CreateView):
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


# ORDER VIEWS
def place_order(request, service_id):
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
    if not request.user.profile.is_seller:
        messages.error(request, "Only sellers can manage orders.")
        return redirect('profile_list')

    orders = Order.objects.filter(seller=request.user.profile).order_by('-date_ordered')
    return render(request, 'beuseful/manage_orders.html', {'orders': orders})


def update_order_status(request, order_id):
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
    View to display all orders placed by the logged-in user (buyer).
    """
    orders = Order.objects.filter(buyer=request.user.profile).order_by('-date_ordered')
    return render(request, 'beuseful/my_orders.html', {'orders': orders})


def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Ensure the order is completed
    if order.status != "Completed":
        messages.error(request, "You can only leave a review for completed orders.")
        return redirect('my_orders')

    # Ensure the logged-in user is the buyer or seller of the order
    if request.user.profile not in [order.buyer, order.service.seller]:
        messages.error(request, "You are not authorized to review this order.")
        return redirect('my_orders')

    # Prevent duplicate reviews for the same order and user
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
    template_name = 'beuseful/default.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile_list')
        return super().get(request, *args, **kwargs)


# CUSTOM LOGOUT VIEW
class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post']

#ABOUT PAGE VIEW
class AboutPageView(TemplateView):
    template_name = "beuseful/about.html"

#ORDERS VIEWS/CLASSES
class MyOrdersView(ListView):
    model = Order
    template_name = 'beuseful/my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Fetch orders where the logged-in user is the buyer
        return Order.objects.filter(buyer=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()

        # Add a flag to each order indicating if the user has left a review
        for order in orders:
            order.user_has_reviewed = order.reviews.filter(reviewer=self.request.user.profile).exists()

        context['orders'] = orders
        return context
    
class ManageOrdersView(ListView):
    model = Order
    template_name = 'beuseful/manage_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Fetch orders for the services provided by the logged-in seller
        return Order.objects.filter(service__seller=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()

        # Add a flag to each order indicating if the seller has left a review
        for order in orders:
            order.user_has_reviewed = order.reviews.filter(reviewer=self.request.user.profile).exists()

        context['orders'] = orders
        return context

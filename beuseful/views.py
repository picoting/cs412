from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages

from .models import Profile, Service, Order
from .forms import CreateProfileForm, CreateServiceForm, CreateOrderForm, OrderUpdateForm


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
        context['is_own_profile'] = (
            self.request.user.is_authenticated
            and hasattr(self.request.user, 'profile')
            and profile == self.request.user.profile
        )
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
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login

from InventoryManagement.settings import LOW_QUANTITY
from .forms import UserRegisterForm, InventoryItemForm
from django.contrib.auth import logout
from .models import InventoryItem, Category
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.
class Index(TemplateView):
    template_name = 'inventory/index.html'

# The View give us to access to different methods based on http method
class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})
    
    def post (self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            user = authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1']
            )

            login(request, user)
            return redirect('index')
        return render(request, 'inventory/signup.html', {'form': form})
    
class LogoutView(View):
    template_name = "inventory/logout.html"

    def get(self, request):
        logout(request) 
        return render(request, self.template_name)
    
    # def post(self, request):
    #     logout(request)
    #     return render(request, self.template_name)

class Dashboard(LoginRequiredMixin, View):
    template_name = "inventory/dashboard.html"
    def get(self, request):
        items = InventoryItem.objects.filter(user=self.request.user.id).order_by('id')
        low_inventory = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte = LOW_QUANTITY  # "quantity less than or equal to" (<=)
        )
        if low_inventory.count() > 0:
            if low_inventory.count() > 1:
                messages.error(request, f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request, f'{low_inventory.count()} item have low inventory')
        
        low_inventory_ids = InventoryItem.objects.filter(
            user=self.request.user.id,
            quantity__lte = LOW_QUANTITY  # "quantity less than or equal to" (<=)
        ).values_list('id', flat=True)

        return render(request, self.template_name, {'items': items, 'low_inventory_ids': low_inventory_ids})
    
class AddInventoryItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy('dashboard')

    # this func is used in class-based views (CBVs) to pass extra data to templates.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        # to avoid valuate for user
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class EditInventoryItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy('dashboard')
    
class DeleteInventoryItem(LoginRequiredMixin, DeleteView):
	model = InventoryItem
    # will make a confirmation page here
	template_name = 'inventory/delete_item.html'
	success_url = reverse_lazy('dashboard')
	context_object_name = 'item'
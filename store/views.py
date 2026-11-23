from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView

from .models import Products, Discount, Categories

from .forms import ProductAddForm, DiscountAddForm


class StorePage(LoginRequiredMixin, UserPassesTestMixin,ListView):
    template_name = "products.html"
    model = Products
    
    
    def get_context_data(self):
        context = super().get_context_data()
        context["product_form"] = ProductAddForm()
        context["discount_form"] = DiscountAddForm()
        context["categories"] = Categories.objects.all()
        context["products"] = self.get_queryset()
        return context
    
    def get(self, request):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if request.GET.get("barcode"):
            context["products"] = context["products"].filter(barcode=request.GET.get("barcode"))
        
        if request.GET.get("cat") and request.GET.get("cat") != "all_categories":
            context["products"] = context["products"].filter(category__name=request.GET.get("cat").strip())
        
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        
        if "product_add" in request.POST:
            form = ProductAddForm(request.POST)
            if form.is_valid():
                form.save()
                form = ProductAddForm()
                
                return redirect("store:store_page") 
               
            messages.error(request, "There has been error during product creation !")
            return redirect("store:store_page")
        
        
        if "discount_add" in request.POST:
            form = DiscountAddForm(request.POST)
            if form.is_valid():
                discount = form.save(commit=False)
                discount.product_id = request.POST.get("product")
                discount.save()
                messages.success(request, "New Discount is created !")
                return redirect("store:store_page")
            
            messages.error(request, "Something went bad !")
            return redirect("store:store_page")
        
        # Update action
        if "product_update" in request.POST:
            try:
                product = Products.objects.get(id=request.POST.get("edit_product"))

                new_name = request.POST.get("product_name")
                new_barcode = request.POST.get("sku")
                new_category = Categories.objects.get(id=request.POST.get("cat"))
                new_price = request.POST.get("price")
                new_cost = request.POST.get("cost")
                new_stock_amount = request.POST.get("stock")

                product.name = new_name
                product.barcode = new_barcode
                product.category = new_category
                product.sell_price = new_price
                product.original_price = new_cost
                product.store_amount = new_stock_amount
                product.save()
                return redirect("store:store_page")
            except Exception as error:
                messages.error(request, f"{str(error)}")
                return redirect("store:store_page")
            
        
        # Delete Action
        if "delete_product" in request.POST:
            try:
                product = Products.objects.get(id=request.POST.get("delete_product"))
                product.delete()
                messages.success(request, f"Deleted {product.name} successfully !")
                return redirect("store:store_page")
            except Exception as error:
                messages.error(request, "The Product you wanted to delete is not exist !")
                return redirect("store:store_page")
        
        
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Sizning bu bo'limga kirishga ruxsatingiz yo'q!")
        return redirect("/auth/login")
    
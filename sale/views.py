from django.shortcuts import render,redirect
from datetime import datetime
# from 
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    ListView,
    View
)

from store.models import Products, Categories
from .models import Check, CheckItem, ReturnedItem

class SalePage(LoginRequiredMixin, ListView):
    template_name = "sale.html"
    model = Products
    
    def get_context_data(self):
        
        context = super().get_context_data()
        context["categories"] = Categories.objects.all()
        context["products"] = self.get_queryset()
        return context
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        
        # Filters 
        try:
            if "cat_filter" in  request.GET:
                context["products"] = context["products"].filter(category_id=request.GET.get("cat_filter"))
            elif "barcode" in request.GET:
                context["products"] = context["products"].filter(barcode=request.GET.get("barcode"))
            else:
                pass
        except Exception as error:
            messages.error(request, "UnExpected error occured !")
            
        # Check opening 
        try:
            active_check = Check.objects.get(status=False,user_id = request.user.id)
            context["open_check"] = active_check
            
            active_check.to_pay()
            
        except Check.DoesNotExist as error:
            active_check = Check.objects.create(user_id = request.user.id)
            active_check.save()
            context["open_check"] = active_check
        
        
        return render(request, self.template_name, context)
        
    
    
    def post(self, request):
        
        if "add_to_check" in request.POST:
            selected_product = Products.objects.get(barcode=request.POST.get("barcode"))
            active_check = Check.objects.get(id= request.POST.get("check"))

            found = None
            for i in active_check.check_items.all():
                if i.product.id == selected_product.id:
                    found = i
            
            if found is None:
                new_check_item = CheckItem.objects.create(
                    product = selected_product,
                    checks =active_check
                )
                selected_product.store_amount -= 1
                selected_product.save()
                new_check_item.save()
            else:
                found.product.store_amount -= 1
                found.product.save()
                found.amount += 1
                found.save()
        
        if "decrement" in request.POST:
            try:
                item = CheckItem.objects.get(id = request.POST.get("item_id"))
                if item.amount == 0 or item.amount == 1: 
                   item.delete()
                else:
                    item.product.store_amount += 1
                    item.amount -= 1
                    item.save()
                    item.product.save()
                
                return redirect("sale:sale_page") 
            except Exception as error:
                messages.error(request, "Xatolik sodir boldi , qaytadan urinib ko'ring!")

        if "increment" in request.POST:
            try:
                item = CheckItem.objects.get(id = request.POST.get("item_id"))
                
                if item.product.store_amount == item.amount:
                    messages.error(request, "Mahsulot yetarli emas !")
                else:
                    item.product.store_amount -= 1
                    item.amount += 1
                    item.save()
                    item.product.save()
                    
                return redirect("sale:sale_page") 
            except Exception as error:
                messages.error(request, "Xatolik sodir boldi , qaytadan urinib ko'ring!")
        
        if "clear" in request.POST:
            try:
                check = Check.objects.get(id = request.POST.get("check_id"))
                for item in check.check_items.all():
                    item.product.store_amount += item.amount
                    item.product.save()
                    item.delete()
                    
            except Exception as error:
                messages.error(request, "Xatolik sodir boldi , qaytadan urinib ko'ring!")

        if "sell" in request.POST:

            try:
                check = Check.objects.get(id = request.POST.get("check_id"))
                check.payment_type = request.POST.get("pay")
                check.sold = datetime.now()
                check.status = True
                check.save()
            except Exception as error:
                messages.error(request, "Xatolik sodir boldi , qaytadan urinib ko'ring!")
            
        return redirect("sale:sale_page")
            
            

class ReturnPage(LoginRequiredMixin, View):
    template_name = "return.html"
    
    def get(self, request):
        context = {}
        
        if "search_check" in request.GET:
            context["check"] = Check.objects.get(id=request.GET.get("check"))
        
        
        return render(request, self.template_name, context)
    
    
    def post(self, request):
        
        # Return logic
        if "return" in request.POST:
            items_id = request.POST.getlist("return_items")
            
            for i in items_id:
                item = CheckItem.objects.get(id = i)
                
                new_returned_item = ReturnedItem.objects.create(
                    amount = request.POST.get(f"qty-{i}"),
                    payment_type = request.POST.get("payment_type"),
                    cause = request.POST.get("reason"),
                    user_id = request.user.id,
                    checks = Check.objects.get(id = item.checks.id),
                    paroduct = Products.objects.get(id = item.product.id)
                )
                new_returned_item.save()
                
            
        return redirect("sale:return_page") 
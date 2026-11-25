from django.shortcuts import render,redirect
# from 
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    ListView
)

from store.models import Products, Categories
from .models import Check, CheckItem

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
                new_check_item.save()
            else:
                found.amount += 1
                found.save()
                
            
            
        return redirect("sale:sale_page")
            
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ecommerce.models import Product, Specification, ProductAttribute
from .models import Customer


# Create your views here.
def index(request):
    products = Product.objects.all()
    product_attributes = ProductAttribute.objects.filter()
    context = {
        'products': products
    }
    return render(request,'ecommerce/product-list.html',context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request,'ecommerce/product-details.html',context)

def shopping_cart(request):
    return render(request, 'shopping-cart.html')



@login_required
def customer_profile(request):
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, 'customer_profile.html', {'customer': customer})

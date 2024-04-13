from django.shortcuts import render
from products.models import Product, Category
# Create your views here.

def index(request):
    categories = Category.objects.all()
    categorized_products = {}
    for category in categories:
        products_in_category = Product.objects.filter(category=category)
        categorized_products[category] = products_in_category
    params = {'categorized_products': categorized_products}
    # params = {'products' : Product.objects.all()}
    return render(request, 'home/index.html', params)

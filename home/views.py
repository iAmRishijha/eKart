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

def search_product(request):
    query = request.GET.get('search')
    prods = Product.objects.all()
    result = []
    for prod in prods:
        if query in prod.product_description.lower() or query in prod.product_name.lower() or query in prod.category.category_name.lower():
            result.append(prod)
    return render(request, "home/search.html", {"products": result})

def search_category(request, slug):
    category = Category.objects.get(slug=slug)
    products_in_category = Product.objects.filter(category=category)
    print(products_in_category)
    return render(request, "home/category.html", {"products": products_in_category})

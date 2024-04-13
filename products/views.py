from django.shortcuts import render, HttpResponseRedirect
from products.models import Product, SizeVariant
from accounts.models import Cart, CartItems
# Create your views here.

def get_product(request,slug):
    user = request.user
    try:
        product = Product.objects.get(slug = slug)
        params = {"product" : product}
        if request.GET.get('size'):
            size = request.GET.get("size")
            price = product.get_product_price_by_size(size)
            params["updated_price"] = price
            params["selected_size"] = size
            
        # For updating the  value in + and - 
        # we check if the user has a cart and same item of same size is stored in cart
        # then we jus fetch the value from cart item and pass it in params 
        # else we pass 1 as deault value
        try:
            cart = Cart.objects.filter(user=user, is_paid=False).first()
            if cart is not None:
                size_variant = SizeVariant.objects.get(size = size)
                check_cart = CartItems.objects.filter(cart=cart, product=product, size=size_variant).first()
                if check_cart is not None:
                    params["quantity"] =check_cart.quantity
                else:
                    params["quantity"] = 1
            else:
                params["quantity"] = 1
        except Exception as e:
            params["quantity"] = 1

        return render(request, 'products/product.html', params)
    except Exception as e:
        print(e)

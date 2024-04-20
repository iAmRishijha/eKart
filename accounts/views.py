from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Cart, CartItems, OrderDetail, OrderUpdate
from products.models import Product, SizeVariant, ColorVariant, Coupon
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# Create your views here.



def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email","")
        password = request.POST.get("password","")

        # Checking if the given username exists and has done account verification
        user_obj = User.objects.filter(username=email)
        if not user_obj.exists():
            messages.warning(request, "Account not found")
            return HttpResponseRedirect(request.path_info)
        
        elif user_obj[0].profile.is_email_verified == False:
            messages.warning(request, "Account not verified")
            return HttpResponseRedirect(request.path_info)

        # if the user exists and account is verified then check the login credentials
        # if the user credentials are correct then login and redirect to home page
        check_user = authenticate(username=email, password=password)
        if check_user is not None:
            print(check_user.first_name)
            login(request, check_user)
            return redirect('/')
        
        messages.warning(request, "Invalid Credentials")
        return HttpResponseRedirect(request.path_info)
    
    return render(request, "accounts/login.html")

def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name","")
        last_name = request.POST.get("last_name","")
        email = request.POST.get("email","")
        password = request.POST.get("password","")

        user_obj = User.objects.filter(username=email)
        if user_obj.exists():
            messages.warning(request, "Email id is already in taken")
            return HttpResponseRedirect(request.path_info)
    
        new_user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        new_user.set_password(password)
        new_user.save()
        messages.success(request, "An Activation Email has been sent to your email")

    return render(request, "accounts/register.html")

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse("Invaid email token")


def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()

    except Exception as e:
        pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def add_to_cart(request,uid):
    variant = request.GET.get("variant")
    quantity = request.GET.get("quantity")
    product = Product.objects.get(uid = uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user = user, is_paid = False)

    # Checking if the item is already in the cart
    # if present then just updating its quantity and redirecting to current page
    check_cart = CartItems.objects.filter(cart=cart, product=product).first()
    if variant:
        size_variant = SizeVariant.objects.get(size = variant)
        check_cart = CartItems.objects.filter(cart=cart, product=product, size=size_variant).first()
    
    if check_cart:
        check_cart.quantity = int(quantity)
        check_cart.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    
    # if item is new then create cart item for it
    cart_item = CartItems.objects.create(cart = cart, product=product)
    if variant:
        variant = request.GET.get("variant")
        size_variant = SizeVariant.objects.get(size = variant)
        cart_item.size = size_variant
        cart_item.save()
    if quantity:
        quantity = request.GET.get('quantity')
        cart_item.quantity = int(quantity)
        cart_item.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required
def cart_page(request):
    try:
        cart = Cart.objects.get(is_paid = False, user = request.user )
        if request.method == "POST":
            coupon = request.POST.get('coupon')
            coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
            if not coupon_obj.exists():
                messages.warning(request, "Inavlid Coupon Code.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if cart.coupon:
                messages.warning(request,"Coupon already exists.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if cart.get_cart_total() < coupon_obj[0].minimum_amount:
                messages.warning(request,f'Minimum cart value required is {coupon_obj[0].minimum_amount} to apply this coupon')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if coupon_obj[0].is_expired:
                messages.warning(request,"Coupon expired.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            cart.coupon = coupon_obj[0]
            cart.save()
            messages.success(request, "Coupon Applied.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_total = cart.get_cart_total()
        total_price = cart_total
        try:
            if cart.get_cart_total() > cart.coupon.minimum_amount:
                total_price = cart.get_cart_total() - cart.coupon.discount_price
        except Exception:
            total_price = cart_total

        cart.order_price = total_price
        cart.save()

        cart_items = CartItems.objects.filter(cart = cart)
        params = {'cart' : cart, 'cart_items' : cart_items, 'total_price' : total_price} 
        return render(request, "accounts/cart.html", params)
    except Exception as e:
        return render(request, "accounts/cart.html")


    

def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid = cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon Removed.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def checkout(request):
    # print(request.method)
    try:
        cart = Cart.objects.get(is_paid = False, user = request.user )
        total_price = cart.order_price
        client = razorpay.Client(auth = (settings.KEY, settings.SECRET))
        payment = client.order.create({'amount': total_price*100, 'currency':'INR', 'payment_capture': '1'})
        cart.razorpay_order_id = payment['id']
        cart.save()
        params = {'payment': payment}

        if request.method == 'POST':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address1')+", "+request.POST.get("address2")
            email = request.POST.get("email")
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip = request.POST.get('zipcode')
            
            details = OrderDetail(order_id = cart.razorpay_order_id, name = name, phone = phone, address = address, email = email, city = city, state = state, zip = zip)
            details.save()
            
            return HttpResponseRedirect('http://127.0.0.1:8000/accounts/success/' + '?order_id=' + str(payment['id']))
        
        return render(request, "accounts/checkout.html", params)
    except Exception as e:
        return render(request, 'accounts/cart.html')

@csrf_exempt
def success(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razorpay_order_id = order_id)
    cart.is_paid = True
    cart.save()

    update = OrderUpdate(order_id=order_id, update_description = "Order Placed")
    update.save()
    return HttpResponse("Payment success")


@login_required
def orderhistory(request):
    cart_paid = Cart.objects.filter(user = request.user, is_paid = True).order_by('-updated_at')
    return render(request, 'accounts/orders.html',  {"paid_items" : cart_paid})


def tracker(request, order_id):
    updates = OrderUpdate.objects.filter(order_id = order_id).order_by("-updated_at")
    shipping_details = OrderDetail.objects.get(order_id = order_id)
    params = {'shipping_details': shipping_details, 'updates': updates}
    return render(request, 'accounts/tracker.html', params)

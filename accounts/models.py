from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.email import send_activation_email
from products.models import Product, ColorVariant, SizeVariant, Coupon
# Create your models here.


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_img = models.ImageField(upload_to="profile")

    def get_cart_count(self):
        cart_size = []
        cart_item = CartItems.objects.filter(cart__is_paid=False, cart__user=self.user)
        for item in cart_item:
            cart_size.append(item.quantity)
        return sum(cart_size)

    def __str__(self)->str:
        return self.user.username





@receiver(post_save, sender=User)
def send_mail_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user=instance,email_token=email_token)
            email = instance.email
            send_activation_email(email, email_token)
    except Exception as e:
        pass





class Cart(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="carts")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    order_price = models.IntegerField(default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id =models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_signature =models.CharField(max_length=100, blank=True, null=True)
    
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for cart_item in cart_items:
            itemPrice = []
            # price.append(cart_item.product.price)
            itemPrice.append(cart_item.product.price)
            if cart_item.color:
                color_variant_price = cart_item.color.price
                itemPrice.append(color_variant_price)
            if cart_item.size:
                size_variant_price = cart_item.size.price
                itemPrice.append(size_variant_price)
            price.append(sum(itemPrice)*cart_item.quantity)
        
        return sum(price)
    
    def __str__(self)->str:
        return self.user.username
    

    
class CartItems(BaseModel):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(ColorVariant,on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(SizeVariant,on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    def get_product_price(self):
        price = [self.product.price]
        if self.color:
            color_variant_price = self.color.price
            price.append(color_variant_price)
        if self.size:
            size_variant_price = self.size.price
            price.append(size_variant_price)
        return sum(price)
    
    def __str__(self) -> str:
        return self.product.product_name
    

class OrderDetail(BaseModel):
    order_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=50)
    phone = models.IntegerField()
    address = models.CharField(max_length=500)
    email = models.EmailField(max_length=500)
    city = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    zip = models.CharField(max_length=6)

class OrderUpdate(BaseModel):
    order_id = models.CharField(max_length=255, null=True, blank=True)
    update_description = models.TextField(max_length=1000)
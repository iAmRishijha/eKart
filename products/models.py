from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
# Create your models here.

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    categorty_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        return super(Category, self).save(*args,**kwargs)

    def __str__(self)->str:
        return self.category_name


class ColorVariant(BaseModel):
    color = models.CharField(max_length=50)
    price = models.IntegerField(default=0)

    def __str__(self,) -> str:
        return self.color
    
class SizeVariant(BaseModel):
    size = models.CharField(max_length=50)
    price = models.IntegerField(default=0)

    def __str__(self,) -> str:
        return self.size


class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    product_description = models.TextField()
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    color = models.ManyToManyField(ColorVariant, blank=True)
    size = models.ManyToManyField(SizeVariant, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        return super(Product, self).save(*args,**kwargs)

    def __str__(self)->str:
        return self.product_name

    def get_product_price_by_size(self, size):
        return self.price + SizeVariant.objects.get(size=size).price


class ProductImage(BaseModel):
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product')


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)
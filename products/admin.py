from django.contrib import admin
# Register your models here.

from .models import  *

admin.site.register(Category)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    model = ColorVariant

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    model = SizeVariant

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductImage)

admin.site.register(Coupon)

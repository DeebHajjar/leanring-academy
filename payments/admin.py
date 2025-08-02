from django.contrib import admin
from .models import Order, Payment, Coupon

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Coupon)

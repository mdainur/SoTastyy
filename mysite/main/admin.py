from django.contrib import admin
from .models import Food, Order, OrderItem, Address, Payment, UserProfile, Comment, Restourant


admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Food)
admin.site.register(Comment)
admin.site.register(Restourant)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(UserProfile)

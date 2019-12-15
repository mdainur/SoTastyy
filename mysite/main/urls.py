from django.urls import path, include
from . import views
from .views import (
    OrderSummaryView,
    add_to_cart,
    CheckoutView,
    IndexView,
    remove_single_item_from_cart,
    remove_from_cart,
    PaymentView,
    HistoryView,
)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('signup/', views.signup, name='signup'),
    path('restoran1/', views.res, name="res"),
    path('restoran2/', views.res2, name="res2"),
    path('restoran1/dinner/', views.din, name="din"),
    path('restoran1/breakfast/', views.bre, name="bre"),
    path('contacts/', views.contacts, name="contacts"),
    path('restoran1/lunch/', views.lun, name="lun"),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('history-orders/', HistoryView.as_view(), name='history'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('accounts/', include('django.contrib.auth.urls')),
    ]

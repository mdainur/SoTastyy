from django.utils import timezone
from .models import Food, Order, OrderItem, Address, UserProfile, Payment, Comment, Restourant
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CheckoutForm, PaymentForm
from django.conf import settings

import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def checkout(request):
    return render(request, 'main/checkout.html')


class IndexView(ListView):
    model = Food
    template_name = 'main/index.html'


def contacts(request):
    return render(request, 'main/contacts.html')


def res(request):
    rest = Restourant.objects.first()
    foods = Food.objects.filter(rest=rest)
    users = User.objects.all()
    return render(request, 'main/restoran1.html', {'foods': foods, 'users': users, 'rest': rest})


def din(request):
    txt = 'D'
    foods = Food.objects.filter(time=txt)
    users = User.objects.all()
    return render(request, 'main/restoran1.html', {'foods': foods, 'users': users})


def bre(request):
    txt = 'B'
    foods = Food.objects.filter(time=txt)
    users = User.objects.all()
    return render(request, 'main/restoran1.html', {'foods': foods, 'users': users})


def lun(request):
    txt = 'L'
    foods = Food.objects.filter(time=txt)
    users = User.objects.all()
    return render(request, 'main/restoran1.html', {'foods': foods, 'users': users})


def res2(request):
    rest = Restourant.objects.last()
    foods = Food.objects.filter(rest=rest)
    users = User.objects.all()
    return render(request, 'main/restoran2.html', {'foods': foods, 'users': users, 'rest': rest})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Food, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("order-summary")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'main/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class HistoryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'main/history.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Food, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("index", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("index", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Food, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("index", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("index", slug=slug)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, 'main/checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_phone = form.cleaned_data.get('shipping_phone')

                    if is_valid_form([shipping_address1, shipping_phone]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            phone_number=shipping_phone,
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.shipping_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "main/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, {err.get('message')})
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


# class PaymentView(View):
#     def get(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         if order.billing_address:
#             context = {
#                 'order': order,
#                 'DISPLAY_COUPON_FORM': False
#             }
#             userprofile = self.request.user.userprofile
#             if userprofile.one_click_purchasing:
#                 # fetch the users card list
#                 cards = stripe.Customer.list_sources(
#                     userprofile.stripe_customer_id,
#                     limit=3,
#                     object='card'
#                 )
#                 card_list = cards['data']
#                 if len(card_list) > 0:
#                     # update the context with the default card
#                     context.update({
#                         'card': card_list[0]
#                     })
#             return render(self.request, "main/payment.html", context)
#         else:
#             messages.warning(
#                 self.request, "You have not added a billing address")
#             return redirect("main/checkout")
#
#     def post(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         form = PaymentForm(self.request.POST)
#         userprofile = UserProfile.objects.get(user=self.request.user)
#         if form.is_valid():
#             token = form.cleaned_data.get('stripeToken')
#             save = form.cleaned_data.get('save')
#             use_default = form.cleaned_data.get('use_default')
#
#             if save:
#                 if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
#                     customer = stripe.Customer.retrieve(
#                         userprofile.stripe_customer_id)
#                     customer.sources.create(source=token)
#
#                 else:
#                     customer = stripe.Customer.create(
#                         email=self.request.user.email,
#                     )
#                     customer.sources.create(source=token)
#                     userprofile.stripe_customer_id = customer['id']
#                     userprofile.one_click_purchasing = True
#                     userprofile.save()
#
#             amount = int(order.get_total() * 100)
#
#             try:
#
#                 if use_default or save:
#                     # charge the customer because we cannot charge the token more than once
#                     charge = stripe.Charge.create(
#                         amount=amount,  # cents
#                         currency="usd",
#                         customer=userprofile.stripe_customer_id
#                     )
#                 else:
#                     # charge once off on the token
#                     charge = stripe.Charge.create(
#                         amount=amount,  # cents
#                         currency="usd",
#                         source=token
#                     )
#
#                 # create the payment
#                 payment = Payment()
#                 payment.stripe_charge_id = charge['id']
#                 payment.user = self.request.user
#                 payment.amount = order.get_total()
#                 payment.save()
#
#                 # assign the payment to the order
#
#                 order_items = order.items.all()
#                 order_items.update(ordered=True)
#                 for item in order_items:
#                     item.save()
#
#                 order.ordered = True
#                 order.payment = payment
#                 order.ref_code = create_ref_code()
#                 order.save()
#
#                 messages.success(self.request, "Your order was successful!")
#                 return redirect("/")
#
#             except stripe.error.CardError as e:
#                 body = e.json_body
#                 err = body.get('error', {})
#                 messages.warning(self.request, {err.get('message')})
#                 return redirect("/")
#
#             except stripe.error.RateLimitError as e:
#                 # Too many requests made to the API too quickly
#                 messages.warning(self.request, "Rate limit error")
#                 return redirect("/")
#
#             except stripe.error.InvalidRequestError as e:
#                 # Invalid parameters were supplied to Stripe's API
#                 print(e)
#                 messages.warning(self.request, "Invalid parameters")
#                 return redirect("/")
#
#             except stripe.error.AuthenticationError as e:
#                 # Authentication with Stripe's API failed
#                 # (maybe you changed API keys recently)
#                 messages.warning(self.request, "Not authenticated")
#                 return redirect("/")
#
#             except stripe.error.APIConnectionError as e:
#                 # Network communication with Stripe failed
#                 messages.warning(self.request, "Network error")
#                 return redirect("/")
#
#             except stripe.error.StripeError as e:
#                 # Display a very generic error to the user, and maybe send
#                 # yourself an email
#                 messages.warning(
#                     self.request, "Something went wrong. You were not charged. Please try again.")
#                 return redirect("/")
#
#             except Exception as e:
#                 # send an email to ourselves
#                 messages.warning(
#                     self.request, "A serious error occurred. We have been notifed.")
#                 return redirect("/")
#
#         messages.warning(self.request, "Invalid data received")
#         return redirect("/payment/stripe/")
#
#
# # class PaymentView(View):
# #     def get(self, *args, **kwargs):
# #         return render(self.request, "main/payment.html")
# #
# #     def post(self, *args, **kwargs):
# #         order = Order.objects.get(user=self.request.user, ordered=False)
# #         token = self.request.POST.get('stripeToken')
# #         amount = int(order.get_total() * 100)
# #         try:
# #             charge = stripe.Charge.create(
# #                 amount=amount,
# #                 currency="usd",
# #                 source=token,
# #             )
# #
# #             order.ordered = True
# #
# #             payment = Payment()
# #             payment.stripe_charge_id = charge['id']
# #             payment.user = self.request.user
# #             payment.amount = amount
# #             payment.save()
# #
# #             order.ordered = True
# #             order.payment = payment
# #             order.save()
# #
# #             messages.success(self.request, "Your order was successful!")
# #             return redirect("/")
# #
# #         except stripe.error.CardError as e:
# #             body = e.json_body
# #             err = body.get('error', {})
# #             messages.warning(self.request, {err.get('message')})
# #             return redirect("/")
# #
# #         except stripe.error.RateLimitError as e:
# #             # Too many requests made to the API too quickly
# #             messages.warning(self.request, "Rate limit error")
# #             return redirect("/")
# #
# #         except stripe.error.InvalidRequestError as e:
# #             # Invalid parameters were supplied to Stripe's API
# #             print(e)
# #             messages.warning(self.request, "Invalid parameters")
# #             return redirect("/")
# #
# #         except stripe.error.AuthenticationError as e:
# #             # Authentication with Stripe's API failed
# #             # (maybe you changed API keys recently)
# #             messages.warning(self.request, "Not authenticated")
# #             return redirect("/")
# #
# #         except stripe.error.APIConnectionError as e:
# #             # Network communication with Stripe failed
# #             messages.warning(self.request, "Network error")
# #             return redirect("/")
# #
# #         except stripe.error.StripeError as e:
# #             # Display a very generic error to the user, and maybe send
# #             # yourself an email
# #             messages.warning(
# #                 self.request, "Something went wrong. You were not charged. Please try again.")
# #             return redirect("/")
# #
# #         except Exception as e:
# #             # send an email to ourselves
# #             messages.warning(
# #                 self.request, "A serious error occurred. We have been notifed.")
# #             return redirect("/")
# #
# #             messages.warning(self.request, "Invalid data received")
# #         return redirect("/payment/stripe/")

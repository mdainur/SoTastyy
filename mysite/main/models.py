from django.conf import settings
from django.db.models.signals import post_save
from django.db import models
from django.utils import timezone
from django.shortcuts import reverse

TIME_CHOICES = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner'),
)


class Restourant(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='img/', default='NULL')
    def __str__(self):
        return self.name



class Comment(models.Model):
    text = models.CharField(max_length=200)
    author = models.CharField(max_length=20)

    def __str__(self):
        return self.author


class Food(models.Model):
    food_name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    rest = models.ForeignKey(Restourant,on_delete=models.CASCADE,blank=True, null=True)
    time = models.CharField(choices=TIME_CHOICES, max_length=2, blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    slug = models.SlugField()
    img = models.ImageField(upload_to='img/', default='NULL')

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.food_name

    def get_absolute_url(self):
        return reverse("main:index", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("main:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Food, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(default=timezone.now)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.item.food_name

    def get_total_item_price(self):
        return self.quantity * self.item.price


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    phone_number = models.IntegerField()
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)

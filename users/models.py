from django.db import models

from products.models import Product

class User(models.Model): 
    kakao_id                = models.CharField(max_length=50)
    name                    = models.CharField(max_length=50)
    email                   = models.EmailField(unique=True)
    password                = models.CharField(max_length=200)
    phone_number            = models.CharField(max_length=30, unique=True, null=True)
    personal_clearance_code = models.CharField(max_length=13, unique=True, null=True)
    address                 = models.CharField(max_length=200)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'users'


class Cart(models.Model):
    user         = models.ForeignKey("User", on_delete=models.CASCADE)
    product      = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity     = models.IntegerField()
    totoal_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "carts"


class DeliveryLocation(models.Model): 
    user         = models.ForeignKey('User', on_delete=models.CASCADE)
    receiver     = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    location     = models.CharField(max_length=200, null=True)

    class Meta: 
        db_table = 'delivery_locations'


class Like(models.Model): 
    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta: 
        db_table = 'likes'
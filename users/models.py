from ctypes import sizeof
from pyexpat import model
from django.db import models

from products.models import Product
from core.models     import TimeStampModel

class User(TimeStampModel): 
    kakao_id                = models.CharField(max_length=50)
    name                    = models.CharField(max_length=50)
    email                   = models.EmailField(unique=True)
    password                = models.CharField(max_length=200)
    phone_number            = models.CharField(max_length=30, unique=True, null=True)
    personal_clearance_code = models.CharField(max_length=13, unique=True, null=True)
    address                 = models.CharField(max_length=200)
  
    class Meta: 
        db_table = 'users'


class Cart(models.Model):
    user         = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    product      = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity     = models.IntegerField(default=1)
    size         = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "carts"


class DeliveryLocation(models.Model): 
    user        = models.ForeignKey('User', on_delete=models.CASCADE)
    post_number = models.CharField(max_length=10)
    address1    = models.CharField(max_length=200)
    address2    = models.CharField(max_length=200)

    class Meta: 
        db_table = 'delivery_locations'


class Like(models.Model): 
    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta: 
        db_table = 'likes'


class Token(models.Model):
    token = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "tokens"
from django.db       import models

from users.models    import User
from products.models import Product


class Order(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'


class OrderProduct(models.Model):
    order             = models.ForeignKey('Order', on_delete=models.CASCADE)
    product           = models.ForeignKey(Product, on_delete=models.CASCADE)
    price             = models.DecimalField(max_digits=10, decimal_places=2)
    quantity          = models.IntegerField()
    order_status      = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'order_products'


class OrderStatus(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'order_status'

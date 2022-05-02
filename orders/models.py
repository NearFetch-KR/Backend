from django.db       import models

from core.models     import TimeStampModel
from users.models    import User
from products.models import Product


class Order(TimeStampModel):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    order_status = models.ForeignKey('OrderStatus', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=150)
    
    class Meta:
        db_table = 'orders'


class OrderProduct(models.Model):  
    order             = models.ForeignKey('Order', on_delete=models.CASCADE)
    product           = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price             = models.DecimalField(max_digits=10, decimal_places=2)
    quantity          = models.IntegerField()
    
    class Meta:
        db_table = 'order_products'


class OrderStatus(models.Model):
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'order_status'




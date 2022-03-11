from django.db import models


class Product(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    brand    = models.CharField(max_length=50)
    name     = models.CharField(max_length=300)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "products"


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "categories"


class Image(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    url     = models.URLField(max_length=1000)

    class Meta:
        db_table = "images"
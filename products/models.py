from django.db import models

class Largecategory(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "large_categories"


class Mediumcategory(models.Model):
    large_category = models.ForeignKey("Largecategory", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "medium_categories"


class Smallcategory(models.Model):
    medium_category = models.ForeignKey("Mediumcategory", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "small_categories"


class Product(models.Model):
    small_category = models.ForeignKey("Smallcategory", on_delete=models.SET_NULL, null=True)
    brand    = models.CharField(max_length=50)
    name     = models.CharField(max_length=300)
    price    = models.IntegerField()
    sale_price = models.IntegerField(null=True)
    sku_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "products"


class Image(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    url     = models.URLField(max_length=1000)

    class Meta:
        db_table = "images"


class Material(models.Model):
    name     = models.CharField(max_length=300)
    product  = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "materials"


class Option(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)

    class Meta:
        db_table = 'options'



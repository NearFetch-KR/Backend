from django.db import models


class Mediumcategory(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "medium_categories"


class Smallcategory(models.Model):
    medium_category = models.ForeignKey("Mediumcategory", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "small_categories"


class Product(models.Model):
    small_category = models.ForeignKey("Smallcategory", on_delete=models.CASCADE)
    brand    = models.CharField(max_length=50)
    name     = models.CharField(max_length=300)
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
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
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "materials"


class MaterialProduct(models.Model):
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    product  = models.ForeignKey('Product', on_delete=models.CASCADE)
   
    class Meta:
        db_table = 'material_products'


class Option(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)

    class Meta:
        db_table = 'options'



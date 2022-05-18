# Generated by Django 4.0.3 on 2022-05-18 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_product_discount_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_rate',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]

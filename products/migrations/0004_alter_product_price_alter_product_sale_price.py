# Generated by Django 4.0.3 on 2022-04-25 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_largecategory_alter_product_small_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.IntegerField(null=True),
        ),
    ]

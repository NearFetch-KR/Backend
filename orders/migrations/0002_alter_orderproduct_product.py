# Generated by Django 4.0.3 on 2022-04-25 03:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_largecategory_alter_product_small_category_and_more'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product'),
        ),
    ]

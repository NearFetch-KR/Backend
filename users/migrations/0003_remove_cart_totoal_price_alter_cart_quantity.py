# Generated by Django 4.0.3 on 2022-04-22 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_personal_clearance_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='totoal_price',
        ),
        migrations.AlterField(
            model_name='cart',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]

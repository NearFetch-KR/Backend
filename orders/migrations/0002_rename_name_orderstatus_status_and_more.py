# Generated by Django 4.0.3 on 2022-04-22 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderstatus',
            old_name='name',
            new_name='status',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='order_status',
        ),
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(default='', max_length=150),
            preserve_default=False,
        ),
    ]
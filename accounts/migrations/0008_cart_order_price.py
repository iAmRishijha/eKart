# Generated by Django 5.0.1 on 2024-04-13 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_cartitems_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='order_price',
            field=models.IntegerField(default=0),
        ),
    ]

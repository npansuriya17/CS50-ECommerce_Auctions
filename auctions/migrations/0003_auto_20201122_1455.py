# Generated by Django 3.1.3 on 2020-11-22 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201122_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_listing',
            name='reference_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
# Generated by Django 3.1.3 on 2020-12-15 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20201215_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_listing',
            name='reference_image',
            field=models.ImageField(blank=True, upload_to='auctions/listingimages/'),
        ),
    ]

# Generated by Django 3.1.3 on 2020-12-15 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_auto_20201215_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction_listing',
            name='reference_image',
            field=models.ImageField(blank=True, default='auctions/listingimages/default.jpg', upload_to='auctions/listingimages/'),
        ),
    ]

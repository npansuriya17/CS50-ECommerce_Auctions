from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.utils import timezone

def valid_bid(value):
    if value <= 0:
        raise ValidationError(
            ('Your starting bid is %(value). Starting bid value must be greater than 0'),
            params={'value':value}
        )

def user_directory_path(instance, filename): 
    return 'auctions/listingimages/{0}_{1}'.format(instance.user.id, filename) 

class User(AbstractUser):
    pass

class Auction_Categories(models.Model):
    category = models.CharField(max_length=64)
    
    def __str__(self):
        return self.category

class Auction_Listing(models.Model):
    item_name = models.CharField(max_length=64)
    item_description = models.CharField(max_length=500)
    item_category = models.ForeignKey(Auction_Categories,on_delete=models.CASCADE)
    starting_bid = models.IntegerField(validators=[valid_bid])
    current_bid = models.IntegerField(validators=[valid_bid])
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    #link = models.CharField(max_length=64,default=None,blank=True,null=True)
    reference_image = models.ImageField(upload_to="auctions/listingimages/",blank=True,default="default.jpg")
    listing_time = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s' % (self.item_name, self.item_description, str(self.item_category), self.starting_bid, self.current_bid, self.user, self.isActive, self.reference_image, self.listing_time)
    
class Bids(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Auction_Listing,on_delete=models.CASCADE)
    user_bid = models.IntegerField()
    isWinner = models.BooleanField(default=False)
    
    def __str__(self):
        return '%s %s %s %s' % (str(self.user), str(self.item), self.user_bid, self.isWinner)
    
class Comments(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Auction_Listing,on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    comment_time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return '%s %s %s %s' % (str(self.user), str(self.item), self.comment, self.comment_time)
    
class Watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Auction_Listing,on_delete=models.CASCADE)
    
    def __str__(self):
        return '%s %s' % (str(self.user), str(self.item))
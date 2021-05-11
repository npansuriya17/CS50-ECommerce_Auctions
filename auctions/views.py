from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
from .models import *
from datetime import date
from django.utils import timezone


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print(user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def index(request):
    if str(request.user) == "AnonymousUser":
        current_user = None
    else:
        current_user = request.user
    return render(request, "auctions/index.html",{
        "items" : Auction_Listing.objects.all(),
        "current_user" : current_user
        })


def categories(request):
    return render(request, "auctions/categories.html", {
    "allcategories" : Auction_Categories.objects.all()
    })

def category(request,category):
    if str(request.user) == "AnonymousUser":
        current_user = None
    else:
        current_user = request.user
    return render(request, "auctions/index.html", {
    "items" : Auction_Listing.objects.filter(item_category__category=category),
    "current_user" : current_user
    })


def watchlist(request):
    item_ids = list(Watchlist.objects.filter(user=request.user).values("item"))
    item_list = []
    for item_id in item_ids:
        item_list.append(Auction_Listing.objects.get(id=int(item_id["item"])))
    
    return render(request, "auctions/watchlist.html", {
    "items" : item_list
    })
    


class CreateNewForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':25}),label="Description", max_length=200)
    starting_bid = forms.DecimalField(label="Starting-Bid",min_value=0,decimal_places=2)
    image = forms.ImageField(label="Image", required=False)

def createlisting(request):
    if request.method == "POST": 
        form = CreateNewForm(request.POST,request.FILES)
        print(request.POST)
        if form.is_valid():
            new_item = Auction_Listing()
            new_item.item_name = form.cleaned_data["name"]
            new_item.item_description = form.cleaned_data["description"]
            new_item.item_category = Auction_Categories.objects.get(id=int(request.POST.get("category")))
            new_item.starting_bid = form.cleaned_data["starting_bid"]
            new_item.current_bid = form.cleaned_data["starting_bid"]
            new_item.user = request.user
            if form.cleaned_data["image"]:
                new_item.reference_image = form.cleaned_data["image"]
            new_item.save()
            return redirect(listing, item_id=new_item.id)
        else:
            return render(request, "auctions/createlisting.html",{
            "form": form ,
            "allcategories" : Auction_Categories.objects.all()
            })
    
    return render(request, "auctions/createlisting.html",{
        "form":CreateNewForm(),
        "allcategories" : Auction_Categories.objects.all()
    })

  
def listing(request, item_id):
    #Fetch Listing Item
    listing_item = Auction_Listing.objects.get(id=int(item_id))
        
    #Get User-Bids
    userbids = Bids.objects.filter(item=listing_item).filter(user=request.user).values("user_bid").order_by('-user_bid').first()
    if userbids:
        lastbid = userbids['user_bid']
    else:
        lastbid = None
    print(lastbid)
    #Watchlist
    isWatchlisted = isWatchlistedItem(request.user,listing_item)
    
    #POST
    if request.method == "POST":
        comment = request.POST.get("textcomment")
        bidvalue = request.POST.get("textbidvalue")
        
        #COmment
        if 'btncomment' in request.POST:
            new_comment = Comments()
            new_comment.user = request.user
            new_comment.item = listing_item
            new_comment.comment = request.POST["textcomment"]
            new_comment.save()
            
        #place-bid
        if 'btnplacebid' in request.POST:
            current_bid = Auction_Listing.objects.values("current_bid").get(id=int(item_id))
            your_bid = int(request.POST["textbidvalue"])
            if current_bid["current_bid"] < your_bid:                
                bid = Bids()
                bid.user = request.user
                bid.item = listing_item
                bid.user_bid = your_bid
                bid.save()
                #update current bid in item
                listing_item.current_bid = your_bid
                listing_item.save()
                lastbid = your_bid
        
        #Add Watchlist
        if 'btnwatchlist' in request.POST:
            watchlist = Watchlist()
            watchlist.user = request.user
            watchlist.item = listing_item
            watchlist.save()
            isWatchlisted = True
        #Remove Watchlist
        if 'btnwatchlisted' in request.POST:
            Watchlist.objects.filter(user=request.user).filter(item=item_id).delete()
            isWatchlisted = False
        #Close Bid
        if 'btnclosebid' in request.POST:
            listing_item.isActive = False
            listing_item.save()
            
    return render(request, "auctions/listings.html", {
    "item" : listing_item ,
    "comments" : Comments.objects.filter(item=listing_item),
    "lastbid": lastbid ,
    "isWatchlisted": isWatchlisted ,
    "isActive": isActive(listing_item),
    "mylisting" : listing_item.user == request.user
    })

def isActive(listing_item):
    return listing_item.isActive

def isWatchlistedItem(current_user,listing_item):
    isWatchlisted = False
    item_ids = list(Watchlist.objects.filter(user=current_user).values("item"))
    for it in item_ids:
        if int(listing_item.id) == int(it["item"]):
            isWatchlisted = True
            break
    return isWatchlisted
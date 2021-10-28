from django.urls import path

from products.views import WishList, WishFlag

urlpatterns = [
    path('/wishlist', WishList.as_view()),
    path('/wishflag', WishFlag.as_view())
]
from django.urls    import path

from products.views import ProductView, BrandView, DetailProductView, WishList, WishFlag

urlpatterns = [
    path('/wishlist', WishList.as_view()),
    path('/wishflag', WishFlag.as_view()),
    path('', ProductView.as_view()),
    path('/brand', BrandView.as_view()),
    path('/<int:product_id>', DetailProductView.as_view())
]
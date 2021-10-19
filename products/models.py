from django.db   import models

from core.models import TimeStampModel

class Brand(TimeStampModel):
    name = models.CharField(max_length = 20)

    class Meta:
        db_table = 'brands'

class Product(TimeStampModel):
    brand         = models.ForeignKey('Brand', on_delete = models.CASCADE)
    name          = models.CharField(max_length = 50)
    model_number  = models.CharField(max_length = 200)
    release_price = models.PositiveIntegerField()

    class Meta:
        db_table = 'products'

class ProductSize(TimeStampModel):
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    size    = models.ForeignKey('Size', on_delete = models.CASCADE)

    class Meta:
        db_table = 'product_sizes'

class Size(TimeStampModel):
    size = models.PositiveIntegerField()

    class Meta:
        db_table = 'sizes'

class ProductImage(TimeStampModel):
    product   = models.ForeignKey('Product', on_delete = models.CASCADE, null = True)
    image_url = models.CharField(max_length = 1000)

    class Meta :
        db_table = 'product_images'

class Wishlist(TimeStampModel):
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    user    = models.ForeignKey('users.User', on_delete = models.CASCADE)

    class Meta :
        db_table = 'wishlists'
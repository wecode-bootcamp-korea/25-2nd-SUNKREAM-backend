from django.db   import models

from core.models import TimeStampModel

class BiddingStatus(TimeStampModel):
    status = models.CharField(max_length = 20)

    class Meta:
        db_table = 'bidding_status'

class BiddingPosition(TimeStampModel):
    position = models.CharField(max_length = 20)

    class Meta:
        db_table = 'bidding_positons'

class Bidding(TimeStampModel):
    user             = models.ForeignKey('users.User', on_delete = models.SET_NULL, null = True)
    bidding_status   = models.ForeignKey('BiddingStatus', on_delete = models.SET_NULL, null = True)
    bidding_position = models.ForeignKey('BiddingPosition', on_delete = models.SET_NULL, null = True)
    product_size     = models.ForeignKey('products.ProductSize', on_delete = models.CASCADE)
    price            = models.PositiveIntegerField()

    class Meta:
        db_table = 'biddings'

class OrderStatus(TimeStampModel):
    status = models.CharField(max_length = 20)

    class Meta:
        db_table = 'order_status'
    
class Order(TimeStampModel):
    order_status = models.ForeignKey('OrderStatus', on_delete = models.SET_NULL, null = True)
    bidding      = models.ForeignKey('Bidding', on_delete = models.CASCADE)
    buyer        = models.ForeignKey('users.User', on_delete = models.CASCADE, related_name = 'buyer')
    seller       = models.ForeignKey('users.User', on_delete = models.CASCADE, related_name = 'seller')

    class Meta:
        db_table = 'oders'



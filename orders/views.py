import json
from enum                        import Enum
from datetime                    import datetime
from json.decoder                import JSONDecodeError
from dateutil.relativedelta      import relativedelta

from django.views                import View
from django.http.response        import JsonResponse
from django.db                   import transaction
from django.db.models            import Q, F
from django.db.models.query      import Prefetch
from django.db.models.aggregates import Count, Min, Max

from products.models             import Product, ProductSize
from orders.models               import Bidding, Order, BiddingPosition
from orders.decorator            import query_debugger
from users.utils                 import login_decorator

class BiddingStatusId(Enum):
    ON_BIDDING = 1
    CONTRACTED = 2

class BiddingPositionId(Enum):
    BUY  = 1
    SELL = 2

class OrderStatusId(Enum):
    INSPECTION = 1
    IN_TRANSIT = 2
    DELIVERED  = 3

class InsufficientPointError(Exception):
    pass

class InvalidBiddingStatusError(Exception):
    pass

class CheckId():
    def check_product_id(product_id):
        if not Product.objects.filter(id = product_id).exists():
            raise Product.DoesNotExist

    def check_product_size_id(productsize_id):
        if not ProductSize.objects.filter(id = productsize_id).exists():
            raise ProductSize.DoesNotExist
        
    def check_bidding_id(bidding_id):
        if not Bidding.objects.filter(id = bidding_id).exists():
            raise Bidding.DoesNotExist
    
    def check_bidding_position_id(position_id):
        if not BiddingPosition.objects.filter(id = position_id).exists():
            raise BiddingPosition.DoesNotExist
    
    def check_bidding_status_id(bidding_status_id):
        if bidding_status_id == BiddingStatusId.CONTRACTED.value:
            raise InvalidBiddingStatusError

def user_point_check(user, position, bidding):
    if (position == BiddingPositionId.SELL.name and bidding.price > user.point) or (position == BiddingPositionId.BUY.name and bidding.price > bidding.user.point):
        raise InsufficientPointError

class BiddingView(View):
    @login_decorator
    @query_debugger
    def post(self, request, productsize_id, position_id):
        try:
            CheckId.check_product_size_id(productsize_id)
            CheckId.check_bidding_position_id(position_id)
        
            data  = json.loads(request.body)
            user  = request.user
            price = data['price']
            
            Bidding.objects.create(
                user                 = user,
                bidding_status_id    = BiddingStatusId.ON_BIDDING.value,
                bidding_position_id  = position_id,
                product_size_id      = productsize_id, 
                price                = price
            )

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)

        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)

        except ProductSize.DoesNotExist:
            return JsonResponse({'message' : 'PRODUCT_SIZE_DOES_NOT_EXIST'}, status = 404)

        except BiddingPosition.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_BIDDING_POSITION'}, status = 400)


    @login_decorator
    @query_debugger
    def get(self, request, productsize_id, position_id):
        try:
            CheckId.check_product_size_id(productsize_id)
            CheckId.check_bidding_position_id(position_id)
            
            user              = request.user
            sell_price_filter = (Q(bidding__bidding_position_id = BiddingPositionId.BUY.value) & Q(bidding__bidding_status_id = BiddingStatusId.ON_BIDDING.value))
            buy_price_filter  = (Q(bidding__bidding_position_id = BiddingPositionId.SELL.value) & Q(bidding__bidding_status_id = BiddingStatusId.ON_BIDDING.value))
            biddings          = Bidding.objects.filter(bidding_position_id = position_id, bidding_status_id = BiddingStatusId.ON_BIDDING.value).order_by('price' if position_id == BiddingPositionId.SELL.value else '-price')
            product_size      = ProductSize.objects.annotate(sell_price = Max('bidding__price', filter = sell_price_filter), buy_price = Min('bidding__price', filter = buy_price_filter)).\
                                select_related('size', 'product').prefetch_related(Prefetch('bidding_set', queryset = biddings)).get(id = productsize_id)

            data = {
                'product_image_url'    : product_size.product.productimage_set.first().image_url,
                'product_name'         : product_size.product.name,
                'product_brand'        : product_size.product.brand.name,
                'product_model_number' : product_size.product.model_number,
                'size'                 : product_size.size.size,
                'sell_price'           : product_size.sell_price,
                'buy_price'            : product_size.buy_price,
                'user_point'           : user.point,
                'bidding_id'           : product_size.bidding_set.first().id if product_size.bidding_set.first() else None,
                'bidding_price'        : product_size.bidding_set.first().price if product_size.bidding_set.first() else None
            }

            return JsonResponse({'data' : data}, status = 200)

        except ProductSize.DoesNotExist:    
            return JsonResponse({'message' : 'PRODUCT_SIZE_DOES_NOT_EXIST'}, status = 404)

        except ProductSize.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)
        
        except BiddingPosition.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_BIDDING_POSITION'}, status = 400)
    
class SizePriceView(View):
    @login_decorator
    @query_debugger
    def get(self, request, product_id, position_id):
        try:
            CheckId.check_product_id(product_id)             
            CheckId.check_bidding_position_id(position_id)
            
            product = Product.objects.select_related('brand').get(id = product_id)
            sizes   = ProductSize.objects.select_related('size').filter(product_id = product_id).prefetch_related(
                      Prefetch('bidding_set', queryset = Bidding.objects.filter(bidding_position_id = position_id, bidding_status_id = BiddingStatusId.ON_BIDDING.value).\
                      order_by('price' if position_id == BiddingPositionId.SELL.value else '-price')))
            
            product_info = {
                'product_image_url'    : product.productimage_set.first().image_url,
                'product_name'         : product.name,
                'product_brand'        : product.brand.name,
                'product_model_number' : product.model_number,
            }

            size_price_list = [{
                'productsize_id' : size.id,
                'size'           : size.size.size,
                'bidding_id'     : size.bidding_set.first().id if size.bidding_set.first() else None,
                'bidding_price'  : size.bidding_set.first().price if size.bidding_set.first() else None,
            } for size in sizes]

            return JsonResponse({'product_info' : product_info, 'size_price_list' : size_price_list}, status = 200)

        except Product.DoesNotExist:
            return JsonResponse({'message' : 'PRODUCT_DOES_NOT_EXIST'}, status = 404)
        
        except Product.MultipleObjectsReturned:
            return JsonResponse({'message' :  'MULTIPLE_RETURN_ERROR'}, status = 400)
        
        except BiddingPosition.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_BIDDING_POSITION'}, status = 400)

class OrderView(View):
    @login_decorator
    @query_debugger
    @transaction.atomic
    def post(self, request, bidding_id):
        try:
            CheckId.check_bidding_id(bidding_id)
            
            user              = request.user           
            bidding           = Bidding.objects.select_related('bidding_status', 'bidding_position', 'user').get(id = bidding_id)
            bidding_status_id = bidding.bidding_status_id
            position          = bidding.bidding_position.position
            
            CheckId.check_bidding_status_id(bidding_status_id)
            user_point_check(user, position,bidding)
            
            Order.objects.create(
                order_status_id = OrderStatusId.INSPECTION.value,
                bidding         = bidding,
                buyer           = bidding.user if position == BiddingPositionId.BUY.name else user, 
                seller          = bidding.user if position == BiddingPositionId.SELL.name else user
            )
            
            bidding.bidding_status_id = BiddingStatusId.CONTRACTED.value
            bidding.save()

            if position == BiddingPositionId.BUY.name:
                user.point = user.point + bidding.price
                user.save()
                bidding.user.point = bidding.user.point - bidding.price
                bidding.user.save()
            
            if position == BiddingPositionId.SELL.name:
                user.point = user.point - bidding.price
                user.save()
                bidding.user.point = bidding.user.point + bidding.price
                bidding.user.save()
               
            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except Bidding.DoesNotExist:
            return JsonResponse({'message' : 'BIDDING_DOES_NOT_EXIST'}, status = 404)

        except Bidding.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)
        
        except InvalidBiddingStatusError:
            return JsonResponse({'message' : 'INVALID_BIDDING_ID'}, status = 400)
        
        except InsufficientPointError:
            return JsonResponse({'message' : 'INSUFFICIENT_POINT'}, status = 400)

class PriceHistoryView(View):
    @query_debugger
    def get(self, request, product_id):
        try:
            CheckId.check_product_id(product_id)
            size   = request.GET.get('size')
            period = request.GET.get('period', '1y')
            sort   = request.GET.get('sort')
            limit  = int(request.GET.get('limit', 5))
            offset = int(request.GET.get('offset', 0))
            limit  = offset + limit

            sort_by = {
                'low_price'  : 'price',
                'high_price' : '-price',
                'low_size'   : 'size',
                'high_size'  : '-size',
                'recent'     : '-created_at' 
            }

            order_period = {
                '1m' : datetime.now() - relativedelta(months = 1),
                '3m' : datetime.now() - relativedelta(months = 3),
                '6m' : datetime.now() - relativedelta(months = 6),
                '1y' : datetime.now() - relativedelta(years = 1),
            }

            order_grape_filter = (Q(bidding__product_size__product_id = product_id) & Q(created_at__range = (order_period.get(period, '1y'), datetime.now())))
            order_filter       = Q(bidding__product_size__product_id = product_id)
            bidding_filter     = (Q(bidding_status_id = BiddingStatusId.ON_BIDDING.value) & Q(product_size__product_id = product_id))

            if size:
                if not ProductSize.objects.filter(product_id = product_id, size__size = size).exists():
                    return JsonResponse({'message' : 'PRODUCT_SIZE_DOES_NOT_EXIST'}, status = 404)
                
                product_size = ProductSize.objects.get(product_id = product_id, size__size = size)
                order_grape_filter.add(Q(bidding__product_size = product_size), Q.AND)
                order_filter.add(Q(bidding__product_size = product_size), Q.AND)
                bidding_filter.add(Q(product_size = product_size), Q.AND)

            order_graph   = Order.objects.select_related('bidding').filter(order_grape_filter).order_by('created_at') 
            orders        = Order.objects.annotate(price = F('bidding__price'), size = F('bidding__product_size__size__size')).select_related('bidding__product_size__size').\
                            filter(order_filter).order_by(sort_by.get(sort, '-created_at'))       
            sell_biddings = Bidding.objects.annotate(size = F('product_size__size__size')).select_related('product_size__size').\
                            filter(bidding_filter, bidding_position_id = BiddingPositionId.SELL.value).order_by(sort_by.get(sort, 'price'))
            buy_biddings  = Bidding.objects.annotate(size = F('product_size__size__size')).select_related('product_size__size').\
                            filter(bidding_filter, bidding_position_id = BiddingPositionId.BUY.value).order_by(sort_by.get(sort, '-price'))
            
            data = {
            'order_graph_data' : [{
                'id'         : order.id,
                'price'      : order.bidding.price,
                'created_at' : order.created_at.strftime('%Y-%m-%d')
            }for order in order_graph],

            'order_list' : [{
                'id'         : order.id,
                'price'      : order.bidding.price,
                'size'       : order.bidding.product_size.size.size,
                'created_at' : order.created_at.strftime('%Y-%m-%d')
            }for order in orders[offset:limit]],

            'sell_bidding_list' : [{
                'price' : sell_bidding['price'],
                'size'  : sell_bidding['size'],
                'count' : sell_bidding['price_count']
            }for sell_bidding in sell_biddings.values('price', 'size').annotate(price_count = Count('price')).distinct()[offset:limit]],

            'buy_bidding_list' : [{
                'price' : buy_bidding['price'],
                'size'  : buy_bidding['size'],
                'count' : buy_bidding['price_count']
            }for buy_bidding in buy_biddings.values('price','size').annotate(price_count = Count('price')).distinct()[offset:limit]]
            }

            return JsonResponse({'data' : data}, status = 200)
        
        except Product.DoesNotExist:
            return JsonResponse({'message' : 'PRODUCT_DOES_NOT_EXIST'}, status = 404)

        except ProductSize.DoesNotExist:
            return JsonResponse({'message' : 'PRODUCT_SIZE_DOES_NOT_EXIST'}, status = 404)
        
        except ProductSize.MultipleObjectsReturned:
            return JsonResponse({'message' : 'MULTIPLE_RETURN_ERROR'}, status = 400)

class OrderListView(View):
    @login_decorator
    @query_debugger
    def get(self, request):
        user = request.user

        buy_orders  = Order.objects.select_related('bidding__product_size__product__brand', 'bidding__product_size__size', 'order_status').\
                    filter(buyer = user).prefetch_related('bidding__product_size__product__productimage_set')

        sell_orders = Order.objects.select_related('bidding__product_size__product__brand', 'bidding__product_size__size', 'order_status').\
                    filter(seller = user).prefetch_related('bidding__product_size__product__productimage_set')

        biddings    = Bidding.objects.select_related('product_size__product__brand', 'product_size__size').\
                    filter(user = user, bidding_status_id = BiddingStatusId.ON_BIDDING.value).prefetch_related('product_size__product__productimage_set')

        buy_order_list = [{
            'product_id'        : buy_order.bidding.product_size.product.id,
            'product_image_url' : buy_order.bidding.product_size.product.productimage_set.all()[0].image_url,
            'product_name'      : buy_order.bidding.product_size.product.name,
            'product_brand'     : buy_order.bidding.product_size.product.brand.name,
            'size'              : buy_order.bidding.product_size.size.size,
            'order_status'      : buy_order.order_status.status,
        }for buy_order in buy_orders]

        sell_order_list = [{
            'product_id'        : sell_order.bidding.product_size.product.id,
            'product_image_url' : sell_order.bidding.product_size.product.productimage_set.all()[0].image_url,
            'product_name'      : sell_order.bidding.product_size.product.name,
            'product_brand'     : sell_order.bidding.product_size.product.brand.name,
            'size'              : sell_order.bidding.product_size.size.size,
            'order_status'      : sell_order.order_status.status,
        }for sell_order in sell_orders]

        buy_bidding_list = [{
            'product_id'        : buy_bidding.product_size.product.id,
            'product_image_url' : buy_bidding.product_size.product.productimage_set.all()[0].image_url,
            'product_name'      : buy_bidding.product_size.product.name,
            'product_brand'     : buy_bidding.product_size.product.brand.name,
            'size'              : buy_bidding.product_size.size.size,
        } for buy_bidding in biddings.filter(bidding_position_id = BiddingPositionId.BUY.value)]

        sell_bidding_list = [{
            'product_id'        : sell_bidding.product_size.product.id,
            'product_image_url' : sell_bidding.product_size.product.productimage_set.all()[0].image_url,
            'product_name'      : sell_bidding.product_size.product.name,
            'product_brand'     : sell_bidding.product_size.product.brand.name,
            'size'              : sell_bidding.product_size.size.size,
        } for sell_bidding in biddings.filter(bidding_position_id = BiddingPositionId.SELL.value)]

        buy_order_count       = len(buy_order_list)
        sell_order_count      = len(sell_order_list)
        buy_on_bidding_count  = len(buy_bidding_list)
        sell_on_bidding_count = len(sell_bidding_list)

        data = {
            'user_name'             : user.name,
            'user_email'            : user.email,
            'user_point'            : user.point,
            'buy_order_count'       : buy_order_count,
            'buy_order_list'        : buy_order_list,
            "sell_order_count"      : sell_order_count,
            'sell_order_list'       : sell_order_list,
            'buy_on_bidding_count'  : buy_on_bidding_count,
            'buy_bidding_list'      : buy_bidding_list,
            'sell_on_bidding_count' : sell_on_bidding_count,
            'sell_bidding_list'     : sell_bidding_list
        }
        
        return JsonResponse({'data' : data}, status = 200)

        
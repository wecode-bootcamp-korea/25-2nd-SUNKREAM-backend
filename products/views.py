import json
from json.decoder import JSONDecodeError

from django.views                   import View
from django.http                    import JsonResponse
from django.db.models.query     import Prefetch
from django.db.models               import Q
from django.db.models.aggregates    import Max, Min

from products.models    import Product, ProductImage, Brand, Wishlist
from orders.models       import Order

from users.utils  import login_decorator

class WishList(View):
    @login_decorator
    def post(self, request):
        try:
            user_id      = request.user.id
            wish_product = request.GET.get('product_id')

            if not Product.objects.filter(id = wish_product).exists():
                return JsonResponse({'message:' : 'INVALID_PRODUCT_ID'}, status = 404)

            if not Wishlist.objects.filter(user_id = user_id, product_id = wish_product).exists():
                Wishlist.objects.create(user_id = user_id, product_id = wish_product)

                wish_count = Wishlist.objects.filter(product_id = wish_product).count()

                return JsonResponse({'message' : 'WISH_CREATE_SUCCESS', 'wish_count' : wish_count}, status = 201)

            Wishlist.objects.get(user_id = user_id, product_id = wish_product).delete()
            wish_count = Wishlist.objects.filter(product_id = wish_product).count()
            return JsonResponse({'message' : 'WISH_DELETE_SUCCESS', 'wish_count' : wish_count}, status = 200)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)

    @login_decorator
    def get(self, request):
        try:
            user_id   = request.user.id
            wish_list = Wishlist.objects.filter(user_id = user_id)

            results = [{
                            'id'    : wish.product.id,
                            'brand' : wish.product.brand.name,
                            'name'  : wish.product.name,
                            'price' : wish.product.release_price,
                            'image' : [
                                        {
                                        'thumbnail' : img.image_url
                                        } for img in wish.product.productimage_set.all()[:1]
                                    ]
                            } for wish in wish_list]
            return JsonResponse({'results' : results}, status = 200)

        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)

class WishFlag(View):
    @login_decorator
    def get(self, request):
        try:
            user_id      = request.user.id
            wish_product = request.GET.get('product_id')

            if not Product.objects.filter(id = wish_product):
                return JsonResponse({'message:' : 'INVALID_PRODUCT_ID'}, status = 404)

            wish_count = Wishlist.objects.filter(product_id = wish_product).count()

            check_my_wish = True

            if not Wishlist.objects.filter(product_id = wish_product, user_id = user_id):
                check_my_wish = False

            results = {
                        'wish_count'    : wish_count,
                        'check_my_wish' : check_my_wish,
                    }
            return JsonResponse({'results' : results}, status = 200)
    
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)

class ProductView(View) :
    def get(self, request) :
        try :
            brand_id = request.GET.getlist('brand_id')
            size_id  = request.GET.getlist('size_id')
            sort     = request.GET.get('sort')
            search   = request.GET.get('search')
            start    = int(request.GET.get('start',0))
            stop     = int(request.GET.get('stop',0))
            limit    = int(request.GET.get('limit', 40))
            offset   = int(request.GET.get('offset', 0))

            sort_by  = {
                        'now_buy_price'  : '-buy_price',
                        'now_sell_price' : 'sell_price',
                        'premium'        : 'release_price',
                    }

            products_filter = Q()
            
            if brand_id :
                products_filter.add(Q(brand_id__in=brand_id), Q.AND)
            if size_id :
                products_filter.add(Q(productsize__size_id__in=size_id), Q.AND)
            if start or stop : 
                products_filter.add(Q(buy_price__range = (start, stop+1)),Q.AND)
            if search :
                products_filter.add(Q(name__icontains = search)|Q(brand__name__icontains = search), Q.AND)

            buy_price_filter  = (Q(productsize__bidding__bidding_position_id = 2) & Q(productsize__bidding__bidding_status_id = 1))
            sell_price_filter = (Q(productsize__bidding__bidding_position_id = 1) & Q(productsize__bidding__bidding_status_id = 1))

            products = Product.objects\
                                        .annotate(buy_price = Min('productsize__bidding__price', filter = buy_price_filter),
                                                sell_price = Max('productsize__bidding__price', filter = sell_price_filter))\
                                        .filter(products_filter)\
                                        .select_related('brand')\
                                        .order_by(sort_by.get(sort,'id'))\
                                        .prefetch_related(Prefetch('productimage_set', queryset = ProductImage.objects.all().order_by('id')))
            
            if limit :
                limit    = offset + limit
                products = products[offset : limit]

            products_list = [{
                            'id'            : product.id,
                            'brand'         : product.brand.name,
                            'name'          : product.name,
                            'thumbnail_url' : product.productimage_set.first().image_url,
                            'product_price' : product.buy_price,
                            'release_price' : product.release_price
                        } for product in products]
            return JsonResponse({'products_list' : products_list}, status = 200)

        except TypeError as e :
            return JsonResponse({'message' : f'{e}'}, status=400)
        except AttributeError as e :
            return JsonResponse({'message' : f'{e}'}, status=400)

class BrandView(View):
    def get(self, request):
            brands = Brand.objects.all()

            brand_list = [{
                        'brand_id'   : brand.id,
                        'brand_name' : brand.name,
                    } for brand in brands]
            return JsonResponse({'brand_list' : brand_list}, status = 200)

class DetailProductView(View) :
    def get(self, request, product_id) :
        try :    
            buy_price_filter  = (Q(productsize__bidding__bidding_position_id = 2) & Q(productsize__bidding__bidding_status_id = 1))
            sell_price_filter = (Q(productsize__bidding__bidding_position_id = 1) & Q(productsize__bidding__bidding_status_id = 1))

            if not Product.objects.filter(id = product_id).exists():
                return JsonResponse({'MESSAGE':'product_id_not_exist'}, status = 404)
            
            product  = Product.objects\
                                    .annotate(buy_price = Min('productsize__bidding__price', filter = buy_price_filter), 
                                            sell_price = Max('productsize__bidding__price', filter = sell_price_filter))\
                                    .get(id = product_id)
                                                    
            orders   = Order.objects.\
                                    filter(bidding__product_size__product_id = product_id).\
                                    order_by('-created_at')
            wishlist = len(Wishlist.objects.filter(id=product_id).all())
            
            product_detail = [{
                                'product_id'      : product.id,
                                'name'            : product.name,
                                'brand_name'      : product.brand.name,
                                'release_price'   : product.release_price,
                                'model_number'    : product.model_number,
                                'image_list'      : [image.image_url for image in product.productimage_set.all()],
                                'recent_price'    : orders.first().bidding.price if orders.exists() else None,
                                'buy_price'       : product.buy_price,
                                'sell_price'      : product.sell_price,
                                'total_wishlist'  : wishlist,
                            }]
            return JsonResponse({'product_detail' : product_detail}, status=200)

        except AttributeError as e :
            return JsonResponse({'message' : f'{e}'}, status=400)        
        except TypeError as e :
            return JsonResponse({'message' : f'{e}'}, status=400)

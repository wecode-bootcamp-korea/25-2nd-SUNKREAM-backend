import json
from json.decoder import JSONDecodeError

from django.http import JsonResponse
from django.views import View

from products.models import Product, Wishlist
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
                'image' : 
                [
                    {
                        'thumbnail' : img.image_url
                    } for img in wish.product.productimage_set.all()[:1]]
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
